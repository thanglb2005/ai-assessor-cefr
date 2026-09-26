"""Ghép FeatureSet (M04 Spec v0.2).

Tên và thứ tự đặc trưng đọc từ `feature_order` của artifact M05 (M04-FR-003),
không có danh sách thứ hai trong code. VAD do M04 chạy (M04-FR-004); VAD lỗi
thì không đổi sang VAD khác.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from aicefr.contracts import (
    AsrStatus,
    DecodedAudio,
    FeatureSet,
    FeatureValue,
    ReasonCode,
    Transcript,
)
from aicefr.features.pauses import VAD_FEATURES, pause_features
from aicefr.features.text import Measure, normalize_tokens, text_features

log = logging.getLogger(__name__)

FEATURE_VERSION = "v3"

UNITS: dict[str, str] = {
    "n_words": "từ",
    "words_per_sec": "từ/s",
    "total_dur": "s",
    "mean_word_len": "ký tự",
    "ttr": "tỷ lệ",
    "log_uniq": "-",
    "asr_conf_mean": "[0,1]",
    "asr_conf_geo": "[0,1]",
    "vad_silence_ratio": "tỷ lệ",
    "vad_mean_pause": "s",
    "vad_pause_per_min": "lần/phút",
    "vad_long_pause_ratio": "tỷ lệ",
    "vad_pause_sd": "s",
    "vad_mean_seg_len": "s",
    "vad_n_seg_per_min": "lần/phút",
    "vad_articulation_rate": "từ/s nói",
    "vad_onset_delay": "s",
    "vad_speech_sec": "s",
}
# Đặc trưng cần transcript OK (bảng dữ liệu thiếu, dòng 1).
TRANSCRIPT_FEATURES = frozenset(
    {
        "n_words",
        "words_per_sec",
        "mean_word_len",
        "ttr",
        "log_uniq",
        "asr_conf_mean",
        "asr_conf_geo",
        "vad_articulation_rate",
    }
)
_NOT_COMPUTABLE: Measure = (None, ReasonCode.FEATURE_NOT_COMPUTABLE)


class FeatureConfigError(ValueError):
    """`feature_order` có tên không có công thức trong catalogue."""


class VadEngine(Protocol):
    name: str
    version: str
    threshold: float
    min_silence_ms: int

    def segments(self, samples: Any, sample_rate_hz: int) -> list[tuple[float, float]]: ...


class FeatureExtractor:
    def __init__(
        self,
        feature_order: Sequence[str],
        model_feature_version: str,
        trained_with: Mapping[str, Any],
        vad: VadEngine | None,
    ) -> None:
        unknown = [n for n in feature_order if n not in UNITS]
        if unknown:
            raise FeatureConfigError(f"không có công thức cho đặc trưng: {unknown}")
        self._order = tuple(feature_order)
        self._model_feature_version = model_feature_version
        self._trained_with = dict(trained_with)
        self._vad = vad

    @classmethod
    def from_artifact(cls, artifact: Any, vad: VadEngine | None) -> FeatureExtractor:
        """Dùng `ModelArtifact` của M05 (feature_order, feature_version, trained_with)."""
        return cls(artifact.feature_order, artifact.feature_version, artifact.trained_with, vad)

    def extract(self, transcript: Transcript, audio: DecodedAudio) -> FeatureSet:
        duration = audio.duration_s
        measures = self._measure(transcript, audio, duration)
        values = tuple(
            self._value(name, measures.get(name, _NOT_COMPUTABLE)) for name in self._order
        )
        fs = FeatureSet(
            response_id=transcript.response_id,
            values=values,
            feature_version=FEATURE_VERSION,
            vad_name=self._vad.name if self._vad else None,
            vad_version=self._vad.version if self._vad else None,
            vad_threshold=self._vad.threshold if self._vad else None,
            vad_min_silence_ms=self._vad.min_silence_ms if self._vad else None,
            asr_model=transcript.asr_model,
            transcript_ref=transcript.response_id,
            audio_sha256=audio.audio_sha256,
            reasons=self._consistency_reasons(),
        )
        missing = [v.name for v in fs.values if v.value is None]
        log.info(
            "features response_id=%s missing=%s reasons=%s",
            fs.response_id,
            ",".join(missing) or "-",
            ",".join(r.value for r in fs.reasons) or "-",
        )
        return fs

    def _measure(
        self, transcript: Transcript, audio: DecodedAudio, duration: float
    ) -> dict[str, Measure]:
        if not duration > 0:  # bắt cả D ≤ 0 và NaN
            return {}
        measures: dict[str, Measure] = {"total_dur": (duration, None)}
        transcript_ok = transcript.status is AsrStatus.OK
        n_words: int | None = None
        if transcript_ok:
            measures.update(text_features(transcript.words, duration))
            n_words = len(normalize_tokens(transcript.words))
        segments = self._segments(audio)
        if segments is None:
            measures.update(dict.fromkeys(VAD_FEATURES, _NOT_COMPUTABLE))
        else:
            measures.update(pause_features(segments, duration, n_words))
        if not transcript_ok:
            for name in TRANSCRIPT_FEATURES:
                measures[name] = _NOT_COMPUTABLE
        return measures

    def _segments(self, audio: DecodedAudio) -> list[tuple[float, float]] | None:
        """None khi không có VAD hoặc VAD lỗi — không dùng VAD dự phòng."""
        if self._vad is None:
            return None
        try:
            return list(self._vad.segments(audio.samples, audio.sample_rate_hz))
        except Exception:
            log.exception("VAD %s lỗi", self._vad.name)
            return None

    def _value(self, name: str, measure: Measure) -> FeatureValue:
        value, reason = measure
        if value is not None and not math.isfinite(value):
            value, reason = None, ReasonCode.FEATURE_NOT_COMPUTABLE
        return FeatureValue(name=name, value=value, unit=UNITS[name], missing_reason=reason)

    def _consistency_reasons(self) -> tuple[ReasonCode, ...]:
        reasons: list[ReasonCode] = []
        if self._model_feature_version != FEATURE_VERSION:
            reasons.append(ReasonCode.FEATURE_VERSION_MISMATCH)
        tw = self._trained_with
        vad = self._vad
        pairs = (
            ("vad_name", vad.name if vad else None),
            ("vad_threshold", vad.threshold if vad else None),
            ("vad_min_silence_ms", vad.min_silence_ms if vad else None),
        )
        if any(key in tw and value != tw[key] for key, value in pairs):
            reasons.append(ReasonCode.VAD_VERSION_MISMATCH)
        return tuple(reasons)
