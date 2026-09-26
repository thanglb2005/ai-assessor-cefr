"""Identifier chuẩn của model ASR (M03-FR-003).

`asr_model` là identifier chuẩn, không phải tên repo weight. Ánh xạ tường minh
và so bằng `==`: `whisper-small.en` là model khác, không được coi là `whisper-small`.
"""

from __future__ import annotations

from collections.abc import Mapping

from aicefr.contracts import ReasonCode

# Weight đã tải có chủ đích (evidence M03-EV-001) → identifier chuẩn.
DEFAULT_WEIGHT_MAP: Mapping[str, str] = {
    "Systran/faster-whisper-small": "whisper-small",
}


def resolve_asr_model(weight_name: str, weight_map: Mapping[str, str] | None = None) -> str | None:
    """Identifier chuẩn của weight, hoặc None nếu weight không có trong bảng."""
    return (DEFAULT_WEIGHT_MAP if weight_map is None else weight_map).get(weight_name)


def asr_version_reasons(
    asr_model: str | None, trained_asr_model: str | None
) -> tuple[ReasonCode, ...]:
    """`ASR_VERSION_MISMATCH` khi weight không có trong bảng ánh xạ, hoặc identifier
    không khớp đúng model scoring đã học."""
    if asr_model is None:
        return (ReasonCode.ASR_VERSION_MISMATCH,)
    if trained_asr_model is None:
        return ()
    return () if asr_model == trained_asr_model else (ReasonCode.ASR_VERSION_MISMATCH,)
