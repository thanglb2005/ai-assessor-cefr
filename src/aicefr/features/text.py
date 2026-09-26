"""Đặc trưng từ transcript (M04 Spec v0.2, catalogue #1, 2, 4–8).

Thiếu dữ liệu trả `None` kèm reason, không bao giờ thay bằng 0 hay trung bình.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from aicefr.contracts import ReasonCode, Word

MIN_WORDS = 10
PROB_FLOOR = 1e-4
_STRIP = '.,?!;:"'

# (giá trị, reason khi None)
Measure = tuple[float | None, ReasonCode | None]


def normalize_tokens(words: Sequence[Word]) -> list[str]:
    """`text.strip().strip('.,?!;:"').lower()`, bỏ token rỗng. Filler vẫn được đếm."""
    tokens = (w.text.strip().strip(_STRIP).lower() for w in words)
    return [t for t in tokens if t]


def text_features(words: Sequence[Word], duration_s: float) -> dict[str, Measure]:
    tokens = normalize_tokens(words)
    n = len(tokens)
    uniq = len(set(tokens))
    few = (None, ReasonCode.TOO_FEW_WORDS)
    out: dict[str, Measure] = {
        "n_words": (float(n), None),
        "words_per_sec": (n / duration_s, None),
        "mean_word_len": (sum(len(t) for t in tokens) / n, None) if n >= MIN_WORDS else few,
        "ttr": (uniq / n, None) if n >= MIN_WORDS else few,
        "log_uniq": (math.log(uniq + 1), None) if n >= MIN_WORDS else few,
    }
    probs = [w.prob for w in words if w.prob is not None]
    if probs:
        out["asr_conf_mean"] = (sum(probs) / len(probs), None)
        geo = math.exp(sum(math.log(max(p, PROB_FLOOR)) for p in probs) / len(probs))
        out["asr_conf_geo"] = (geo, None)
    else:
        out["asr_conf_mean"] = out["asr_conf_geo"] = (None, ReasonCode.FEATURE_NOT_COMPUTABLE)
    return out
