"""M02-TEST-007: explicit policy thresholds and result provenance."""

from __future__ import annotations

import pytest
from tests.audio.test_decoder import config

from aicefr.contracts import QCMeasurement, QCResult, QCStatus, ReasonCode
from aicefr.qc.policy import evaluate_qc


def measured(duration: float = 0.1, silence: float = 0.0, clipping: float = 0.0) -> QCResult:
    return QCResult(
        status=QCStatus.PASS,
        qc_config_version="test-m02-v1",
        measurements=(
            QCMeasurement(name="duration_s", value=duration, unit="s"),
            QCMeasurement(name="silence_ratio", value=silence, unit="ratio"),
            QCMeasurement(name="clipped_ratio", value=clipping, unit="ratio"),
        ),
    )


def test_pass_review_reject_and_threshold_equality() -> None:
    passed = evaluate_qc(measured(), config())
    assert passed.status is QCStatus.PASS and passed.reasons == ()
    assert passed.qc_config_version == "test-m02-v1"
    provisional = measured(silence=0.5, clipping=0.3)
    reviewed = evaluate_qc(provisional, config())
    assert reviewed.status is QCStatus.REVIEW
    assert reviewed.reasons == (ReasonCode.QC_SILENCE_REVIEW, ReasonCode.QC_CLIPPING_REVIEW)
    assert reviewed.measurements == provisional.measurements
    rejected = evaluate_qc(measured(silence=0.9, clipping=0.6), config())
    assert rejected.status is QCStatus.REJECT
    assert rejected.reasons == (ReasonCode.QC_SILENCE_REJECT, ReasonCode.QC_CLIPPING_REJECT)


def test_duration_limits_and_reject_precedence() -> None:
    assert evaluate_qc(measured(duration=0.005), config()).reasons == (ReasonCode.QC_TOO_SHORT,)
    assert evaluate_qc(measured(duration=1.1), config()).reasons == (ReasonCode.QC_DURATION_LIMIT,)
    result = evaluate_qc(measured(duration=0.005, silence=0.5, clipping=0.6), config())
    assert result.status is QCStatus.REJECT
    assert result.reasons == (ReasonCode.QC_TOO_SHORT, ReasonCode.QC_CLIPPING_REJECT)


def test_structural_reject_and_missing_or_invalid_measurements() -> None:
    original = QCResult(
        status=QCStatus.REJECT,
        qc_config_version="test-m02-v1",
        reasons=(ReasonCode.QC_DECODE_FAILED,),
    )
    assert evaluate_qc(original, config()) is original
    missing = QCResult(status=QCStatus.PASS, qc_config_version="test-m02-v1")
    assert evaluate_qc(missing, config()).reasons == (ReasonCode.QC_MEASUREMENT_MISSING,)
    null = QCResult(
        status=QCStatus.PASS,
        qc_config_version="test-m02-v1",
        measurements=(QCMeasurement(name="duration_s", value=None, unit="s",
                                     missing_reason=ReasonCode.QC_DECODE_FAILED),),
    )
    assert evaluate_qc(null, config()).status is QCStatus.REJECT
    invalid = evaluate_qc(measured(silence=1.2), config())
    assert invalid.reasons == (ReasonCode.QC_MEASUREMENT_MISSING,)
    with pytest.raises(ValueError, match="versions differ"):
        evaluate_qc(measured(), config(version="another-version"))
