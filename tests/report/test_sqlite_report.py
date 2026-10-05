from datetime import UTC, datetime

from aicefr.auth.service import AccountRecord
from aicefr.contracts import (
    Actor,
    ActorRole,
    AssessmentStatus,
    AuditEvent,
    BlobRef,
    Criterion,
    CriterionCoverage,
    Interaction,
    ReasonCode,
    ResponseRecord,
    ReviewAction,
    ReviewCandidate,
    ReviewState,
)
from aicefr.report.contracts import DiagnosticReport, ReportStatus
from aicefr.report.service import ReportService
from aicefr.report.sqlite import SQLiteReportRepository
from aicefr.review.service import ReviewActionRequest, ReviewService
from aicefr.review.sqlite import SQLiteReviewRepository
from aicefr.storage.sqlite import SQLiteStore


def _report() -> DiagnosticReport:
    return DiagnosticReport(
        response_id="a" * 32, status=ReportStatus.PROVISIONAL,
        assessment_status=AssessmentStatus.NOT_EVALUATED,
        criteria=tuple(CriterionCoverage(criterion=item) for item in Criterion),
        interaction=Interaction(),
        source_versions={"assessment": "unavailable"},
    )


def test_report_survives_reopen_and_put_uses_caller_transaction(tmp_path):
    store = SQLiteStore(tmp_path)
    _add_response(store)
    repository = SQLiteReportRepository(store)
    report = _report()
    with store.transaction() as connection:
        repository.put(report)
        assert connection.in_transaction
    assert repository.get(report.response_id) == report
    store.close()

    reopened = SQLiteStore(tmp_path)
    assert SQLiteReportRepository(reopened).get(report.response_id) == report
    reopened.close()


def test_report_write_rolls_back_with_review_callback_transaction(tmp_path):
    store = SQLiteStore(tmp_path)
    _add_response(store)
    repository = SQLiteReportRepository(store)
    report = _report()
    try:
        with store.transaction():
            repository.put(report)
            raise RuntimeError("callback failed")
    except RuntimeError:
        pass
    assert repository.get(report.response_id) is None
    store.close()


def test_real_review_decision_and_audit_roll_back_when_report_write_fails(tmp_path):
    store = SQLiteStore(tmp_path)
    _add_response(store)
    teacher = Actor(actor_id="fixture-teacher", role=ActorRole.TEACHER)
    store.add_account(AccountRecord(teacher, "fixture-hash"))
    report_repository = SQLiteReportRepository(store)
    report = _report()
    report_repository.put(report)
    review_repository = SQLiteReviewRepository(store)
    now = datetime(2026, 10, 2, tzinfo=UTC)
    review_repository.add(ReviewCandidate(
        response_id=report.response_id, response_revision=1,
        assessment_status=AssessmentStatus.NOT_EVALUATED, proposed_band=None,
        reasons=(ReasonCode.MODEL_VERSION_MISSING,),
        source_versions={"model": "unavailable"}, state=ReviewState.PENDING,
        created_at=now, updated_at=now,
    ))
    store.connection.execute("""
        CREATE TRIGGER fail_report_update BEFORE UPDATE ON diagnostic_reports
        BEGIN SELECT RAISE(ABORT, 'fixture write failure'); END
    """)
    service = ReviewService(
        review_repository, clock=lambda: now,
        report_sink=ReportService(report_repository, decision_verifier=review_repository),
    )
    try:
        service.decide(teacher, report.response_id, ReviewActionRequest(
            action=ReviewAction.OVERRIDE, expected_revision=1,
            final_band="B1", reason="fixture verification",
        ))
    except Exception:
        pass
    else:
        raise AssertionError("report failure did not abort teacher decision")
    assert review_repository.get(report.response_id).state is ReviewState.PENDING
    assert review_repository.list_audit() == ()
    assert not report_repository.get(report.response_id).teacher_verified
    store.close()


def _add_response(store: SQLiteStore) -> None:
    actor = Actor(actor_id="fixture-student", role=ActorRole.STUDENT)
    store.add_account(AccountRecord(actor, "fixture-hash"))
    response_id = "a" * 32
    store.save_response(
        ResponseRecord(
            response_id=response_id, owner_id=actor.actor_id, task_id="task",
            task_version="v1", blob=BlobRef(blob_id="b" * 32, sha256="c" * 64, size_bytes=1),
            created_at=datetime(2026, 10, 2, tzinfo=UTC),
        ),
        AuditEvent(
            event_id="d" * 32, actor_id=actor.actor_id, action="submitted",
            object_id=response_id, recorded_at=datetime(2026, 10, 2, tzinfo=UTC),
        ),
    )
