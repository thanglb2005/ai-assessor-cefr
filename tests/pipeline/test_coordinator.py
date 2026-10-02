import io
import sqlite3
from types import SimpleNamespace

import numpy as np
import pytest
import soundfile as sf

from aicefr.audio.config import AudioFormat, QCConfig
from aicefr.auth.service import AccountRecord, ConsentService
from aicefr.contracts import (
    Actor,
    ActorRole,
    AsrStatus,
    Assessment,
    AssessmentStatus,
    Band,
    Criterion,
    CriterionCoverage,
    FeatureSet,
    FeatureValue,
    Interaction,
    Provenance,
    QCStatus,
    ReasonCode,
    ResponseStatus,
    ReviewAction,
    ReviewState,
    Transcript,
    Word,
)
from aicefr.pipeline.coordinator import PipelineCoordinator
from aicefr.report.contracts import (
    CommentRequest,
    CommentTemplate,
    EvidenceRef,
    EvidenceSource,
)
from aicefr.report.service import DiagnosticReportBuilder, ReportInput, ReportService
from aicefr.report.sqlite import SQLiteReportRepository
from aicefr.review.service import ReviewActionRequest, ReviewService
from aicefr.review.sqlite import SQLiteReviewRepository
from aicefr.storage.blob import BlobStore
from aicefr.storage.service import ResponseService
from aicefr.storage.sqlite import ConcurrentResponseUpdate, SQLiteStore


def _audio(*, silence_ratio: float = 0.0, format: str = "WAV") -> bytes:
    samples = np.full(16_000, 0.2, dtype=np.float32)
    samples[: int(len(samples) * silence_ratio)] = 0
    output = io.BytesIO()
    sf.write(output, samples, 16_000, format=format)
    return output.getvalue()


class _Asr:
    def __init__(self, status: AsrStatus = AsrStatus.OK, *, test_only: bool = False):
        self.calls = 0
        self.status = status
        self.test_only = test_only

    def transcribe(self, response_id, audio, qc):
        self.calls += 1
        return Transcript(
            response_id=response_id,
            status=self.status,
            text="hello" if self.status is AsrStatus.OK else "",
            words=(Word(text="hello", start_s=0.1, end_s=0.3),)
            if self.status is AsrStatus.OK
            else (),
            engine="fixture-engine",
            engine_version="1.0",
            decode_config_version="fixture-decode-v1",
            audio_sha256=audio.audio_sha256,
            asr_model="small",
            reasons=(ReasonCode.ASR_FAILED,)
            if self.status is AsrStatus.ASR_FAILED
            else (),
            test_only=self.test_only,
        )


class _Extractor:
    def extract(self, transcript, audio):
        return FeatureSet(
            response_id=transcript.response_id,
            values=(FeatureValue(name="words_per_minute", value=120.0, unit="words/min"),),
            feature_version="fixture-features-v1",
            vad_name="fixture-vad",
            vad_version="1.0",
            vad_threshold=0.5,
            vad_min_silence_ms=150,
            asr_model="small",
            transcript_ref=transcript.response_id,
            audio_sha256=audio.audio_sha256,
        )


class _Scorer:
    def __init__(
        self,
        status: AssessmentStatus = AssessmentStatus.ESTIMATED,
        reasons: tuple[ReasonCode, ...] = (),
    ):
        self.status = status
        self.reasons = reasons

    def score(self, features, transcript):
        estimated = self.status is not AssessmentStatus.NOT_EVALUATED
        return Assessment(
            response_id=features.response_id,
            status=self.status,
            overall_score=3.2 if estimated else None,
            overall_band=Band.B1 if estimated else None,
            criteria=tuple(
                CriterionCoverage(
                    criterion=criterion,
                    coverage=1.0,
                    features=("words_per_minute",) if criterion is Criterion.FLUENCY else (),
                )
                for criterion in Criterion
            ),
            interaction=Interaction(),
            reasons=self.reasons,
            provenance=Provenance(
                model_version="fixture-model-v1",
                model_sha256="0" * 64,
                feature_version="fixture-features-v1",
                band_map_version="fixture-band-v1",
                calibration_version=None,
                trained_with={},
                unit_of_inference="one response",
                scored_at="2026-10-02T00:00:00+00:00",
            ),
        )


class _Stack:
    def __init__(self, root, *, scorer=None, asr=None, extractor=None):
        self.data_dir = root / "data"
        self.store = SQLiteStore(self.data_dir)
        self.student = Actor(actor_id="fixture-student", role=ActorRole.STUDENT)
        self.teacher = Actor(actor_id="fixture-teacher", role=ActorRole.TEACHER)
        self.store.add_account(AccountRecord(self.student, "fixture-hash"))
        self.store.add_account(AccountRecord(self.teacher, "fixture-hash"))
        consent = ConsentService(self.store)
        consent.activate(self.student, "consent-v1")
        self.blobs = BlobStore(self.data_dir, max_bytes=100_000)
        self.responses = ResponseService(self.store, self.blobs, consent)
        self.review_repository = SQLiteReviewRepository(self.store)
        self.reports = SQLiteReportRepository(self.store)
        self.report_service = ReportService(
            self.reports, decision_verifier=self.review_repository
        )
        self.reviews = ReviewService(
            self.review_repository, report_sink=self.report_service
        )
        self.asr = asr or _Asr()
        self.pipeline = PipelineCoordinator(
            responses=self.responses,
            reports=self.report_service,
            reviews=self.reviews,
            qc_config=QCConfig(
                version="fixture-qc-v1",
                accepted_formats=tuple(AudioFormat),
                max_input_bytes=100_000,
                min_duration_s=0.01,
                max_duration_s=2,
                max_input_sample_rate_hz=48_000,
                silence_threshold=0.01,
                clipping_threshold=0.99,
                review_silence_ratio=0.5,
                reject_silence_ratio=0.9,
                review_clipping_ratio=0.3,
                reject_clipping_ratio=0.6,
            ),
            asr=self.asr,
            extractor=extractor or _Extractor(),
            scorer=scorer or _Scorer(),
        )

    def submit(self, data=None):
        return self.responses.submit(
            self.student,
            task_id="fixture-task",
            task_version="v1",
            consent_version="consent-v1",
            audio_bytes=data or _audio(),
        )


def test_sqlite_coordinator_commits_report_status_candidate_and_restart(tmp_path):
    stack = _Stack(tmp_path)
    record = stack.submit(_audio(silence_ratio=0.7))

    stack.pipeline.enqueue(record)

    current = stack.store.get_response(record.response_id)
    report = stack.reports.get(record.response_id)
    candidate = stack.review_repository.get(record.response_id)
    assert current.status is ResponseStatus.REVIEW_REQUIRED
    assert current.status_reason is ReasonCode.QC_SILENCE_REVIEW
    assert report.assessment_status is AssessmentStatus.NOT_EVALUATED
    assert report.overall_score is None and report.overall_band is None
    assert candidate.response_revision == current.revision
    assert candidate.reasons == (ReasonCode.QC_SILENCE_REVIEW,)
    assert stack.asr.calls == 0
    stack.store.close()

    reopened = SQLiteStore(stack.data_dir)
    assert reopened.get_response(record.response_id).status is ResponseStatus.REVIEW_REQUIRED
    assert SQLiteReportRepository(reopened).get(record.response_id) == report
    assert SQLiteReviewRepository(reopened).get(record.response_id) == candidate
    reopened.close()


@pytest.mark.parametrize("fail_table", ["diagnostic_reports", "review_candidates"])
def test_sqlite_final_write_failure_rolls_back_report_status_and_candidate(
    tmp_path, fail_table, caplog
):
    stack = _Stack(
        tmp_path,
        scorer=_Scorer(
            AssessmentStatus.REVIEW_REQUIRED, (ReasonCode.SCORE_NEAR_BOUNDARY,)
        ),
    )
    record = stack.submit()
    stack.store.connection.execute(f"""
        CREATE TRIGGER fail_final_write BEFORE INSERT ON {fail_table}
        BEGIN SELECT RAISE(ABORT, 'private database detail'); END
    """)

    stack.pipeline.enqueue(record)

    current = stack.store.get_response(record.response_id)
    assert current.status is ResponseStatus.FAILED
    assert current.status_reason is ReasonCode.PIPELINE_ENQUEUE_FAILED
    assert stack.reports.get(record.response_id) is None
    assert stack.review_repository.get(record.response_id) is None
    actions = [event.action for event in stack.store.list_audit()]
    assert "pipeline_review_required" not in actions
    assert "pipeline_failed" in actions
    assert "private database detail" not in caplog.text


def test_failure_recovery_reloads_running_revision_after_stale_cas(tmp_path, monkeypatch):
    stack = _Stack(
        tmp_path,
        scorer=_Scorer(
            AssessmentStatus.REVIEW_REQUIRED, (ReasonCode.SCORE_NEAR_BOUNDARY,)
        ),
    )
    record = stack.submit()
    stack.store.connection.execute("""
        CREATE TRIGGER fail_candidate BEFORE INSERT ON review_candidates
        BEGIN SELECT RAISE(ABORT, 'fixture persistence failure'); END
    """)
    transition = stack.responses.transition_status
    injected = False

    def interleaved_transition(**kwargs):
        nonlocal injected
        if kwargs["status"] is ResponseStatus.FAILED and not injected:
            injected = True
            transition(
                response_id=kwargs["response_id"],
                expected_revision=kwargs["expected_revision"],
                status=ResponseStatus.RUNNING,
                actor_id="system-fixture",
                action="fixture_concurrent_update",
            )
            raise ConcurrentResponseUpdate("fixture stale revision")
        return transition(**kwargs)

    monkeypatch.setattr(stack.responses, "transition_status", interleaved_transition)

    stack.pipeline.enqueue(record)

    current = stack.store.get_response(record.response_id)
    assert current.status is ResponseStatus.FAILED
    assert current.status_reason is ReasonCode.PIPELINE_ENQUEUE_FAILED
    assert stack.reports.get(record.response_id) is None
    assert stack.review_repository.get(record.response_id) is None


def test_duplicate_and_nonqueued_sqlite_claims_never_repeat_asr(tmp_path):
    stack = _Stack(tmp_path)
    record = stack.submit()
    stack.pipeline.enqueue(record)
    calls = stack.asr.calls

    stack.pipeline.enqueue(record)
    completed = stack.store.get_response(record.response_id)
    stack.pipeline.enqueue(completed)
    stack.pipeline.enqueue(record.model_copy(update={"revision": 999}))

    assert stack.asr.calls == calls == 1
    assert stack.store.get_response(record.response_id).status is ResponseStatus.COMPLETED


def test_claim_rejects_forged_blob_or_owner_provenance(tmp_path):
    stack = _Stack(tmp_path)
    record = stack.submit()
    forged = record.model_copy(update={"owner_id": "other-student"})

    stack.pipeline.enqueue(forged)

    assert stack.asr.calls == 0
    assert stack.store.get_response(record.response_id).status is ResponseStatus.QUEUED
    stack.pipeline.enqueue(record)
    assert stack.asr.calls == 1


def test_asr_refusal_survives_scorer_model_refusal_without_estimate(tmp_path):
    stack = _Stack(
        tmp_path,
        asr=_Asr(AsrStatus.ASR_FAILED),
        scorer=_Scorer(
            AssessmentStatus.NOT_EVALUATED, (ReasonCode.MODEL_VERSION_MISSING,)
        ),
    )
    record = stack.submit()

    stack.pipeline.enqueue(record)

    current = stack.store.get_response(record.response_id)
    report = stack.reports.get(record.response_id)
    candidate = stack.review_repository.get(record.response_id)
    assert current.status is ResponseStatus.REVIEW_REQUIRED
    assert current.status_reason is ReasonCode.ASR_FAILED
    assert report.reasons == (ReasonCode.ASR_FAILED, ReasonCode.MODEL_VERSION_MISSING)
    assert report.overall_score is None and report.overall_band is None
    assert report.comments == ()
    assert candidate.reasons == report.reasons


def test_review_decision_report_callback_failure_rolls_back_decision_and_audit(tmp_path):
    stack = _Stack(tmp_path)
    record = stack.submit(_audio(silence_ratio=0.7))
    stack.pipeline.enqueue(record)
    stack.store.connection.execute("""
        CREATE TRIGGER fail_teacher_report BEFORE UPDATE ON diagnostic_reports
        BEGIN SELECT RAISE(ABORT, 'private teacher write detail'); END
    """)

    with pytest.raises(sqlite3.IntegrityError):
        stack.reviews.decide(
            stack.teacher,
            record.response_id,
            ReviewActionRequest(
                action=ReviewAction.OVERRIDE,
                expected_revision=1,
                final_band=Band.B1,
                reason="fixture override",
            ),
        )

    assert stack.review_repository.get(record.response_id).state is ReviewState.PENDING
    assert stack.review_repository.list_audit() == ()
    assert not stack.reports.get(record.response_id).teacher_verified
    count = stack.store.connection.execute(
        "SELECT count(*) FROM review_decisions WHERE response_id=?", (record.response_id,)
    ).fetchone()[0]
    assert count == 0


def test_scorer_near_boundary_creates_durable_candidate(tmp_path):
    stack = _Stack(
        tmp_path,
        scorer=_Scorer(
            AssessmentStatus.REVIEW_REQUIRED, (ReasonCode.SCORE_NEAR_BOUNDARY,)
        ),
    )
    record = stack.submit()
    stack.pipeline.enqueue(record)
    current = stack.store.get_response(record.response_id)
    candidate = stack.review_repository.get(record.response_id)
    assert current.status is ResponseStatus.REVIEW_REQUIRED
    assert current.status_reason is ReasonCode.SCORE_NEAR_BOUNDARY
    assert candidate.reasons == (ReasonCode.SCORE_NEAR_BOUNDARY,)
    assert candidate.response_revision == current.revision


@pytest.mark.parametrize("audio_format", ["FLAC", "OGG", "MP3"])
def test_pipeline_sniffs_supported_containers_from_generated_audio(
    tmp_path, audio_format
):
    if audio_format not in sf.available_formats():
        pytest.skip(f"libsndfile does not support {audio_format}")
    stack = _Stack(tmp_path)
    record = stack.submit(_audio(format=audio_format))
    stack.pipeline.enqueue(record)
    assert stack.store.get_response(record.response_id).status is ResponseStatus.COMPLETED
    assert stack.reports.get(record.response_id) is not None


def test_corrupt_container_is_rejected_without_calling_asr(tmp_path):
    stack = _Stack(tmp_path)
    record = stack.submit(b"corrupt encoded data")
    stack.pipeline.enqueue(record)
    current = stack.store.get_response(record.response_id)
    assert current.status is ResponseStatus.REJECTED
    assert current.status_reason is ReasonCode.QC_UNSUPPORTED_FORMAT
    assert stack.asr.calls == 0
    assert stack.reports.get(record.response_id) is None


def test_container_outside_m02_whitelist_is_rejected(tmp_path):
    stack = _Stack(tmp_path)
    record = stack.submit(_audio(format="AIFF"))

    stack.pipeline.enqueue(record)

    current = stack.store.get_response(record.response_id)
    assert current.status is ResponseStatus.REJECTED
    assert current.status_reason is ReasonCode.QC_UNSUPPORTED_FORMAT
    assert stack.asr.calls == 0
    assert stack.reports.get(record.response_id) is None


def test_missing_asr_transcript_fails_with_pipeline_reason(tmp_path, monkeypatch):
    import aicefr.pipeline.coordinator as coordinator_module

    stack = _Stack(tmp_path)
    record = stack.submit()
    monkeypatch.setattr(
        coordinator_module,
        "process_audio",
        lambda **_: SimpleNamespace(
            qc=SimpleNamespace(status=QCStatus.PASS, reasons=()),
            audio=SimpleNamespace(duration_s=1.0),
            transcript=None,
        ),
    )
    stack.pipeline.enqueue(record)
    current = stack.store.get_response(record.response_id)
    assert current.status is ResponseStatus.FAILED
    assert current.status_reason is ReasonCode.PIPELINE_ENQUEUE_FAILED
    assert stack.reports.get(record.response_id) is None


def test_empty_qc_review_reasons_fail_closed(tmp_path, monkeypatch):
    import aicefr.pipeline.coordinator as coordinator_module

    stack = _Stack(tmp_path)
    record = stack.submit()
    monkeypatch.setattr(
        coordinator_module,
        "process_audio",
        lambda **_: SimpleNamespace(
            qc=SimpleNamespace(status=QCStatus.REVIEW, reasons=()),
            audio=SimpleNamespace(duration_s=1.0),
            transcript=None,
        ),
    )
    stack.pipeline.enqueue(record)
    report = stack.reports.get(record.response_id)
    candidate = stack.review_repository.get(record.response_id)
    assert report.reasons == (ReasonCode.QC_MEASUREMENT_MISSING,)
    assert candidate.reasons == (ReasonCode.QC_MEASUREMENT_MISSING,)
    assert stack.store.get_response(record.response_id).status is ResponseStatus.REVIEW_REQUIRED
    assert stack.asr.calls == 0


def test_success_report_contains_only_valid_transcript_and_feature_evidence(tmp_path):
    stack = _Stack(tmp_path)
    record = stack.submit()

    stack.pipeline.enqueue(record)

    report = stack.reports.get(record.response_id)
    assert report.source_versions["asr_engine"] == "fixture-engine@1.0"
    assert report.source_versions["feature_set"] == "fixture-features-v1"
    assert report.source_versions["qc_config"] == "fixture-qc-v1"
    assert {comment.source for comment in report.comments} == {
        EvidenceSource.TRANSCRIPT, EvidenceSource.FEATURE_SET
    }
    assert len(report.comments) == 2
    assert report.evidence_issues == ()


def test_test_only_transcript_does_not_generate_report_evidence(tmp_path):
    stack = _Stack(tmp_path, asr=_Asr(test_only=True))
    record = stack.submit()

    stack.pipeline.enqueue(record)

    report = stack.reports.get(record.response_id)
    assert report.comments == ()
    assert report.evidence_issues == ()


def test_builder_drops_foreign_and_stale_evidence_refs():
    assessment = _Scorer().score(
        FeatureSet(
            response_id="local-response",
            values=(FeatureValue(name="words_per_minute", value=120.0, unit="words/min"),),
            feature_version="fixture-features-v1",
            vad_name=None,
            vad_version=None,
            vad_threshold=None,
            vad_min_silence_ms=None,
            asr_model=None,
            transcript_ref=None,
            audio_sha256="0" * 64,
        ),
        Transcript(
            response_id="local-response", status=AsrStatus.OK, text="hello",
            words=(), engine="fixture", engine_version="1",
            decode_config_version="decode-v1", audio_sha256="0" * 64,
        ),
    )
    transcript = Transcript(
        response_id="local-response", status=AsrStatus.OK, text="hello", words=(),
        engine="fixture", engine_version="1", decode_config_version="decode-v1",
        audio_sha256="0" * 64,
    )
    features = FeatureSet(
        response_id="local-response",
        values=(FeatureValue(name="words_per_minute", value=120.0, unit="words/min"),),
        feature_version="fixture-features-v1",
        vad_name=None, vad_version=None, vad_threshold=None, vad_min_silence_ms=None,
        asr_model=None, transcript_ref=None, audio_sha256="0" * 64,
    )
    report = DiagnosticReportBuilder().build(ReportInput(
        response_id="local-response", audio_duration_s=1, assessment=assessment,
        transcript=transcript, features=features,
        evidence_refs=(
            EvidenceRef(
                evidence_id="foreign", response_id="foreign-response",
                source=EvidenceSource.TRANSCRIPT, source_version="decode-v1",
                criterion=Criterion.FLUENCY,
            ),
            EvidenceRef(
                evidence_id="stale", response_id="local-response",
                source=EvidenceSource.FEATURE_SET, source_version="stale-features",
                criterion=Criterion.FLUENCY,
            ),
            EvidenceRef(
                evidence_id="feature:words_per_minute:0x1.0000000000000p+0",
                response_id="local-response",
                source=EvidenceSource.FEATURE_SET,
                source_version="fixture-features-v1",
                criterion=Criterion.FLUENCY,
            ),
        ),
        comment_requests=(
            CommentRequest(
                criterion=Criterion.FLUENCY,
                template=CommentTemplate.WORD_TIMING_OBSERVED,
                evidence_id="foreign",
            ),
            CommentRequest(
                criterion=Criterion.FLUENCY,
                template=CommentTemplate.FEATURE_VALUE_AVAILABLE,
                evidence_id="stale",
            ),
            CommentRequest(
                criterion=Criterion.FLUENCY,
                template=CommentTemplate.FEATURE_VALUE_AVAILABLE,
                evidence_id="feature:words_per_minute:0x1.0000000000000p+0",
            ),
        ),
    ))
    assert report.comments == ()
    assert {issue.reason for issue in report.evidence_issues} == {
        "EVIDENCE_RESPONSE_MISMATCH", "EVIDENCE_SOURCE_VERSION_MISMATCH",
        "EVIDENCE_FEATURE_VALUE_MISMATCH", "COMMENT_EVIDENCE_MISSING",
    }


def test_invalid_timestamps_and_missing_features_produce_no_evidence(tmp_path):
    stack = _Stack(tmp_path)
    response_id = "fixture-response"
    transcript = Transcript(
        response_id=response_id,
        status=AsrStatus.OK,
        text="hello",
        words=(Word(text="hello", start_s=1.2, end_s=1.4),),
        engine="fixture",
        engine_version="1",
        decode_config_version="decode-v1",
        audio_sha256="0" * 64,
    )
    features = FeatureSet(
        response_id=response_id,
        values=(FeatureValue(
            name="words_per_minute", value=None, unit="words/min",
            missing_reason=ReasonCode.FEATURE_NOT_COMPUTABLE,
        ),),
        feature_version="fixture-features-v1",
        vad_name=None,
        vad_version=None,
        vad_threshold=None,
        vad_min_silence_ms=None,
        asr_model="small",
        transcript_ref=response_id,
        audio_sha256="0" * 64,
    )
    assessment = _Scorer().score(features, transcript)

    report_input = stack.pipeline._report_input(
        response_id, 1.0, assessment, transcript, features
    )

    assert report_input.evidence_refs == ()
    assert report_input.comment_requests == ()
