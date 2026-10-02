"""Connect M01/M02 through M07 using injected, typed domain services."""

from __future__ import annotations

import io
import logging
from contextlib import nullcontext
from datetime import UTC, datetime
from typing import Protocol

import soundfile as sf

from aicefr.audio.config import AudioFormat, QCConfig
from aicefr.audio.pipeline import process_audio
from aicefr.contracts import (
    Assessment,
    AssessmentStatus,
    Criterion,
    CriterionCoverage,
    Interaction,
    Provenance,
    QCStatus,
    ReasonCode,
    ResponseRecord,
    ResponseStatus,
    ReviewCandidate,
    ReviewState,
)
from aicefr.report.service import ReportInput
from aicefr.review.routing import review_candidate_from_assessment
from aicefr.storage.sqlite import ConcurrentResponseUpdate

log = logging.getLogger(__name__)


class _Responses(Protocol):
    blobs: object

    def transition_status(self, *, response_id: str, expected_revision: int,
                          status: ResponseStatus, actor_id: str, action: str,
                          reason: ReasonCode | None = None) -> ResponseRecord: ...


class PipelineCoordinator:
    def __init__(self, *, responses, reports, reviews, qc_config: QCConfig,
                 asr, extractor, scorer) -> None:
        self._responses = responses
        self._reports = reports
        self._reviews = reviews
        self._qc_config = qc_config
        self._asr = asr
        self._extractor = extractor
        self._scorer = scorer

    def enqueue(self, response: ResponseRecord) -> None:
        if response.status is not ResponseStatus.QUEUED:
            return
        store = getattr(self._responses, "metadata", None)
        claim = getattr(store, "claim_queued_response", None)
        try:
            if claim is not None:
                current = claim(response)
            else:
                current = self._responses.transition_status(
                    response_id=response.response_id, expected_revision=response.revision,
                    status=ResponseStatus.RUNNING, actor_id="system-pipeline",
                    action="pipeline_started",
                )
        except ConcurrentResponseUpdate:
            return
        reason = ReasonCode.ASR_FAILED
        try:
            # The response carries an immutable, checksummed reference. Read only
            # through the configured BlobStore; never interpret a client path.
            data = self._responses.blobs.read(response.blob)
            extension = self._container_extension(data)
            result = process_audio(response_id=response.response_id, data=data,
                                   declared_extension=extension,
                                   config=self._qc_config, asr=self._asr)
            if result.qc.status is QCStatus.REJECT:
                reason = result.qc.reasons[0] if result.qc.reasons else ReasonCode.QC_DECODE_FAILED
                self._responses.transition_status(
                    response_id=response.response_id, expected_revision=current.revision,
                    status=ResponseStatus.REJECTED, actor_id="system-pipeline",
                    action="pipeline_rejected", reason=reason,
                )
                return
            if result.qc.status is QCStatus.REVIEW:
                assessment = self._not_evaluated(response.response_id, result.qc.reasons)
                with self._unit_of_work():
                    self._reports.build_and_store(ReportInput(
                        response_id=response.response_id,
                        audio_duration_s=result.audio.duration_s if result.audio else 0,
                        assessment=assessment,
                    ))
                    final = self._responses.transition_status(
                        response_id=response.response_id, expected_revision=current.revision,
                        status=ResponseStatus.REVIEW_REQUIRED, actor_id="system-pipeline",
                        action="pipeline_review_required", reason=result.qc.reasons[0],
                    )
                    now = datetime.now(UTC)
                    self._reviews.add_candidate(ReviewCandidate(
                        response_id=response.response_id, response_revision=final.revision,
                        assessment_status=assessment.status, proposed_band=None,
                        reasons=assessment.reasons, source_versions={"qc": self._qc_config.version},
                        state=ReviewState.PENDING, created_at=now, updated_at=now,
                    ))
                return

            transcript = result.transcript
            if transcript is None:
                raise RuntimeError("ASR result missing")
            features = self._extractor.extract(transcript, result.audio)
            assessment = self._scorer.score(features, transcript)
            needs_review = assessment.status is not AssessmentStatus.ESTIMATED
            with self._unit_of_work():
                self._reports.build_and_store(ReportInput(
                    response_id=response.response_id,
                    audio_duration_s=result.audio.duration_s,
                    assessment=assessment, transcript=transcript, features=features,
                ))
                final = self._responses.transition_status(
                    response_id=response.response_id, expected_revision=current.revision,
                    status=(ResponseStatus.REVIEW_REQUIRED if needs_review
                            else ResponseStatus.COMPLETED),
                    actor_id="system-pipeline",
                    action="pipeline_review_required" if needs_review else "pipeline_completed",
                    reason=assessment.reasons[0] if needs_review and assessment.reasons else None,
                )
                if needs_review:
                    self._reviews.add_candidate(review_candidate_from_assessment(
                        assessment, response_revision=final.revision,
                    ))
        except Exception:
            # Stable reason only. Exceptions may contain model details or data;
            # never log their value or traceback at this boundary.
            log.error("pipeline failed response_id=%s", response.response_id)
            try:
                latest = self._responses.transition_status(
                    response_id=response.response_id, expected_revision=current.revision,
                    status=ResponseStatus.FAILED, actor_id="system-pipeline",
                    action="pipeline_failed", reason=reason,
                )
                del latest
            except Exception:
                pass

    def _unit_of_work(self):
        store = getattr(self._responses, "metadata", None)
        return store.transaction() if store is not None else nullcontext()

    @staticmethod
    def _container_extension(data: bytes) -> str:
        try:
            with sf.SoundFile(io.BytesIO(data)) as handle:
                fmt, subtype = handle.format.upper(), handle.subtype.upper()
        except Exception:
            return "unsupported"
        if fmt == "WAV" and subtype.startswith("PCM_"):
            return AudioFormat.WAV_PCM.value
        if fmt == "FLAC" and subtype.startswith("PCM_"):
            return AudioFormat.FLAC.value
        if fmt == "OGG" and subtype == "VORBIS":
            return AudioFormat.OGG_VORBIS.value
        if fmt == "MPEG_LAYER_III" or subtype == "MPEG_LAYER_III":
            return AudioFormat.MP3.value
        return "unsupported"

    @staticmethod
    def _not_evaluated(
        response_id: str, reasons: tuple[ReasonCode, ...]
    ) -> Assessment:
        safe_reasons = reasons or (ReasonCode.QC_MEASUREMENT_MISSING,)
        return Assessment(
            response_id=response_id, status=AssessmentStatus.NOT_EVALUATED,
            criteria=tuple(CriterionCoverage(criterion=item, reasons=safe_reasons)
                           for item in Criterion),
            interaction=Interaction(), reasons=safe_reasons,
            provenance=Provenance(model_version=None, model_sha256=None,
                                  feature_version=None, band_map_version=None,
                                  calibration_version=None, trained_with={},
                                  unit_of_inference=None,
                                  scored_at=datetime.now(UTC).isoformat()),
        )
