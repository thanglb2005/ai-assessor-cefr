import pytest
from tests.asr.fixtures import WEIGHT_SMALL

from aicefr.asr.identity import asr_version_reasons, resolve_asr_model
from aicefr.asr.validation import timestamp_problem
from aicefr.contracts import ReasonCode, Word


def test_mapped_weight_resolves_to_canonical_id():
    """M03-TEST-013 (phần ánh xạ)."""
    assert resolve_asr_model(WEIGHT_SMALL) == "whisper-small"
    assert asr_version_reasons("whisper-small", "whisper-small") == ()


@pytest.mark.parametrize("weight", ["Systran/faster-whisper-small.en", "whisper-small.en", "x"])
def test_unmapped_weight_is_none_and_mismatch(weight):
    """M03-TEST-014 (regression F-04: so chuỗi con)."""
    assert resolve_asr_model(weight) is None
    assert asr_version_reasons(None, "whisper-small") == (ReasonCode.ASR_VERSION_MISMATCH,)


def test_custom_map_and_other_model_mismatch():
    """M03-TEST-015 (phần so khớp)."""
    assert resolve_asr_model("w", {"w": "whisper-medium"}) == "whisper-medium"
    assert asr_version_reasons("whisper-medium", "whisper-small") == (
        ReasonCode.ASR_VERSION_MISMATCH,
    )
    assert asr_version_reasons("whisper-medium", None) == ()


def test_unmapped_weight_is_mismatch_even_without_trained_model():
    """FINDING-07-A1-02: Spec M03 — weight không có trong bảng → null + mismatch."""
    assert asr_version_reasons(None, None) == (ReasonCode.ASR_VERSION_MISMATCH,)


def _w(start, end):
    return Word(text="a", start_s=start, end_s=end)


@pytest.mark.parametrize(
    "ws",
    [[_w(-0.1, 0.2)], [_w(0.5, 0.4)], [_w(1.0, 1.2), _w(0.8, 1.3)], [_w(0.0, 10.5)]],
    ids=["start_am", "end_truoc_start", "khong_don_dieu", "vuot_duration"],
)
def test_invalid_timestamps_are_reported(ws):
    """M03-TEST-004 (phần validator)."""
    assert timestamp_problem(ws, 10.0) is not None


def test_valid_timestamps_pass():
    assert timestamp_problem([_w(0.0, 0.3), _w(0.3, 0.6), _w(0.3, 0.7)], 10.0) is None
