import logging

import pytest
from tests.features.fixtures import (
    EXPECTED_TEXT,
    EXPECTED_VAD,
    TRAINED_WITH,
    FakeVad,
    make_audio,
    make_transcript,
    make_words,
)

from aicefr.contracts import AsrStatus, ReasonCode
from aicefr.features.extractor import (
    FEATURE_VERSION,
    TRANSCRIPT_FEATURES,
    UNITS,
    FeatureConfigError,
    FeatureExtractor,
)
from aicefr.scoring.artifact import load_artifact


def extractor(order, vad=None, version="v3", trained=TRAINED_WITH):
    return FeatureExtractor(order, version, trained, FakeVad() if vad is None else vad)


def test_full_fixture_gives_18_values_with_units(feature_order_v2):
    """M04-TEST-001 qua extractor: 18 giá trị đúng bảng, có unit, không missing."""
    fs = extractor(feature_order_v2).extract(make_transcript(), make_audio())
    expected = EXPECTED_TEXT | EXPECTED_VAD | {"total_dur": 11.0}
    for v in fs.values:
        assert v.value == pytest.approx(expected[v.name], abs=1e-6), v.name
        assert v.unit == UNITS[v.name] and v.missing_reason is None
    assert fs.reasons == () and fs.feature_version == FEATURE_VERSION


def test_unreliable_transcript_nulls_transcript_features_only(feature_order_v2):
    """M04-TEST-004 + 011: vẫn đủ 18 tên đúng vị trí."""
    fs = extractor(feature_order_v2).extract(
        make_transcript(status=AsrStatus.UNRELIABLE), make_audio()
    )
    assert fs.names() == feature_order_v2
    for v in fs.values:
        if v.name in TRANSCRIPT_FEATURES:
            assert v.value is None and v.missing_reason is ReasonCode.FEATURE_NOT_COMPUTABLE
        else:
            assert v.value is not None, v.name


def test_zero_duration_nulls_all_18(feature_order_v2):
    """M04-TEST-008 (D = 0; contract DecodedAudio đã chặn D < 0)."""
    fs = extractor(feature_order_v2).extract(make_transcript(), make_audio(duration=0.0))
    assert len(fs.values) == 18
    assert all(v.value is None for v in fs.values)
    assert all(v.missing_reason is ReasonCode.FEATURE_NOT_COMPUTABLE for v in fs.values)


def test_nan_becomes_none_with_reason(feature_order_v2):
    """M04-TEST-009."""
    vad = FakeVad(segments=[(float("nan"), 3.0), (3.4, 6.0)])
    fs = extractor(feature_order_v2, vad).extract(make_transcript(), make_audio())
    onset = next(v for v in fs.values if v.name == "vad_onset_delay")
    assert onset.value is None and onset.missing_reason is ReasonCode.FEATURE_NOT_COMPUTABLE


def test_order_follows_real_artifact_without_filler_ratio(real_artifact_order):
    """M04-TEST-010 (ART-REAL; regression REF-05)."""
    fs = extractor(real_artifact_order).extract(make_transcript(), make_audio())
    assert fs.names() == real_artifact_order
    assert "filler_ratio" not in fs.names() and len(fs.values) == 18


def test_from_artifact_uses_artifact_order(write_fake_artifact, feature_order_v2):
    art = write_fake_artifact(feature_order_v2)
    fx = FeatureExtractor.from_artifact(art, FakeVad())
    assert fx.extract(make_transcript(), make_audio()).names() == feature_order_v2


def test_unknown_feature_name_is_config_error():
    """M04-TEST-012."""
    with pytest.raises(FeatureConfigError, match="foo_bar"):
        extractor(("n_words", "foo_bar"))


def test_model_feature_version_mismatch_is_flagged(feature_order_v2):
    """M04-TEST-013."""
    fs = extractor(feature_order_v2, version="v4").extract(make_transcript(), make_audio())
    assert fs.reasons == (ReasonCode.FEATURE_VERSION_MISMATCH,)


def test_silero_parameters_recorded_without_mismatch(feature_order_v2):
    """M04-TEST-014."""
    fs = extractor(feature_order_v2).extract(make_transcript(), make_audio())
    assert (fs.vad_name, fs.vad_version, fs.vad_threshold, fs.vad_min_silence_ms) == (
        "silero",
        "6.2.1",
        0.5,
        150,
    )
    assert ReasonCode.VAD_VERSION_MISMATCH not in fs.reasons


@pytest.mark.parametrize(
    "vad",
    [FakeVad(name="energy"), FakeVad(threshold=0.6), FakeVad(min_silence_ms=200)],
    ids=["name", "threshold", "min_silence"],
)
def test_other_vad_configuration_is_flagged(feature_order_v2, vad):
    """M04-TEST-015."""
    fs = extractor(feature_order_v2, vad).extract(make_transcript(), make_audio())
    assert fs.reasons == (ReasonCode.VAD_VERSION_MISMATCH,)


def test_failing_vad_nulls_vad_features_without_fallback(feature_order_v2):
    vad = FakeVad(fail=True)
    fs = extractor(feature_order_v2, vad).extract(make_transcript(), make_audio())
    vad_values = [v for v in fs.values if v.name.startswith("vad_")]
    assert vad.calls == 1 and all(v.value is None for v in vad_values)
    assert fs.vad_name == "silero"  # không đổi sang VAD khác


def test_missing_vad_nulls_vad_features(feature_order_v2):
    fx = FeatureExtractor(feature_order_v2, "v3", TRAINED_WITH, None)
    fs = fx.extract(make_transcript(), make_audio())
    assert fs.vad_name is None and ReasonCode.VAD_VERSION_MISMATCH in fs.reasons
    assert all(v.value is None for v in fs.values if v.name.startswith("vad_"))


def test_feature_set_and_log_do_not_leak_transcript(feature_order_v2, caplog):
    """M04-TEST-017."""
    words = make_words(["SECRET-NAME-123"] + [f"w{i}" for i in range(11)])
    tr = make_transcript(words=words, text="SECRET-NAME-123 w0 w1")
    with caplog.at_level(logging.INFO, logger="aicefr.features.extractor"):
        fs = extractor(feature_order_v2).extract(tr, make_audio())
    assert "SECRET-NAME-123" not in fs.model_dump_json()
    assert "SECRET-NAME-123" not in caplog.text and "response_id=r1" in caplog.text


def test_extraction_is_deterministic_and_unrounded(feature_order_v2):
    """M04-TEST-018."""
    fx = extractor(feature_order_v2)
    a, b = (fx.extract(make_transcript(), make_audio()) for _ in range(2))
    assert a == b
    rate = next(v.value for v in a.values if v.name == "words_per_sec")
    assert rate == 14 / 11.0


@pytest.fixture
def real_artifact_order(real_artifact_path):
    return load_artifact(real_artifact_path).feature_order
