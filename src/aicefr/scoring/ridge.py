"""Toán chấm của Ridge (M05 Spec v0.2, bước 6–8).

Mọi con số (mean, scale, coef, intercept, ngưỡng, margin, ood_tolerance) đọc từ
artifact; module này không giữ bản sao nào.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from aicefr.contracts import Band
from aicefr.scoring.artifact import ModelArtifact

SCORE_MIN, SCORE_MAX = 1.0, 6.0


@dataclass(frozen=True)
class OodFinding:
    feature: str
    value: float
    trained_low: float
    trained_high: float
    accepted_low: float
    accepted_high: float
    too: str  # "low" | "high"


def ood_detail(values: Mapping[str, float | None], artifact: ModelArtifact) -> list[OodFinding]:
    """Đặc trưng nằm ngoài [lo − tol·span ; hi + tol·span]. Bỏ qua giá trị None và span ≤ 0."""
    tol = artifact.ood_tolerance
    findings: list[OodFinding] = []
    for name, lo, hi in zip(
        artifact.feature_order, artifact.feature_lo, artifact.feature_hi, strict=True
    ):
        value = values.get(name)
        span = hi - lo
        if value is None or span <= 0:
            continue
        low, high = lo - tol * span, hi + tol * span
        if value < low or value > high:
            findings.append(
                OodFinding(name, value, lo, hi, low, high, "low" if value < low else "high")
            )
    return findings


def predict(values: Mapping[str, float | None], artifact: ModelArtifact) -> float:
    """Điểm overall trong [1,0 ; 6,0]. Gọi sau khi đã kiểm không đặc trưng nào None."""
    raw = artifact.intercept
    for name, mean, scale, coef in zip(
        artifact.feature_order, artifact.mean, artifact.scale, artifact.coef, strict=True
    ):
        value = values.get(name)
        if value is None:
            raise ValueError(f"thiếu giá trị đặc trưng {name}")
        raw += coef * (value - mean) / (scale or 1.0)
    return min(max(raw, SCORE_MIN), SCORE_MAX)


def to_band(score: float, thresholds: Mapping[str, float]) -> Band:
    if score < thresholds["A2_B1"]:
        return Band.A2
    if score < thresholds["B1_B2"]:
        return Band.B1
    return Band.B2


def near_boundary(score: float, thresholds: Mapping[str, float], margin: float) -> bool:
    return any(abs(score - t) <= margin for t in thresholds.values())
