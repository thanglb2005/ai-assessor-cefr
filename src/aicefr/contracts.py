"""Hợp đồng dữ liệu dùng chung giữa các module.

Bản đầu chỉ gồm phần M03 (ASR), M04 (Features), M05 (Scoring) cần, lấy field
từ Specification v0.2 đã duyệt của ba module đó, cộng hai kiểu đầu vào từ M02
(`QCResult`, `DecodedAudio`) ở mức tối thiểu. Owner M01/M02/M06/M07/M08 bổ sung
kiểu và reason code của module mình vào đây.

Nguyên tắc: thiếu dữ liệu là `None` kèm reason, không bao giờ là 0 hay giá trị
trung bình.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator

# M03 và M04 cần audio 16 kHz mono (whisper-small và Silero VAD). Chờ owner M02
# xác nhận (M03-O-002, SCRUM-16); DecodedAudio chỉ ghi lại sample rate thực tế.
EXPECTED_SAMPLE_RATE_HZ = 16_000


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# --- M08 — Identity and consent ----------------------------------------------


class ActorRole(StrEnum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class Actor(_Frozen):
    actor_id: str = Field(min_length=1)
    role: ActorRole


class ConsentState(StrEnum):
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"


class ConsentRecord(_Frozen):
    participant_id: str = Field(min_length=1)
    consent_version: str = Field(min_length=1)
    state: ConsentState
    recorded_at: datetime


class SessionRecord(_Frozen):
    token_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    actor_id: str = Field(min_length=1)
    role: ActorRole
    created_at: datetime
    last_seen_at: datetime
    idle_expires_at: datetime
    absolute_expires_at: datetime


class ReasonCode(StrEnum):
    # M03 — ASR
    ASR_FAILED = "ASR_FAILED"
    ASR_EMPTY_TRANSCRIPT = "ASR_EMPTY_TRANSCRIPT"
    ASR_HALLUCINATION = "ASR_HALLUCINATION"
    ASR_VERSION_MISMATCH = "ASR_VERSION_MISMATCH"
    # M04 — Features
    VAD_VERSION_MISMATCH = "VAD_VERSION_MISMATCH"
    FEATURE_NOT_COMPUTABLE = "FEATURE_NOT_COMPUTABLE"
    TOO_FEW_WORDS = "TOO_FEW_WORDS"
    FEATURE_VERSION_MISMATCH = "FEATURE_VERSION_MISMATCH"
    # M05 — Scoring
    OUT_OF_DISTRIBUTION = "OUT_OF_DISTRIBUTION"
    SCORE_NEAR_BOUNDARY = "SCORE_NEAR_BOUNDARY"
    MODEL_VERSION_MISSING = "MODEL_VERSION_MISSING"
    MODEL_ARTIFACT_INVALID = "MODEL_ARTIFACT_INVALID"


# --- M02 → M03/M04 -----------------------------------------------------------


class QCStatus(StrEnum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


class QCResult(_Frozen):
    status: QCStatus
    reasons: tuple[str, ...] = ()
    qc_config_version: str


class DecodedAudio(_Frozen):
    """PCM float32 mono đã giải mã. Không ghi đè bản gốc."""

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    samples: np.ndarray
    sample_rate_hz: int = Field(gt=0)
    duration_s: float = Field(ge=0)
    audio_sha256: str

    @field_validator("samples")
    @classmethod
    def _mono_float32(cls, v: np.ndarray) -> np.ndarray:
        if v.ndim != 1:
            raise ValueError("samples phải là mảng 1 chiều (mono)")
        if v.dtype != np.float32:
            raise ValueError("samples phải có dtype float32")
        return v


# --- M08 — Stored response and audit -----------------------------------------


class BlobRef(_Frozen):
    blob_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size_bytes: int = Field(gt=0)


class ResponseRecord(_Frozen):
    response_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    owner_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    task_version: str = Field(min_length=1)
    blob: BlobRef
    status: str = "submitted"
    revision: int = Field(default=1, ge=1)
    created_at: datetime


class AuditEvent(_Frozen):
    event_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    actor_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    object_id: str = Field(min_length=1)
    recorded_at: datetime
    reason: str | None = None


# --- M03 — ASR ---------------------------------------------------------------


class AsrStatus(StrEnum):
    OK = "OK"
    UNRELIABLE = "UNRELIABLE"
    ASR_FAILED = "ASR_FAILED"
    NOT_RUN = "NOT_RUN"


class Word(_Frozen):
    text: str
    start_s: float
    end_s: float
    prob: float | None = Field(default=None, ge=0.0, le=1.0)


class Transcript(_Frozen):
    response_id: str
    status: AsrStatus
    text: str = ""
    words: tuple[Word, ...] = ()
    asr_model: str | None = None
    engine: str
    engine_version: str
    decode_config_version: str
    audio_sha256: str
    reasons: tuple[ReasonCode, ...] = ()
    test_only: bool = False


# --- M04 — Features ----------------------------------------------------------


class FeatureValue(_Frozen):
    name: str
    value: float | None
    unit: str
    missing_reason: ReasonCode | None = None


class FeatureSet(_Frozen):
    response_id: str
    values: tuple[FeatureValue, ...]
    feature_version: str
    vad_name: str | None
    vad_version: str | None
    vad_threshold: float | None
    vad_min_silence_ms: int | None
    asr_model: str | None
    transcript_ref: str | None
    audio_sha256: str
    reasons: tuple[ReasonCode, ...] = ()

    def names(self) -> tuple[str, ...]:
        return tuple(v.name for v in self.values)

    def value_of(self, name: str) -> float | None:
        for v in self.values:
            if v.name == name:
                return v.value
        raise KeyError(name)


# --- M05 — Scoring -----------------------------------------------------------


class Criterion(StrEnum):
    RANGE = "range"
    ACCURACY = "accuracy"
    FLUENCY = "fluency"
    COHERENCE = "coherence"
    PHONOLOGY = "phonology"


class Band(StrEnum):
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"


class AssessmentStatus(StrEnum):
    ESTIMATED = "ESTIMATED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_EVALUATED = "NOT_EVALUATED"


class CriterionCoverage(_Frozen):
    """Chỉ mang coverage của một tiêu chí; không có điểm hay band riêng."""

    criterion: Criterion
    coverage: float | None = Field(default=None, ge=0.0, le=1.0)
    features: tuple[str, ...] = ()
    reasons: tuple[ReasonCode, ...] = ()


class Interaction(_Frozen):
    """Bài độc thoại không có bằng chứng tương tác."""

    level: None = None
    score_status: str = "insufficient_evidence"


class Provenance(_Frozen):
    model_version: str | None
    model_sha256: str | None
    feature_version: str | None
    band_map_version: str | None
    calibration_version: str | None
    trained_with: dict[str, Any] = Field(default_factory=dict)
    unit_of_inference: str | None
    scored_at: str


class OutOfRangeFeature(_Frozen):
    """Đặc trưng nằm ngoài khoảng chấp nhận của model, để báo lý do cho người học."""

    feature: str
    value: float
    accepted_low: float
    accepted_high: float
    too: str  # "low" | "high"


class Assessment(_Frozen):
    response_id: str
    status: AssessmentStatus
    overall_score: float | None = Field(default=None, ge=1.0, le=6.0)
    overall_band: Band | None = None
    criteria: tuple[CriterionCoverage, ...]
    interaction: Interaction = Interaction()
    reasons: tuple[ReasonCode, ...] = ()
    out_of_range: tuple[OutOfRangeFeature, ...] = ()
    provenance: Provenance
    teacher_verified: bool = False
