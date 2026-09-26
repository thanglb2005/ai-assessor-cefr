import math

import pytest
from tests.features.fixtures import (
    EXPECTED_TEXT,
    EXPECTED_VAD,
    FX_DURATION,
    FX_SEGMENTS,
    make_words,
)

from aicefr.contracts import ReasonCode
from aicefr.features.pauses import VAD_FEATURES, pause_features
from aicefr.features.text import normalize_tokens, text_features


def test_text_features_match_expected_table(fx_words):
    """M04-TEST-001 (phần text): khớp bảng kỳ vọng với sai số 1e-6."""
    got = text_features(fx_words, FX_DURATION)
    for name, expected in EXPECTED_TEXT.items():
        value, reason = got[name]
        assert value == pytest.approx(expected, abs=1e-6), name
        assert reason is None


def test_pause_features_match_expected_table():
    """M04-TEST-001 (phần VAD): tail 1,0 s được tính và không phải ngừng dài."""
    got = pause_features(FX_SEGMENTS, FX_DURATION, n_words=14)
    for name, expected in EXPECTED_VAD.items():
        value, reason = got[name]
        assert value == pytest.approx(expected, abs=1e-6), name
        assert reason is None


def test_filler_is_counted_and_punctuation_stripped(fx_words):
    tokens = normalize_tokens(fx_words)
    assert tokens[0] == "um" and tokens[7] == "nice" and len(tokens) == 14


def test_gap_and_tail_of_exactly_030_s_are_not_pauses():
    """M04-TEST-002: điều kiện là > 0,30 s."""
    got = pause_features([(0.0, 1.0), (1.3, 2.0)], 2.3, n_words=5)
    assert got["vad_pause_per_min"] == (0.0, None)


def test_no_pause_gives_measured_zero_not_missing():
    """M04-TEST-003: P rỗng → 0 là giá trị đo thật, không có missing_reason."""
    got = pause_features([(0.2, 9.9)], 10.0, n_words=20)
    for name in ("vad_mean_pause", "vad_long_pause_ratio", "vad_pause_sd"):
        assert got[name] == (0.0, None)


@pytest.mark.parametrize(("count", "missing"), [(9, True), (10, False)])
def test_lexical_features_need_ten_tokens(count, missing):
    """M04-TEST-005."""
    got = text_features(make_words([f"w{i}" for i in range(count)]), 10.0)
    for name in ("mean_word_len", "ttr", "log_uniq"):
        value, reason = got[name]
        if missing:
            assert value is None and reason is ReasonCode.TOO_FEW_WORDS
        else:
            assert value is not None and reason is None


def test_no_probability_gives_missing_confidence_not_zero():
    """M04-TEST-006."""
    got = text_features(make_words(["a"] * 12, [None] * 12), 10.0)
    for name in ("asr_conf_mean", "asr_conf_geo"):
        assert got[name] == (None, ReasonCode.FEATURE_NOT_COMPUTABLE)


def test_empty_segments_give_missing_vad_features_not_zero():
    """M04-TEST-007 (regression REF-04: trước đây ra 0.0)."""
    got = pause_features([], 10.0, n_words=20)
    assert set(got) == set(VAD_FEATURES)
    assert all(v == (None, ReasonCode.FEATURE_NOT_COMPUTABLE) for v in got.values())


def test_articulation_missing_without_word_count():
    got = pause_features(FX_SEGMENTS, FX_DURATION, n_words=None)
    assert got["vad_articulation_rate"] == (None, ReasonCode.FEATURE_NOT_COMPUTABLE)
    assert got["vad_speech_sec"][0] == pytest.approx(7.6)


def test_nan_timestamp_propagates_only_to_affected_features():
    """M04-TEST-009 (điều chỉnh): contract Word chặn prob NaN, nên đưa NaN qua segment VAD."""
    got = pause_features([(math.nan, 3.0), (3.4, 6.0)], 11.0, n_words=14)
    assert math.isnan(got["vad_onset_delay"][0])  # extractor đổi thành None (test_extractor)
    assert got["vad_n_seg_per_min"][0] == pytest.approx(2 / (11 / 60))
