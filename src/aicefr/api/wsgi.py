"""Dependency-injected WSGI surface for student upload and teacher review.

The local application exposes fixture-account login through M08. API clients
may also supply an existing M08 session as a Bearer token.
"""

from __future__ import annotations

import ipaddress
import json
from collections.abc import Callable
from dataclasses import dataclass
from email.parser import BytesParser
from email.policy import default
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qs, urlsplit

from pydantic import ValidationError

from aicefr.api.review import ReviewApi
from aicefr.api.student import StudentApi, SubmissionError, SubmitRequest
from aicefr.api.templates import (
    LOCAL_CSS,
    render_consent,
    render_login,
    render_notice,
    render_report,
    render_review_detail,
    render_review_queue,
    render_student_status,
    render_upload_form,
)
from aicefr.auth.service import AuthorizationError, AuthService, ConsentService, ResourceNotFound
from aicefr.contracts import ActorRole, ConsentState
from aicefr.report.contracts import DiagnosticReport
from aicefr.report.service import ReportNotFound, UnverifiedReviewDecision
from aicefr.review.service import (
    InvalidReviewTransition,
    ReviewActionRequest,
    ReviewNotFound,
    StaleReview,
)
from aicefr.storage.service import ResponseService

StartResponse = Callable[[str, list[tuple[str, str]]], Any]


class HttpInputError(ValueError):
    def __init__(self, status: HTTPStatus, code: str) -> None:
        super().__init__(code)
        self.status = status
        self.code = code


@dataclass(frozen=True)
class WebResponse:
    status: HTTPStatus
    content_type: str
    body: bytes
    headers: tuple[tuple[str, str], ...] = ()


class StudentTeacherApp:
    """HTTP/UI adapter with explicit, bounded request parsing.

    This is intentionally framework-free so the assessed service contracts can
    be checked without a web-server dependency.  Production hosting still
    chooses TLS, session issuance and deployment through the M08 owner.
    """

    _SECURITY_HEADERS = (
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
        ("Content-Security-Policy", "default-src 'self'; base-uri 'none'; frame-ancestors 'none'"),
    )

    def __init__(
        self,
        student_api: StudentApi,
        *,
        review_api: ReviewApi | None = None,
        auth: AuthService | None = None,
        consents: ConsentService | None = None,
        responses: ResponseService | None = None,
        reviews: Any | None = None,
        reports: Any | None = None,
        consent_version: str = "local-v1",
        demo: bool = False,
        max_request_bytes: int = 10 * 1024 * 1024,
    ) -> None:
        if max_request_bytes <= 0:
            raise ValueError("max_request_bytes must be positive")
        self._student_api = student_api
        self._review_api = review_api
        self._auth = auth
        self._consents = consents
        self._responses = responses
        self._reviews = reviews
        self._reports = reports
        self._consent_version = consent_version
        self._demo = demo
        self._max_request_bytes = max_request_bytes

    def __call__(self, environ: dict[str, Any], start_response: StartResponse) -> list[bytes]:
        try:
            response = self._dispatch(environ)
        except HttpInputError as error:
            response = self._controlled_error(environ, error.status, error.code)
        except SubmissionError as error:
            response = self._controlled_error(
                environ, HTTPStatus.UNPROCESSABLE_ENTITY, error.code.value
            )
        except ResourceNotFound:
            response = self._controlled_error(environ, HTTPStatus.NOT_FOUND, "RESOURCE_UNAVAILABLE")
        except AuthorizationError:
            response = self._controlled_error(environ, HTTPStatus.FORBIDDEN, "ACCESS_DENIED")
        except ReviewNotFound:
            response = self._controlled_error(environ, HTTPStatus.NOT_FOUND, "REVIEW_UNAVAILABLE")
        except (StaleReview, InvalidReviewTransition):
            response = self._controlled_error(environ, HTTPStatus.CONFLICT, "STALE_OR_FINAL_REVIEW")
        except (ReportNotFound, UnverifiedReviewDecision):
            response = self._controlled_error(environ, HTTPStatus.CONFLICT, "REPORT_NOT_READY")
        except ValidationError:
            response = self._controlled_error(environ, HTTPStatus.BAD_REQUEST, "INVALID_REQUEST")
        except Exception:
            # Do not leak internal paths, database details, or submitted content.
            response = self._controlled_error(
                environ, HTTPStatus.INTERNAL_SERVER_ERROR, "REQUEST_FAILED"
            )
        headers = [
            ("Content-Type", response.content_type),
            ("Content-Length", str(len(response.body))),
            *self._SECURITY_HEADERS,
            *response.headers,
        ]
        start_response(f"{response.status.value} {response.status.phrase}", headers)
        return [response.body]

    @classmethod
    def _controlled_error(
        cls, environ: dict[str, Any], status: HTTPStatus, code: str
    ) -> WebResponse:
        path = str(environ.get("PATH_INFO", ""))
        if path.startswith("/api/"):
            return cls._json(status, {"error": code})
        messages = {
            "SESSION_REQUIRED": "Vui lòng đăng nhập để tiếp tục.",
            "ACCESS_DENIED": "Tài khoản không được phép thực hiện thao tác này.",
            "CSRF_ORIGIN_REQUIRED": "Yêu cầu không hợp lệ. Hãy tải lại trang và thử lại.",
            "RESOURCE_UNAVAILABLE": "Không tìm thấy nội dung hoặc bạn không có quyền truy cập.",
            "REQUEST_TOO_LARGE": "Tệp gửi lên vượt giới hạn.",
            "UNSUPPORTED_REQUEST_FORMAT": "Định dạng yêu cầu không được hỗ trợ.",
            "REQUEST_FAILED": "Không thể xử lý yêu cầu. Vui lòng thử lại.",
            "CONSENT_VERSION_STALE": (
                "Nội dung đồng ý đã thay đổi. Hãy đọc và xác nhận phiên bản hiện tại."
            ),
        }
        return cls._html(
            status,
            render_notice(
                "Không thể xử lý yêu cầu", messages.get(code, "Thông tin gửi lên không hợp lệ.")
            ),
        )

    def _dispatch(self, environ: dict[str, Any]) -> WebResponse:
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        path = str(environ.get("PATH_INFO", "/"))
        if path == "/" and method == "GET":
            return WebResponse(
                HTTPStatus.SEE_OTHER, "text/plain; charset=utf-8", b"", (("Location", "/login"),)
            )
        if path == "/login":
            if method == "GET":
                return self._html(HTTPStatus.OK, render_login(demo=self._demo))
            if method == "POST":
                return self._login(environ)
        if path == "/local.css" and method == "GET":
            return WebResponse(
                HTTPStatus.OK,
                "text/css; charset=utf-8",
                LOCAL_CSS.encode("utf-8"),
                (("Cache-Control", "public, max-age=300"),),
            )
        if path == "/logout" and method == "POST":
            self._require_origin(environ)
            token = self._session_token(environ, unsafe=True)
            if self._auth is None:
                raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")
            self._auth.logout(token)
            return WebResponse(
                HTTPStatus.SEE_OTHER,
                "text/plain; charset=utf-8",
                b"",
                (
                    ("Location", "/login"),
                    ("Set-Cookie", "aicefr_session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"),
                ),
            )
        if path == "/student/consent" and method == "GET":
            actor = self._resolve_cookie_actor(environ, ActorRole.STUDENT)
            record = self._consents.current(actor) if self._consents else None
            active = bool(
                record
                and record.state is ConsentState.ACTIVE
                and record.consent_version == self._consent_version
            )
            return self._html(
                HTTPStatus.OK, render_consent(self._consent_version, active, self._demo)
            )
        if path in {"/student/consent/accept", "/student/consent/withdraw"} and method == "POST":
            token = self._session_token(environ, unsafe=True)
            actor = (
                self._auth.resolve(token, allowed_roles=frozenset({ActorRole.STUDENT}))
                if self._auth
                else None
            )
            if actor is None or self._consents is None:
                raise HttpInputError(HTTPStatus.UNAUTHORIZED, "SESSION_REQUIRED")
            if path.endswith("accept"):
                self._consents.activate(actor, self._consent_version)
            else:
                self._consents.withdraw(actor)
            return WebResponse(
                HTTPStatus.SEE_OTHER,
                "text/plain; charset=utf-8",
                b"",
                (("Location", "/student/consent"),),
            )
        if method == "GET" and path == "/student/upload":
            if self._auth is not None:
                self._resolve_cookie_actor(environ, ActorRole.STUDENT)
            return self._html(HTTPStatus.OK, render_upload_form(demo=self._demo))
        if method == "POST" and path == "/api/student/responses":
            return self._submit(environ, browser=False)
        if method == "POST" and path == "/student/responses":
            return self._submit(environ, browser=True)
        if path.startswith("/api/student/responses/"):
            return self._student_api_route(method, path, environ)
        if path.startswith("/student/responses/"):
            return self._student_page(method, path, environ)
        if self._review_api is not None:
            if method == "GET" and path == "/teacher/reviews":
                return self._teacher_queue_page(environ)
            if (
                method == "GET"
                and path.startswith("/teacher/reviews/")
                and not path.endswith("/audio")
            ):
                return self._teacher_detail(environ, path)
            if method == "GET" and path.startswith("/teacher/reviews/") and path.endswith("/audio"):
                return self._teacher_audio(environ, path)
            if method == "GET" and path == "/api/teacher/reviews":
                return self._teacher_queue_api(environ)
            if path.startswith("/api/teacher/reviews/"):
                return self._teacher_api_route(method, path, environ)
            if path.startswith("/teacher/reviews/"):
                return self._teacher_form_route(method, path, environ)
        raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")

    def _teacher_detail(self, environ: dict[str, Any], path: str) -> WebResponse:
        response_id = path.removeprefix("/teacher/reviews/")
        if (
            not response_id
            or "/" in response_id
            or self._auth is None
            or self._reviews is None
            or self._reports is None
        ):
            raise HttpInputError(HTTPStatus.NOT_FOUND, "RESOURCE_UNAVAILABLE")
        self._auth.resolve(
            self._session_token(environ), allowed_roles=frozenset({ActorRole.TEACHER})
        )
        candidate = self._reviews.get(response_id)
        if candidate is None:
            raise HttpInputError(HTTPStatus.NOT_FOUND, "RESOURCE_UNAVAILABLE")
        report = self._reports.get(response_id)
        return self._html(HTTPStatus.OK, render_review_detail(candidate, report, demo=self._demo))

    def _login(self, environ: dict[str, Any]) -> WebResponse:
        self._require_origin(environ)
        if self._auth is None:
            raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")
        values = self._request_values(environ)
        if set(values) != {"actor_id", "password"} or not all(
            isinstance(values[k], str) for k in values
        ):
            raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_REQUEST")
        try:
            token = self._auth.login(str(values["actor_id"]), str(values["password"]))
            actor = self._auth.resolve(token)
        except AuthorizationError:
            return self._html(
                HTTPStatus.UNAUTHORIZED,
                render_login("Tài khoản hoặc mật khẩu không hợp lệ.", demo=self._demo),
            )
        landing = (
            "/teacher/reviews"
            if actor.role is ActorRole.TEACHER
            else "/student/consent"
            if actor.role is ActorRole.STUDENT
            else "/login"
        )
        return WebResponse(
            HTTPStatus.SEE_OTHER,
            "text/plain; charset=utf-8",
            b"",
            (
                ("Location", landing),
                ("Set-Cookie", f"aicefr_session={token}; HttpOnly; SameSite=Lax; Path=/"),
            ),
        )

    def _resolve_cookie_actor(self, environ: dict[str, Any], role: ActorRole):
        token = self._session_token(environ)
        if self._auth is None:
            raise HttpInputError(HTTPStatus.UNAUTHORIZED, "SESSION_REQUIRED")
        return self._auth.resolve(token, allowed_roles=frozenset({role}))

    @staticmethod
    def _require_origin(environ: dict[str, Any]) -> None:
        scheme = str(environ.get("wsgi.url_scheme", "http"))
        host = str(environ.get("HTTP_HOST", ""))
        origin = str(environ.get("HTTP_ORIGIN", ""))
        try:
            host_parts = urlsplit(f"//{host}")
            origin_parts = urlsplit(origin)
            hostname = host_parts.hostname
            is_loopback = hostname == "localhost" or bool(
                hostname and ipaddress.ip_address(hostname).is_loopback
            )
            matches = (
                is_loopback
                and not host_parts.username
                and origin_parts.scheme == scheme
                and origin_parts.netloc == host
                and not origin_parts.username
                and origin_parts.path == ""
                and not origin_parts.query
                and not origin_parts.fragment
            )
        except ValueError:
            matches = False
        if not matches:
            raise HttpInputError(HTTPStatus.FORBIDDEN, "CSRF_ORIGIN_REQUIRED")

    def _teacher_audio(self, environ: dict[str, Any], path: str) -> WebResponse:
        response_id = path.removeprefix("/teacher/reviews/").removesuffix("/audio")
        if (
            not response_id
            or "/" in response_id
            or self._reviews is None
            or self._responses is None
            or self._auth is None
        ):
            raise HttpInputError(HTTPStatus.NOT_FOUND, "RESOURCE_UNAVAILABLE")
        self._auth.resolve(
            self._session_token(environ), allowed_roles=frozenset({ActorRole.TEACHER})
        )
        candidate = self._reviews.get(response_id)
        record = self._responses.metadata.get_response(response_id)
        if candidate is None or record is None:
            raise HttpInputError(HTTPStatus.NOT_FOUND, "RESOURCE_UNAVAILABLE")
        data = self._responses.blobs.read(record.blob)
        import io

        import soundfile as sf

        from aicefr.audio.decoder import _detected_format

        try:
            with sf.SoundFile(io.BytesIO(data)) as audio:
                fmt = _detected_format(audio.format, audio.subtype)
        except Exception:
            raise HttpInputError(HTTPStatus.NOT_FOUND, "RESOURCE_UNAVAILABLE") from None
        mime = {
            "wav": "audio/wav",
            "flac": "audio/flac",
            "ogg": "audio/ogg",
            "mp3": "audio/mpeg",
        }.get(str(fmt))
        if mime is None:
            raise HttpInputError(HTTPStatus.NOT_FOUND, "RESOURCE_UNAVAILABLE")
        return WebResponse(HTTPStatus.OK, mime, data, (("Content-Disposition", "inline"),))

    def _submit(self, environ: dict[str, Any], *, browser: bool) -> WebResponse:
        token = self._session_token(environ, unsafe=True)
        body = self._read_body(environ)
        request = self._multipart_submit_request(str(environ.get("CONTENT_TYPE", "")), body)
        if self._auth is not None and self._consents is not None:
            actor = self._auth.resolve(token, allowed_roles=frozenset({ActorRole.STUDENT}))
            consent = self._consents.current(actor)
            if (
                request.consent_version != self._consent_version
                or consent is None
                or consent.state is not ConsentState.ACTIVE
                or consent.consent_version != self._consent_version
            ):
                raise HttpInputError(HTTPStatus.FORBIDDEN, "CONSENT_VERSION_STALE")
        status = self._student_api.submit(token, request)
        if browser:
            return WebResponse(
                HTTPStatus.SEE_OTHER,
                "text/plain; charset=utf-8",
                b"",
                (("Location", f"/student/responses/{status.response_id}"),),
            )
        return self._json(HTTPStatus.CREATED, status.model_dump(mode="json"))

    def _student_api_route(self, method: str, path: str, environ: dict[str, Any]) -> WebResponse:
        response_id, suffix = self._student_path(path, "/api/student/responses/")
        token = self._session_token(environ)
        if method == "GET" and suffix == "/status":
            status = self._student_api.get_status(token, response_id)
            return self._json(HTTPStatus.OK, status.model_dump(mode="json"))
        if method == "GET" and suffix == "/report":
            view = self._student_api.get_report(token, response_id)
            if view.report is None:
                return self._json(
                    HTTPStatus.ACCEPTED,
                    {"status": view.status.model_dump(mode="json"), "report": None},
                )
            return self._json(HTTPStatus.OK, self._report_payload(view.report))
        raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")

    def _student_page(self, method: str, path: str, environ: dict[str, Any]) -> WebResponse:
        if method != "GET":
            raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")
        response_id, suffix = self._student_path(path, "/student/responses/")
        token = self._session_token(environ)
        if suffix == "":
            status = self._student_api.get_status(token, response_id)
            return self._html(HTTPStatus.OK, render_student_status(status, demo=self._demo))
        if suffix == "/report":
            view = self._student_api.get_report(token, response_id)
            if isinstance(view.report, DiagnosticReport):
                return self._html(HTTPStatus.OK, render_report(view.report, demo=self._demo))
            return self._html(
                HTTPStatus.ACCEPTED,
                render_student_status(view.status, demo=self._demo),
            )
        raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")

    def _teacher_queue_page(self, environ: dict[str, Any]) -> WebResponse:
        assert self._review_api is not None
        queue = self._review_api.get_queue(self._session_token(environ))
        return self._html(HTTPStatus.OK, render_review_queue(queue, demo=self._demo))

    def _teacher_queue_api(self, environ: dict[str, Any]) -> WebResponse:
        assert self._review_api is not None
        queue = self._review_api.get_queue(self._session_token(environ))
        return self._json(
            HTTPStatus.OK,
            {"items": [item.model_dump(mode="json") for item in queue]},
        )

    def _teacher_api_route(self, method: str, path: str, environ: dict[str, Any]) -> WebResponse:
        response_id, action = self._teacher_path(path, "/api/teacher/reviews/")
        if method != "POST" or action not in {"claim", "decision"}:
            raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")
        outcome = self._teacher_action(environ, response_id, action)
        payload = (
            outcome.model_dump(mode="json")
            if hasattr(outcome, "model_dump")
            else {
                "candidate": outcome.candidate.model_dump(mode="json"),
                "decision": outcome.decision.model_dump(mode="json"),
                "audit": outcome.audit.model_dump(mode="json"),
            }
        )
        return self._json(HTTPStatus.OK, payload)

    def _teacher_form_route(self, method: str, path: str, environ: dict[str, Any]) -> WebResponse:
        response_id, action = self._teacher_path(path, "/teacher/reviews/")
        if method != "POST" or action not in {"claim", "decision"}:
            raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")
        self._teacher_action(environ, response_id, action)
        return WebResponse(
            status=HTTPStatus.SEE_OTHER,
            content_type="text/plain; charset=utf-8",
            body=b"",
            headers=(("Location", "/teacher/reviews"),),
        )

    def _teacher_action(self, environ: dict[str, Any], response_id: str, action: str):
        assert self._review_api is not None
        token = self._session_token(environ, unsafe=True)
        values = self._request_values(environ)
        if action == "claim":
            try:
                expected_revision = int(values["expected_revision"])
            except (KeyError, TypeError, ValueError) as error:
                raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_REQUEST") from error
            return self._review_api.claim(token, response_id, expected_revision)
        request = ReviewActionRequest(**self._decision_values(values))
        return self._review_api.decide(token, response_id, request)

    def _request_values(self, environ: dict[str, Any]) -> dict[str, object]:
        body = self._read_body(environ)
        content_type = str(environ.get("CONTENT_TYPE", "")).lower()
        if content_type.startswith("application/json"):
            try:
                values = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_REQUEST") from error
            if not isinstance(values, dict):
                raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_REQUEST")
            return values
        if content_type.startswith("application/x-www-form-urlencoded"):
            try:
                parsed = parse_qs(body.decode("utf-8"), strict_parsing=True)
            except (UnicodeDecodeError, ValueError) as error:
                raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_REQUEST") from error
            if any(len(value) != 1 for value in parsed.values()):
                raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_REQUEST")
            return {key: value[0] for key, value in parsed.items()}
        raise HttpInputError(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "UNSUPPORTED_REQUEST_FORMAT")

    @staticmethod
    def _decision_values(values: dict[str, object]) -> dict[str, object]:
        allowed = {"action", "expected_revision", "final_band", "reason"}
        if set(values) - allowed:
            raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_REQUEST")
        normalised = dict(values)
        for field in ("final_band", "reason"):
            if normalised.get(field) == "":
                normalised[field] = None
        return normalised

    def _read_body(self, environ: dict[str, Any]) -> bytes:
        content_length = environ.get("CONTENT_LENGTH", "")
        try:
            length = int(content_length) if content_length else None
        except ValueError as error:
            raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_CONTENT_LENGTH") from error
        if length is not None and (length < 0 or length > self._max_request_bytes):
            raise HttpInputError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "REQUEST_TOO_LARGE")
        raw = environ.get("wsgi.input")
        if raw is None:
            raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_REQUEST")
        body = raw.read(self._max_request_bytes + 1 if length is None else length)
        if len(body) > self._max_request_bytes or (length is not None and len(body) != length):
            raise HttpInputError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "REQUEST_TOO_LARGE")
        return body

    @staticmethod
    def _multipart_submit_request(content_type: str, body: bytes) -> SubmitRequest:
        if not content_type.lower().startswith("multipart/form-data"):
            raise HttpInputError(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "UNSUPPORTED_REQUEST_FORMAT")
        try:
            message = BytesParser(policy=default).parsebytes(
                f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
            )
        except (UnicodeEncodeError, ValueError) as error:
            raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_MULTIPART") from error
        if not message.is_multipart():
            raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_MULTIPART")
        fields: dict[str, str] = {}
        audio: tuple[str, str, bytes] | None = None
        for part in message.iter_parts():
            if part.get_content_disposition() != "form-data":
                raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_MULTIPART")
            name = part.get_param("name", header="content-disposition")
            payload = part.get_payload(decode=True) or b""
            if name == "audio":
                if audio is not None or part.get_filename() is None:
                    raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_MULTIPART")
                audio = (part.get_filename(), part.get_content_type(), payload)
            elif name in {"task_id", "task_version", "consent_version"}:
                if name in fields:
                    raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_MULTIPART")
                try:
                    fields[name] = payload.decode("utf-8")
                except UnicodeDecodeError as error:
                    raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_MULTIPART") from error
            else:
                raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_MULTIPART")
        if audio is None or set(fields) != {"task_id", "task_version", "consent_version"}:
            raise HttpInputError(HTTPStatus.BAD_REQUEST, "INVALID_MULTIPART")
        return SubmitRequest(
            **fields,
            filename=audio[0],
            content_type=audio[1],
            audio_bytes=audio[2],
        )

    def _session_token(self, environ: dict[str, Any], *, unsafe: bool = False) -> str:
        authorization = str(environ.get("HTTP_AUTHORIZATION", ""))
        if authorization.startswith("Bearer ") and authorization[7:]:
            return authorization[7:]
        cookies = str(environ.get("HTTP_COOKIE", ""))
        for value in cookies.split(";"):
            name, separator, token = value.strip().partition("=")
            if name == "aicefr_session" and separator and token:
                if unsafe:
                    if self._auth is not None and self._consents is not None:
                        self._require_origin(environ)
                    else:
                        scheme = str(environ.get("wsgi.url_scheme", "http"))
                        host = str(environ.get("HTTP_HOST", ""))
                        origin = str(environ.get("HTTP_ORIGIN", ""))
                        if not host or origin != f"{scheme}://{host}":
                            raise HttpInputError(HTTPStatus.FORBIDDEN, "CSRF_ORIGIN_REQUIRED")
                return token
        raise HttpInputError(HTTPStatus.UNAUTHORIZED, "SESSION_REQUIRED")

    @staticmethod
    def _student_path(path: str, prefix: str) -> tuple[str, str]:
        remainder = path.removeprefix(prefix)
        response_id, separator, suffix = remainder.partition("/")
        if not response_id:
            raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")
        return response_id, f"/{suffix}" if separator else ""

    @staticmethod
    def _teacher_path(path: str, prefix: str) -> tuple[str, str]:
        response_id, separator, action = path.removeprefix(prefix).partition("/")
        if not response_id or not separator or "/" in action:
            raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")
        return response_id, action

    @staticmethod
    def _report_payload(report: object) -> dict[str, object]:
        if not isinstance(report, DiagnosticReport):
            raise HttpInputError(HTTPStatus.NOT_FOUND, "REPORT_UNAVAILABLE")
        return report.model_dump(mode="json")

    @classmethod
    def _html(cls, status: HTTPStatus, page: str) -> WebResponse:
        return WebResponse(status, "text/html; charset=utf-8", page.encode("utf-8"))

    @classmethod
    def _json(cls, status: HTTPStatus, payload: object) -> WebResponse:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return WebResponse(status, "application/json; charset=utf-8", body)
