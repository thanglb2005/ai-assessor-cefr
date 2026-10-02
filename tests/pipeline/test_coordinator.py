import hashlib
import io
from datetime import UTC, datetime

import numpy as np
import soundfile as sf

from aicefr.audio.config import AudioFormat, QCConfig
from aicefr.contracts import (
    AsrStatus,
    Assessment,
    AssessmentStatus,
    BlobRef,
    Criterion,
    CriterionCoverage,
    FeatureSet,
    Interaction,
    Provenance,
    ReasonCode,
    ResponseRecord,
    ResponseStatus,
    Transcript,
)
from aicefr.pipeline.coordinator import PipelineCoordinator
from aicefr.report.service import MemoryReportRepository, ReportService
from aicefr.storage.sqlite import ConcurrentResponseUpdate


def _bytes(amplitude: float = 0.2, *, silence_ratio: float = 0) -> bytes:
    stream = io.BytesIO()
    samples = np.full(16_000, amplitude, dtype=np.float32)
    samples[: int(len(samples) * silence_ratio)] = 0
    sf.write(stream, samples, 16_000, format="WAV")
    return stream.getvalue()


def _record(data: bytes) -> ResponseRecord:
    return ResponseRecord(
        response_id="a" * 32, owner_id="student", task_id="task", task_version="v1",
        blob=BlobRef(blob_id="b" * 32, sha256=hashlib.sha256(data).hexdigest(),
                     size_bytes=len(data)),
        created_at=datetime(2026, 10, 2, tzinfo=UTC),
    )


class _Responses:
    def __init__(self, record: ResponseRecord, data: bytes):
        self.record = record
        self.blobs = self
        self.data = data

    def read(self, blob):
        assert blob == self.record.blob
        assert hashlib.sha256(self.data).hexdigest() == blob.sha256
        return self.data

    def transition_status(self, *, response_id, expected_revision, status, actor_id,
                          action, reason=None):
        assert response_id == self.record.response_id
        if self.record.revision != expected_revision:
            raise ConcurrentResponseUpdate("stale revision")
        self.record = self.record.model_copy(update={
            "status": status, "status_reason": reason, "revision": expected_revision + 1,
        })
        return self.record


class _Asr:
    def __init__(self):
        self.calls = 0

    def transcribe(self, response_id, audio, qc):
        self.calls += 1
        return Transcript(
            response_id=response_id, status=AsrStatus.OK, text="hello", engine="fixture",
            engine_version="1", decode_config_version="v1",
            audio_sha256=audio.audio_sha256,
        )


class _Extractor:
    def extract(self, transcript, audio):
        return FeatureSet(
            response_id=transcript.response_id, values=(), feature_version="fixture-v1",
            vad_name=None, vad_version=None, vad_threshold=None, vad_min_silence_ms=None,
            asr_model=None, transcript_ref=transcript.response_id,
            audio_sha256=audio.audio_sha256,
        )


class _Scorer:
    def score(self, features, transcript):
        return Assessment(
            response_id=features.response_id, status=AssessmentStatus.ESTIMATED,
            overall_score=3.2, overall_band="B1",
            criteria=tuple(CriterionCoverage(criterion=item) for item in Criterion),
            interaction=Interaction(), provenance=Provenance(
                model_version="fixture", model_sha256=None, feature_version="fixture-v1",
                band_map_version="fixture", calibration_version=None, trained_with={},
                unit_of_inference="fixture", scored_at="2026-10-02T00:00:00+00:00",
            ),
        )


class _Reviews:
    def __init__(self):
        self.candidates = []

    def add_candidate(self, candidate):
        self.candidates.append(candidate)


def _coordinator(responses, asr, *, extractor=None):
    reports = ReportService(MemoryReportRepository())
    reviews = _Reviews()
    pipeline = PipelineCoordinator(
        responses=responses, reports=reports,
        reviews=reviews, qc_config=QCConfig(
            version="test", accepted_formats=tuple(AudioFormat), max_input_bytes=100_000,
            min_duration_s=0.01, max_duration_s=2, max_input_sample_rate_hz=48_000,
            silence_threshold=0.01, clipping_threshold=0.99,
            review_silence_ratio=0.5, reject_silence_ratio=0.9,
            review_clipping_ratio=0.3, reject_clipping_ratio=0.6,
        ), asr=asr, extractor=extractor or _Extractor(), scorer=_Scorer(),
    )
    pipeline.reports = reports
    pipeline.reviews = reviews
    return pipeline


def test_pipeline_completes_after_report_persist_and_duplicate_does_not_rerun():
    data = _bytes()
    response = _record(data)
    responses, asr = _Responses(response, data), _Asr()
    pipeline = _coordinator(responses, asr)

    pipeline.enqueue(response)
    assert responses.record.status is ResponseStatus.COMPLETED
    assert asr.calls == 1
    assert pipeline.reports.get(response.response_id) is not None
    pipeline.enqueue(response)
    assert asr.calls == 1


def test_pipeline_marks_failed_without_logging_exception_payload(caplog):
    data = _bytes()
    response = _record(data)

    class BrokenExtractor:
        def extract(self, transcript, audio):
            raise RuntimeError("private transcript payload")

    responses = _Responses(response, data)
    _coordinator(responses, _Asr(), extractor=BrokenExtractor()).enqueue(response)
    assert responses.record.status is ResponseStatus.FAILED
    assert responses.record.status_reason is ReasonCode.ASR_FAILED
    assert "private transcript payload" not in caplog.text


def test_qc_reject_does_not_call_asr_or_create_report():
    data = _bytes(amplitude=0)
    response = _record(data)
    responses, asr = _Responses(response, data), _Asr()
    pipeline = _coordinator(responses, asr)

    pipeline.enqueue(response)

    assert responses.record.status is ResponseStatus.REJECTED
    assert responses.record.status_reason is ReasonCode.QC_SILENCE_REJECT
    assert asr.calls == 0
    assert pipeline.reports.get(response.response_id) is None


def test_qc_review_persists_unscored_report_and_candidate_without_asr():
    data = _bytes(silence_ratio=0.7)
    response = _record(data)
    responses, asr = _Responses(response, data), _Asr()
    pipeline = _coordinator(responses, asr)

    pipeline.enqueue(response)

    report = pipeline.reports.get(response.response_id)
    assert responses.record.status is ResponseStatus.REVIEW_REQUIRED
    assert report.assessment_status is AssessmentStatus.NOT_EVALUATED
    assert report.overall_score is None and report.overall_band is None
    assert asr.calls == 0
    assert pipeline.reviews.candidates[0].response_revision == responses.record.revision
