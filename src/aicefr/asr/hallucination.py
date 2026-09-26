"""Phát hiện transcript bị ASR "bịa" (M03 Spec v0.2, hành vi 6, config hallucination-v1)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from aicefr.contracts import Word

_STRIP = '.,?!;:"'


@dataclass(frozen=True)
class HallucinationConfig:
    version: str = "hallucination-v1"
    max_consecutive_repeats: int = 6  # > 6 lần liên tiếp là bất thường
    max_single_token_share: float = 0.35  # > 0,35 ...
    min_words_for_share: int = 60  # ... chỉ xét khi có ≥ 60 từ
    min_phrase_len: int = 3
    max_phrase_len: int = 10
    min_phrase_repeats: int = 3  # cụm lặp liền nhau ≥ 3 lần
    tail_low_prob: float = 0.05
    min_tail_low_prob_run: int = 5  # ≥ 5 từ cuối có prob < 0,05
    stalled_s_per_word: float = 0.05
    min_stalled_run: int = 4  # ≥ 4 từ liên tiếp dài < 0,05 s


@dataclass(frozen=True)
class HallucinationFinding:
    rule: str
    detail: str


def detect_hallucination(
    words: Sequence[Word], config: HallucinationConfig | None = None
) -> HallucinationFinding | None:
    """Luật đầu tiên khớp; None nếu không có dấu hiệu."""
    cfg = config or HallucinationConfig()
    tokens = [w.text.strip().strip(_STRIP).lower() for w in words]
    checks = (
        _consecutive_repeat(tokens, cfg),
        _token_share(tokens, cfg),
        _phrase_repeat(tokens, cfg),
        _low_prob_tail(words, cfg),
        _stalled_clock(words, cfg),
    )
    return next((c for c in checks if c is not None), None)


def _consecutive_repeat(tokens: list[str], cfg: HallucinationConfig) -> HallucinationFinding | None:
    run = 0
    for i, tok in enumerate(tokens):
        run = run + 1 if i and tok == tokens[i - 1] else 1
        if run > cfg.max_consecutive_repeats:
            return HallucinationFinding("consecutive_repeat", f"{tok!r} lặp {run} lần")
    return None


def _token_share(tokens: list[str], cfg: HallucinationConfig) -> HallucinationFinding | None:
    if len(tokens) < cfg.min_words_for_share:
        return None
    top = max(set(tokens), key=tokens.count)
    share = tokens.count(top) / len(tokens)
    if share > cfg.max_single_token_share:
        return HallucinationFinding("token_share", f"{top!r} chiếm {share:.2f}")
    return None


def _phrase_repeat(tokens: list[str], cfg: HallucinationConfig) -> HallucinationFinding | None:
    for n in range(cfg.min_phrase_len, cfg.max_phrase_len + 1):
        for start in range(len(tokens) - n * cfg.min_phrase_repeats + 1):
            phrase = tokens[start : start + n]
            repeats = 1
            while tokens[start + repeats * n : start + (repeats + 1) * n] == phrase:
                repeats += 1
            if repeats >= cfg.min_phrase_repeats:
                return HallucinationFinding("phrase_repeat", f"cụm {n} từ lặp {repeats} lần")
    return None


def _low_prob_tail(words: Sequence[Word], cfg: HallucinationConfig) -> HallucinationFinding | None:
    run = 0
    for w in reversed(words):
        if w.prob is None or w.prob >= cfg.tail_low_prob:
            break
        run += 1
    if run >= cfg.min_tail_low_prob_run:
        return HallucinationFinding("low_prob_tail", f"{run} từ cuối có prob < {cfg.tail_low_prob}")
    return None


def _stalled_clock(words: Sequence[Word], cfg: HallucinationConfig) -> HallucinationFinding | None:
    run = 0
    for w in words:
        run = run + 1 if (w.end_s - w.start_s) < cfg.stalled_s_per_word else 0
        if run >= cfg.min_stalled_run:
            return HallucinationFinding("stalled_clock", f"{run} từ liên tiếp < 0,05 s")
    return None
