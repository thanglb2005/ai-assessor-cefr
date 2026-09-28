"""M02-TEST-003: sample-level measurements and shared contract."""

from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError
from tests.audio.test_decoder import config

from aicefr.contracts import DecodedAudio, QCMeasurement, ReasonCode
from aicefr.qc.measurements import measure_audio, missing_measurements


def test_measurements_have_exact_values_and_units() -> None:
    samples = np.array([0.0, 0.01, 0.2, -0.99], dtype=np.float32)
    audio = DecodedAudio(samples=samples, sample_rate_hz=16_000, duration_s=4 / 16_000,
                         audio_sha256="synthetic")
    by_name = {item.name: item for item in measure_audio(audio, config())}
    assert by_name["duration_s"].value == pytest.approx(4 / 16_000)
    assert by_name["duration_s"].unit == "s"
    assert by_name["silence_ratio"].value == 0.5
    assert by_name["clipped_ratio"].value == 0.25
    assert by_name["silence_ratio"].unit == "ratio"
    assert all(item.missing_reason is None for item in by_name.values())


def test_missing_measurement_has_reason_and_invalid_contract_rejected() -> None:
    missing = missing_measurements(ReasonCode.QC_DECODE_FAILED)
    assert len(missing) == 3
    assert all(
        item.value is None and item.missing_reason is ReasonCode.QC_DECODE_FAILED
        for item in missing
    )
    with pytest.raises(ValidationError):
        QCMeasurement(name="duration_s", value=None, unit="s")
    with pytest.raises(ValidationError):
        QCMeasurement(name="duration_s", value=float("nan"), unit="s")
    with pytest.raises(ValidationError):
        DecodedAudio(samples=np.array([float("nan")], dtype=np.float32), sample_rate_hz=16_000,
                     duration_s=1 / 16_000, audio_sha256="synthetic")
