import hashlib
import io
import json
import uuid
from datetime import UTC, datetime

import pytest

from aicefr.api.review import ReviewApi
from aicefr.api.student import (
    AllowlistedTaskAccess,
    StudentApi,
    StudentResponseStatus,
    StudentService,
    StudentStatus,
    SubmissionError,
    SubmitRequest,
    UploadPolicy,
)
from aicefr.api.templates import render_student_status, render_upload_form
from aicefr.api.wsgi import StudentTeacherApp
from aicefr.auth.memory import MemoryIdentityRepository
from aicefr.auth.service import (
    AuthorizationError,
    AuthService,
    ConsentService,
    ResourceNotFound,
    authorize_owner,
)
from aicefr.contracts import (
    Actor,
    ActorRole,
    Assessment,
    AssessmentStatus,
    Band,
    BlobRef,
    Criterion,
    CriterionCoverage,
    Interaction,
    Provenance,
    ReasonCode,
    ResponseRecord,
    ResponseStatus,
    ReviewAction,
    ReviewCandidate,
)
from aicefr.report.contracts import ReportStatus
from aicefr.report.service import MemoryReportRepository, ReportInput, ReportService
from aicefr.review.routing import review_candidate_from_assessment
from aicefr.review.service import (
    MemoryReviewRepository,
    ReviewActionRequest,
    ReviewService,
)


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 9, 28, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


class MemoryResponsePort:
    """M08 response port fixture; M08 owns persistence/blob integration tests."""

    def __init__(self, consents: ConsentService, clock: Clock) -> None:
        self._consents = consents
        self._clock = clock
        self.records: dict[str, ResponseRecord] = {}
        self.blobs: dict[str, bytes] = {}

    def submit(
        self,
        actor: Actor,
        *,
        task_id: str,
        task_version: str,
        consent_version: str,
        audio_bytes: bytes,
        initial_status: ResponseStatus = ResponseStatus.QUEUED,
    ) -> ResponseRecord:
        self._consents.require_active(actor, consent_version)
        blob_id = uuid.uuid4().hex
        blob = BlobRef(
            blob_id=blob_id,
            sha256=hashlib.sha256(audio_bytes).hexdigest(),
            size_bytes=len(audio_bytes),
        )
        record = ResponseRecord(
            response_id=uuid.uuid4().hex,
            owner_id=actor.actor_id,
            task_id=task_id,
            task_version=task_version,
            blob=blob,
            status=initial_status,
            created_at=self._clock(),
        )
        self.records[record.response_id] = record
        self.blobs[blob_id] = audio_bytes
        return record

    def get_response(self, actor: Actor, response_id: str) -> ResponseRecord:
        record = self.records.get(response_id)
        authorize_owner(actor, record.owner_id if record is not None else None)
        assert record is not None
        return record

    def transition_status(
        self,
        *,
        response_id: str,
        expected_revision: int,
        status: ResponseStatus,
        actor_id: str,
        action: str,
        reason: ReasonCode | None = None,
    ) -> ResponseRecord:
        del actor_id, action
        record = self.records[response_id]
        if record.revision != expected_revision:
            raise RuntimeError("response revision is stale")
        updated = record.model_copy(
            update={
                "status": status,
                "status_reason": reason,
                "revision": record.revision + 1,
            }
        )
        self.records[response_id] = updated
        return updated


def _request(**changes) -> SubmitRequest:
    values = {
        "task_id": "fixture-task",
        "task_version": "v1",
        "consent_version": "consent-v1",
        "filename": "fixture.wav",
        "content_type": "audio/wav",
        "audio_bytes": b"synthetic fixture audio",
    }
    values.update(changes)
    return SubmitRequest(**values)


def _setup_api():
    clock = Clock()
    identities = MemoryIdentityRepository()
    auth = AuthService(identities, identities, clock=clock)
    student = auth.bootstrap_fixture_account("fixture-student", ActorRole.STUDENT, "password")
    other = auth.bootstrap_fixture_account("fixture-other", ActorRole.STUDENT, "password")
    teacher = auth.bootstrap_fixture_account("fixture-teacher", ActorRole.TEACHER, "password")
    consent = ConsentService(identities, clock=clock)
    consent.activate(student, "consent-v1")
    responses = MemoryResponsePort(consent, clock)
    reports = MemoryReportRepository()
    service = StudentService(
        auth,
        responses,
        reports,
        UploadPolicy(allowed_media_types=frozenset({"audio/wav"}), max_bytes=64),
        AllowlistedTaskAccess(frozenset({("fixture-task", "v1")})),
    )
    return auth, student, other, teacher, responses, reports, StudentApi(service)


def _multipart_request() -> tuple[str, bytes]:
    boundary = "fixture-boundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="task_id"\r\n\r\n'
        "fixture-task\r\n"
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="task_version"\r\n\r\n'
        "v1\r\n"
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="consent_version"\r\n\r\n'
        "consent-v1\r\n"
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="audio"; filename="fixture.wav"\r\n'
        "Content-Type: audio/wav\r\n\r\n"
    ).encode() + b"fixture-audio" + f"\r\n--{boundary}--\r\n".encode()
    return f"multipart/form-data; boundary={boundary}", body


def _call_app(
    app,
    method: str,
    path: str,
    *,
    body: bytes = b"",
    content_type: str = "",
    token: str | None = None,
    cookie: bool = False,
    include_origin: bool = True,
):
    captured: dict[str, object] = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(body)),
        "CONTENT_TYPE": content_type,
        "wsgi.input": io.BytesIO(body),
        "wsgi.url_scheme": "http",
        "HTTP_HOST": "testserver",
    }
    if token:
        if cookie:
            environ["HTTP_COOKIE"] = f"aicefr_session={token}"
            if method == "POST" and include_origin:
                environ["HTTP_ORIGIN"] = "http://testserver"
        else:
            environ["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    result = b"".join(app(environ, start_response))
    return captured["status"], captured["headers"], result


def test_m01_test_001_student_with_active_consent_creates_queued_response():
    auth, student, _, _, responses, _, api = _setup_api()
    token = auth.login(student.actor_id, "password")

    status = api.submit(token, _request())

    assert status.status is StudentResponseStatus.QUEUED
    record = responses.records[status.response_id]
    assert record.owner_id == student.actor_id
    assert record.status is StudentResponseStatus.QUEUED


def test_m01_test_002_role_or_consent_denial_creates_no_response_or_blob():
    auth, student, _, teacher, responses, _, api = _setup_api()
    teacher_token = auth.login(teacher.actor_id, "password")
    with pytest.raises(AuthorizationError):
        api.submit(teacher_token, _request())

    student_token = auth.login(student.actor_id, "password")
    with pytest.raises(AuthorizationError):
        api.submit(student_token, _request(consent_version="other-consent"))

    assert responses.records == {}
    assert responses.blobs == {}


@pytest.mark.parametrize(
    ("submit_request", "reason"),
    [
        (_request(audio_bytes=b""), "EMPTY_AUDIO"),
        (_request(content_type="text/plain"), "UNSUPPORTED_AUDIO_FORMAT"),
        (_request(audio_bytes=b"x" * 65), "AUDIO_TOO_LARGE"),
    ],
)
def test_m01_test_005_invalid_upload_is_rejected_before_storage(submit_request, reason):
    auth, student, _, _, responses, _, api = _setup_api()
    token = auth.login(student.actor_id, "password")

    with pytest.raises(SubmissionError) as error:
        api.submit(token, submit_request)

    assert error.value.code == reason
    assert responses.records == {}
    assert responses.blobs == {}


def test_m01_closed_task_is_rejected_before_storage():
    auth, student, _, _, responses, _, api = _setup_api()
    token = auth.login(student.actor_id, "password")

    with pytest.raises(SubmissionError) as error:
        api.submit(token, _request(task_id="closed-task"))

    assert error.value.code is ReasonCode.TASK_NOT_OPEN
    assert responses.records == {}
    assert responses.blobs == {}


def test_m01_test_003_foreign_owner_cannot_observe_status_or_report():
    auth, student, other, _, _, _, api = _setup_api()
    student_token = auth.login(student.actor_id, "password")
    response_id = api.submit(student_token, _request()).response_id
    other_token = auth.login(other.actor_id, "password")

    with pytest.raises(ResourceNotFound) as status_denied:
        api.get_status(other_token, response_id)
    with pytest.raises(ResourceNotFound) as report_denied:
        api.get_report(other_token, response_id)

    assert str(status_denied.value) == str(report_denied.value)


def test_m01_test_004_status_is_preserved_and_report_is_never_invented():
    auth, student, _, _, responses, _, api = _setup_api()
    token = auth.login(student.actor_id, "password")
    submitted = api.submit(token, _request())
    review = responses.transition_status(
        response_id=submitted.response_id,
        expected_revision=submitted.revision,
        status=StudentResponseStatus.REVIEW_REQUIRED,
        actor_id="system-pipeline",
        action="pipeline_review_required",
    )
    current = api.get_status(token, submitted.response_id)
    assert current.status is StudentResponseStatus.REVIEW_REQUIRED
    failed = responses.transition_status(
        response_id=review.response_id,
        expected_revision=review.revision,
        status=StudentResponseStatus.FAILED,
        actor_id="system-pipeline",
        action="pipeline_failed",
        reason=ReasonCode.ASR_FAILED,
    )

    report_view = api.get_report(token, failed.response_id)

    assert report_view.status.status is StudentResponseStatus.FAILED
    assert report_view.report is None
    assert report_view.status.report_available is False


def test_m01_completed_is_not_exposed_until_a_report_exists():
    auth, student, _, _, responses, _, api = _setup_api()
    token = auth.login(student.actor_id, "password")
    submitted = api.submit(token, _request())
    responses.transition_status(
        response_id=submitted.response_id,
        expected_revision=submitted.revision,
        status=ResponseStatus.COMPLETED,
        actor_id="system-pipeline",
        action="pipeline_completed",
    )

    visible = api.get_status(token, submitted.response_id)

    assert visible.status is ResponseStatus.RUNNING
    assert visible.reason is ReasonCode.REPORT_NOT_AVAILABLE


def test_m01_task_003_renders_keyboard_labelled_upload_and_safe_status_page():
    upload = render_upload_form("File không hợp lệ")
    status = render_student_status(
        StudentStatus(
            response_id="fixture<&>",
            status=StudentResponseStatus.QUEUED,
            revision=1,
            report_available=False,
        )
    )

    assert 'label for="audio"' in upload
    assert 'role="alert"' in upload
    assert "File không hợp lệ" in upload
    assert "fixture&lt;&amp;&gt;" in status


def test_m01_task_003_wsgi_upload_status_and_owner_boundary_use_real_routes():
    auth, student, other, _, responses, _, api = _setup_api()
    app = StudentTeacherApp(api, max_request_bytes=4_096)
    content_type, body = _multipart_request()

    page_status, _, page = _call_app(app, "GET", "/student/upload")
    status, _, payload = _call_app(
        app,
        "POST",
        "/api/student/responses",
        body=body,
        content_type=content_type,
        token=auth.login(student.actor_id, "password"),
    )
    submitted = json.loads(payload)
    response_id = submitted["response_id"]
    owner_page_status, _, owner_page = _call_app(
        app,
        "GET",
        f"/student/responses/{response_id}",
        token=auth.login(student.actor_id, "password"),
        cookie=True,
    )
    other_status, _, other_payload = _call_app(
        app,
        "GET",
        f"/api/student/responses/{response_id}/status",
        token=auth.login(other.actor_id, "password"),
    )
    missing_status, _, missing_payload = _call_app(
        app,
        "GET",
        f"/api/student/responses/{'0' * 32}/status",
        token=auth.login(other.actor_id, "password"),
    )

    assert page_status.startswith("200") and b'enctype="multipart/form-data"' in page
    assert status.startswith("201") and submitted["status"] == "QUEUED"
    assert response_id in responses.records
    assert owner_page_status.startswith("200")
    assert b"Tr\xe1\xba\xa1ng th\xc3\xa1i b\xc3\xa0i n\xe1\xbb\x99p" in owner_page
    assert other_status.startswith("404") and missing_status.startswith("404")
    assert other_payload == missing_payload
    assert b"fixture-audio" not in owner_page


def test_m01_wsgi_cookie_mutation_requires_same_origin_before_upload_is_read():
    auth, student, _, _, responses, _, api = _setup_api()
    app = StudentTeacherApp(api, max_request_bytes=4_096)
    content_type, body = _multipart_request()

    status, _, payload = _call_app(
        app,
        "POST",
        "/api/student/responses",
        body=body,
        content_type=content_type,
        token=auth.login(student.actor_id, "password"),
        cookie=True,
        include_origin=False,
    )

    assert status.startswith("403")
    assert json.loads(payload) == {"error": "CSRF_ORIGIN_REQUIRED"}
    assert responses.records == {}


def test_m07_wsgi_teacher_form_is_role_gated_and_writes_audited_decision():
    auth, student, _, teacher, _, _, api = _setup_api()
    repository = MemoryReviewRepository()
    review_service = ReviewService(repository, clock=Clock())
    candidate = review_service.add_candidate(
        ReviewCandidate(
            response_id="e" * 32,
            response_revision=1,
            assessment_status=AssessmentStatus.REVIEW_REQUIRED,
            proposed_band=Band.B1,
            reasons=(ReasonCode.SCORE_NEAR_BOUNDARY,),
            source_versions={"model": "fixture-v1"},
            created_at=Clock()(),
            updated_at=Clock()(),
        )
    )
    app = StudentTeacherApp(api, review_api=ReviewApi(auth, review_service))
    body = b"action=OVERRIDE&expected_revision=1&final_band=B2&reason=fixture+review"

    denied, _, _ = _call_app(
        app,
        "GET",
        "/api/teacher/reviews",
        token=auth.login(student.actor_id, "password"),
    )
    queue_status, _, queue = _call_app(
        app,
        "GET",
        "/teacher/reviews",
        token=auth.login(teacher.actor_id, "password"),
        cookie=True,
    )
    decision_status, headers, _ = _call_app(
        app,
        "POST",
        f"/teacher/reviews/{candidate.response_id}/decision",
        body=body,
        content_type="application/x-www-form-urlencoded",
        token=auth.login(teacher.actor_id, "password"),
        cookie=True,
    )

    assert denied.startswith("403")
    assert queue_status.startswith("200")
    assert b"L\xc6\xb0u quy\xe1\xba\xbft \xc4\x91\xe1\xbb\x8bnh" in queue
    assert decision_status.startswith("303") and headers["Location"] == "/teacher/reviews"
    assert repository.get(candidate.response_id).state.value == "OVERRIDDEN"
    assert repository.list_audit()[0].actor_id == teacher.actor_id


def test_w3_fixture_flow_submits_then_exposes_teacher_verified_report():
    """Fixture-only integration: M01 submission -> M06 report -> M07 action."""
    auth, student, _, teacher, responses, reports, student_api = _setup_api()
    student_token = auth.login(student.actor_id, "password")
    submitted = student_api.submit(student_token, _request())
    assessment = Assessment(
        response_id=submitted.response_id,
        status=AssessmentStatus.REVIEW_REQUIRED,
        overall_score=3.4,
        overall_band=Band.B1,
        criteria=tuple(
            CriterionCoverage(criterion=criterion, coverage=1.0, features=("fixture",))
            for criterion in Criterion
        ),
        interaction=Interaction(),
        reasons=(ReasonCode.SCORE_NEAR_BOUNDARY,),
        provenance=Provenance(
            model_version="fixture-model-v1",
            model_sha256="0" * 64,
            feature_version="fixture-features-v1",
            band_map_version="fixture-bands-v1",
            calibration_version=None,
            unit_of_inference="fixture response",
            scored_at="2026-09-28T00:00:00+00:00",
        ),
    )
    routed = responses.transition_status(
        response_id=submitted.response_id,
        expected_revision=submitted.revision,
        status=ResponseStatus.REVIEW_REQUIRED,
        actor_id="fixture-pipeline",
        action="assessment_review_required",
        reason=ReasonCode.SCORE_NEAR_BOUNDARY,
    )
    review_repository = MemoryReviewRepository()
    report_service = ReportService(reports, decision_verifier=review_repository)
    provisional = report_service.build_and_store(
        ReportInput(
            response_id=submitted.response_id,
            audio_duration_s=1.0,
            assessment=assessment,
        )
    )
    review_service = ReviewService(
        review_repository,
        clock=Clock(),
        report_sink=report_service,
    )
    candidate = review_service.add_candidate(
        review_candidate_from_assessment(
            assessment,
            response_revision=routed.revision,
            clock=Clock(),
        )
    )

    outcome = ReviewApi(auth, review_service).decide(
        auth.login(teacher.actor_id, "password"),
        submitted.response_id,
        ReviewActionRequest(
            action=ReviewAction.OVERRIDE,
            expected_revision=candidate.revision,
            final_band=Band.B2,
            reason="Teacher verified synthetic fixture evidence",
        ),
    )
    report_view = student_api.get_report(student_token, submitted.response_id)

    assert provisional.status is ReportStatus.PROVISIONAL
    assert outcome.decision.audit_id == outcome.audit.event_id
    assert report_view.status.status is ResponseStatus.REVIEW_REQUIRED
    assert report_view.report is not None
    assert report_view.report.status is ReportStatus.TEACHER_VERIFIED
    assert report_view.report.teacher_verified is True
    assert report_view.report.teacher_final is not None
    assert report_view.report.teacher_final.overall_band is Band.B2
