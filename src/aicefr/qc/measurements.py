"""Deterministic M02 measurements on normalized mono PCM."""

from __future__ import annotations

import numpy as np

from aicefr.audio.config import QCConfig
from aicefr.contracts import DecodedAudio, QCMeasurement, ReasonCode

_MEASUREMENT_UNITS = (
    ("duration_s", "s"),
    ("silence_ratio", "ratio"),
    ("clipped_ratio", "ratio"),
)


def missing_measurements(reason: ReasonCode) -> tuple[QCMeasurement, ...]:
    """Represent unavailable measurements as null plus a stable reason."""
    return tuple(
        QCMeasurement(name=name, value=None, unit=unit, missing_reason=reason)
        for name, unit in _MEASUREMENT_UNITS
    )


def measure_audio(audio: DecodedAudio, config: QCConfig) -> tuple[QCMeasurement, ...]:
    """Measure the post-resample signal, using sample-level inclusive comparisons."""
    samples = audio.samples
    if samples.size == 0:
        return missing_measurements(ReasonCode.QC_EMPTY_AUDIO)
    magnitude = np.abs(samples)
    duration_s = float(samples.size / audio.sample_rate_hz)
    silence_ratio = float(np.count_nonzero(magnitude <= config.silence_threshold) / samples.size)
    clipped_ratio = float(np.count_nonzero(magnitude >= config.clipping_threshold) / samples.size)
    return (
        QCMeasurement(name="duration_s", value=duration_s, unit="s"),
        QCMeasurement(name="silence_ratio", value=silence_ratio, unit="ratio"),
        QCMeasurement(name="clipped_ratio", value=clipped_ratio, unit="ratio"),
    )
