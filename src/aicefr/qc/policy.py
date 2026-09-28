"""Versioned QC policy over deterministic M02 measurements."""

from __future__ import annotations

from aicefr.audio.config import QCConfig
from aicefr.contracts import QCResult, QCStatus, ReasonCode

_REQUIRED = frozenset({"duration_s", "silence_ratio", "clipped_ratio"})


def evaluate_qc(qc: QCResult, config: QCConfig) -> QCResult:
    """Classify provisional decoder measurements; retain structural REJECTs."""
    if qc.qc_config_version != config.version:
        raise ValueError("QCResult and QCConfig versions differ")
    if qc.status is not QCStatus.PASS:
        return qc
    values = {item.name: item.value for item in qc.measurements}
    if (
        len(qc.measurements) != len(_REQUIRED)
        or set(values) != _REQUIRED
        or any(value is None for value in values.values())
    ):
        return QCResult(
            status=QCStatus.REJECT,
            reasons=(ReasonCode.QC_MEASUREMENT_MISSING,),
            qc_config_version=config.version,
            measurements=qc.measurements,
        )
    duration = values["duration_s"]
    silence = values["silence_ratio"]
    clipping = values["clipped_ratio"]
    assert duration is not None and silence is not None and clipping is not None
    if duration < 0 or not 0 <= silence <= 1 or not 0 <= clipping <= 1:
        return QCResult(
            status=QCStatus.REJECT,
            reasons=(ReasonCode.QC_MEASUREMENT_MISSING,),
            qc_config_version=config.version,
            measurements=qc.measurements,
        )

    rejected: list[ReasonCode] = []
    review: list[ReasonCode] = []
    if duration > config.max_duration_s:
        rejected.append(ReasonCode.QC_DURATION_LIMIT)
    elif duration < config.min_duration_s:
        rejected.append(ReasonCode.QC_TOO_SHORT)
    if silence >= config.reject_silence_ratio:
        rejected.append(ReasonCode.QC_SILENCE_REJECT)
    elif silence >= config.review_silence_ratio:
        review.append(ReasonCode.QC_SILENCE_REVIEW)
    if clipping >= config.reject_clipping_ratio:
        rejected.append(ReasonCode.QC_CLIPPING_REJECT)
    elif clipping >= config.review_clipping_ratio:
        review.append(ReasonCode.QC_CLIPPING_REVIEW)
    if rejected:
        status, reasons = QCStatus.REJECT, tuple(rejected)
    elif review:
        status, reasons = QCStatus.REVIEW, tuple(review)
    else:
        status, reasons = QCStatus.PASS, ()
    return QCResult(
        status=status,
        reasons=reasons,
        qc_config_version=config.version,
        measurements=qc.measurements,
    )
