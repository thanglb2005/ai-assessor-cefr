"""Coverage năm tiêu chí (M05 Spec v0.2, REF-06).

Bảng gán là giải thích, không phải thang đo đã thẩm định học thuật. Chỉ tính
trên đặc trưng có trong `feature_order` của model (không còn `filler_ratio`).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from aicefr.contracts import Criterion, CriterionCoverage, ReasonCode

CRITERION_FEATURES: dict[Criterion, tuple[str, ...]] = {
    Criterion.RANGE: ("log_uniq", "ttr", "mean_word_len"),
    Criterion.ACCURACY: ("asr_conf_mean", "asr_conf_geo"),
    Criterion.FLUENCY: (
        "words_per_sec",
        "vad_articulation_rate",
        "vad_mean_pause",
        "vad_pause_per_min",
        "vad_long_pause_ratio",
    ),
    Criterion.COHERENCE: ("n_words", "vad_mean_seg_len", "total_dur"),
    Criterion.PHONOLOGY: ("asr_conf_mean", "vad_silence_ratio"),
}


def criterion_coverage(
    values: Mapping[str, float | None], feature_order: Iterable[str]
) -> tuple[CriterionCoverage, ...]:
    """coverage = số đặc trưng liên quan khác None / số đặc trưng liên quan, làm tròn 2 số."""
    order = set(feature_order)
    rows: list[CriterionCoverage] = []
    for criterion, related in CRITERION_FEATURES.items():
        feats = tuple(f for f in related if f in order)
        if not feats:
            rows.append(
                CriterionCoverage(criterion=criterion, reasons=(ReasonCode.FEATURE_NOT_COMPUTABLE,))
            )
            continue
        present = sum(values.get(f) is not None for f in feats)
        coverage = round(present / len(feats), 2)
        reasons = () if present == len(feats) else (ReasonCode.FEATURE_NOT_COMPUTABLE,)
        rows.append(
            CriterionCoverage(
                criterion=criterion, coverage=coverage, features=feats, reasons=reasons
            )
        )
    return tuple(rows)


def not_evaluated_coverage(reasons: tuple[ReasonCode, ...]) -> tuple[CriterionCoverage, ...]:
    """Khi Assessment là NOT_EVALUATED: coverage None, mang reason của Assessment."""
    return tuple(CriterionCoverage(criterion=c, reasons=reasons) for c in CRITERION_FEATURES)
