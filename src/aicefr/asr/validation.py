"""Kiểm timestamp của word (M03 Spec v0.2, bảng lỗi dòng 2)."""

from __future__ import annotations

from collections.abc import Sequence

from aicefr.contracts import Word


def timestamp_problem(words: Sequence[Word], duration_s: float) -> str | None:
    """Mô tả lỗi đầu tiên, hoặc None nếu timestamp hợp lệ."""
    previous_start = 0.0
    for i, w in enumerate(words):
        if w.start_s < 0:
            return f"word {i}: start âm"
        if w.end_s < w.start_s:
            return f"word {i}: end trước start"
        if w.start_s < previous_start:
            return f"word {i}: bắt đầu trước word trước"
        if w.end_s > duration_s:
            return f"word {i}: vượt độ dài audio"
        previous_start = w.start_s
    return None
