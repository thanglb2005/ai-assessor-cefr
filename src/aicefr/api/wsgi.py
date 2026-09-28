"""Small dependency-injected WSGI surface for the M01 and M07 vertical slice.

The application deliberately has no public signup/login route: M08 owns
identity and sessions.  A trusted host supplies the existing M08 session as a
Bearer token or the ``aicefr_session`` cookie.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from email.parser import BytesParser
from email.policy import default
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qs

from pydantic import ValidationError

from aicefr.api.review import ReviewApi
from aicefr.api.student import StudentApi, SubmissionError, SubmitRequest
from aicefr.api.templates import (
    render_report,
    render_review_queue,
    render_student_status,
    render_upload_form,
)
from aicefr.auth.service import AuthorizationError, ResourceNotFound
from aicefr.report.contracts import DiagnosticReport
from aicefr.report.service import ReportNotFound, UnverifiedReviewDecision
from aicefr.review.service import (
    InvalidReviewTransition,
    ReviewActionRequest,
    ReviewNotFound,
    StaleReview,
)

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
        max_request_bytes: int = 10 * 1024 * 1024,
    ) -> None:
        if max_request_bytes <= 0:
            raise ValueError("max_request_bytes must be positive")
        self._student_api = student_api
        self._review_api = review_api
        self._max_request_bytes = max_request_bytes

    def __call__(self, environ: dict[str, Any], start_response: StartResponse) -> list[bytes]:
        try:
            response = self._dispatch(environ)
        except HttpInputError as error:
            response = self._json(error.status, {"error": error.code})
        except SubmissionError as error:
            response = self._json(HTTPStatus.UNPROCESSABLE_ENTITY, {"error": error.code.value})
        except ResourceNotFound:
            response = self._json(HTTPStatus.NOT_FOUND, {"error": "RESOURCE_UNAVAILABLE"})
        except AuthorizationError:
            response = self._json(HTTPStatus.FORBIDDEN, {"error": "ACCESS_DENIED"})
        except ReviewNotFound:
            response = self._json(HTTPStatus.NOT_FOUND, {"error": "REVIEW_UNAVAILABLE"})
        except (StaleReview, InvalidReviewTransition):
            response = self._json(HTTPStatus.CONFLICT, {"error": "STALE_OR_FINAL_REVIEW"})
        except (ReportNotFound, UnverifiedReviewDecision):
            response = self._json(HTTPStatus.CONFLICT, {"error": "REPORT_NOT_READY"})
        except ValidationError:
            response = self._json(HTTPStatus.BAD_REQUEST, {"error": "INVALID_REQUEST"})
        headers = [
            ("Content-Type", response.content_type),
            ("Content-Length", str(len(response.body))),
            *self._SECURITY_HEADERS,
            *response.headers,
        ]
        start_response(f"{response.status.value} {response.status.phrase}", headers)
        return [response.body]

    def _dispatch(self, environ: dict[str, Any]) -> WebResponse:
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        path = str(environ.get("PATH_INFO", "/"))
        if method == "GET" and path == "/student/upload":
            return self._html(HTTPStatus.OK, render_upload_form())
        if method == "POST" and path == "/api/student/responses":
            return self._submit(environ)
        if path.startswith("/api/student/responses/"):
            return self._student_api_route(method, path, environ)
        if path.startswith("/student/responses/"):
            return self._student_page(method, path, environ)
        if self._review_api is not None:
            if method == "GET" and path == "/teacher/reviews":
                return self._teacher_queue_page(environ)
            if method == "GET" and path == "/api/teacher/reviews":
                return self._teacher_queue_api(environ)
            if path.startswith("/api/teacher/reviews/"):
                return self._teacher_api_route(method, path, environ)
            if path.startswith("/teacher/reviews/"):
                return self._teacher_form_route(method, path, environ)
        raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")

    def _submit(self, environ: dict[str, Any]) -> WebResponse:
        token = self._session_token(environ, unsafe=True)
        body = self._read_body(environ)
        request = self._multipart_submit_request(str(environ.get("CONTENT_TYPE", "")), body)
        status = self._student_api.submit(token, request)
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
            return self._html(HTTPStatus.OK, render_student_status(status))
        if suffix == "/report":
            view = self._student_api.get_report(token, response_id)
            if isinstance(view.report, DiagnosticReport):
                return self._html(HTTPStatus.OK, render_report(view.report))
            return self._html(HTTPStatus.ACCEPTED, render_student_status(view.status))
        raise HttpInputError(HTTPStatus.NOT_FOUND, "ROUTE_NOT_FOUND")

    def _teacher_queue_page(self, environ: dict[str, Any]) -> WebResponse:
        assert self._review_api is not None
        queue = self._review_api.get_queue(self._session_token(environ))
        return self._html(HTTPStatus.OK, render_review_queue(queue))

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
        payload = outcome.model_dump(mode="json") if hasattr(outcome, "model_dump") else {
            "candidate": outcome.candidate.model_dump(mode="json"),
            "decision": outcome.decision.model_dump(mode="json"),
            "audit": outcome.audit.model_dump(mode="json"),
        }
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

    @staticmethod
    def _session_token(environ: dict[str, Any], *, unsafe: bool = False) -> str:
        authorization = str(environ.get("HTTP_AUTHORIZATION", ""))
        if authorization.startswith("Bearer ") and authorization[7:]:
            return authorization[7:]
        cookies = str(environ.get("HTTP_COOKIE", ""))
        for value in cookies.split(";"):
            name, separator, token = value.strip().partition("=")
            if name == "aicefr_session" and separator and token:
                if unsafe:
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
