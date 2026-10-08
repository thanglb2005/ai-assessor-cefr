"""Explicit, versioned limits for M02 audio decoding and QC."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum


class AudioFormat(StrEnum):
    WAV_PCM = "wav"
    FLAC = "flac"
    OGG_VORBIS = "ogg"
    MP3 = "mp3"
    WEBM = "webm"
    MP4 = "mp4"


@dataclass(frozen=True, slots=True)
class QCConfig:
    """All policy values are required; fixture values are not product defaults."""

    version: str
    accepted_formats: tuple[AudioFormat, ...]
    max_input_bytes: int
    min_duration_s: float
    max_duration_s: float
    max_input_sample_rate_hz: int
    silence_threshold: float
    clipping_threshold: float
    review_silence_ratio: float
    reject_silence_ratio: float
    review_clipping_ratio: float
    reject_clipping_ratio: float

    def __post_init__(self) -> None:
        if not self.version or self.version != self.version.strip():
            raise ValueError("QCConfig.version must be a nonempty, trimmed string")
        try:
            formats = tuple(AudioFormat(item) for item in self.accepted_formats)
        except ValueError as error:
            raise ValueError("QCConfig contains an unsupported format") from error
        if not formats or len(set(formats)) != len(formats):
            raise ValueError("QCConfig.accepted_formats must be nonempty and unique")
        object.__setattr__(self, "accepted_formats", formats)
        if type(self.max_input_bytes) is not int or self.max_input_bytes <= 0:
            raise ValueError("max_input_bytes must be a positive integer")
        if type(self.max_input_sample_rate_hz) is not int or self.max_input_sample_rate_hz <= 0:
            raise ValueError("max_input_sample_rate_hz must be a positive integer")
        for name in (
            "min_duration_s", "max_duration_s", "silence_threshold", "clipping_threshold",
            "review_silence_ratio", "reject_silence_ratio", "review_clipping_ratio",
            "reject_clipping_ratio",
        ):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if not 0 <= self.min_duration_s <= self.max_duration_s or self.max_duration_s == 0:
            raise ValueError("duration limits are invalid")
        if not 0 <= self.silence_threshold < self.clipping_threshold <= 1:
            raise ValueError("amplitude thresholds are invalid")
        for name in (
            "review_silence_ratio", "reject_silence_ratio", "review_clipping_ratio",
            "reject_clipping_ratio",
        ):
            if not 0 <= getattr(self, name) <= 1:
                raise ValueError(f"{name} must be a ratio")
        if self.review_silence_ratio > self.reject_silence_ratio:
            raise ValueError("silence REVIEW threshold exceeds REJECT threshold")
        if self.review_clipping_ratio > self.reject_clipping_ratio:
            raise ValueError("clipping REVIEW threshold exceeds REJECT threshold")
