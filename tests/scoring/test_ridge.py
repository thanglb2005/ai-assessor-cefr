import pytest

from aicefr.contracts import Band
from aicefr.scoring.artifact import load_artifact
from aicefr.scoring.ridge import near_boundary, ood_detail, predict, to_band

THRESHOLDS = {"A2_B1": 2.75, "B1_B2": 3.75}


@pytest.fixture
def fake(write_fake):
    def _load(**overrides):
        path, sha = write_fake(**overrides)
        return load_artifact(path, expected_sha256=sha)

    return _load


def _mean_values(art):
    return dict(zip(art.feature_order, art.mean, strict=True))


def test_total_dur_just_below_accepted_high_is_not_ood(real_artifact):
    """M05-TEST-015: 77,78 s nằm trong khoảng chấp nhận."""
    values = _mean_values(real_artifact) | {"total_dur": 77.78}
    assert ood_detail(values, real_artifact) == []


def test_total_dur_above_accepted_high_is_ood_with_detail(real_artifact):
    """M05-TEST-015: 80,0 s vượt khoảng chấp nhận ≈ 77,780 s."""
    values = _mean_values(real_artifact) | {"total_dur": 80.0}
    [finding] = ood_detail(values, real_artifact)
    assert finding.feature == "total_dur"
    assert finding.too == "high"
    assert finding.accepted_high == pytest.approx(77.780, abs=1e-3)


def test_ood_detail_reports_low_side_and_skips_none_and_zero_span(fake):
    art = fake(feature_lo=[0.0, 5.0], feature_hi=[1.0, 5.0])
    findings = ood_detail({"a": -0.6, "b": 100.0}, art)
    assert [(f.feature, f.too) for f in findings] == [("a", "low")]
    assert ood_detail({"a": None, "b": 100.0}, art) == []


@pytest.mark.parametrize(
    ("score", "band"),
    [(2.7499, Band.A2), (2.75, Band.B1), (3.7499, Band.B1), (3.75, Band.B2)],
)
def test_to_band_boundaries(score, band):
    """M05-TEST-016."""
    assert to_band(score, THRESHOLDS) is band


@pytest.mark.parametrize(
    ("score", "near"), [(2.25, True), (2.2499, False), (4.25, True), (4.2501, False)]
)
def test_near_boundary_with_margin_half(score, near):
    """M05-TEST-017."""
    assert near_boundary(score, THRESHOLDS, 0.5) is near


@pytest.mark.parametrize(("a", "b", "expected"), [(2.1, 2.1, 6.0), (-1.3, -1.3, 1.0)])
def test_predict_clips_to_score_range(fake, a, b, expected):
    """M05-TEST-018: raw 7,2 → 6,0; raw 0,4 → 1,0."""
    assert predict({"a": a, "b": b}, fake()) == pytest.approx(expected)


def test_predict_uses_one_when_scale_is_zero(fake):
    """M05-TEST-019: scale 0 được thay bằng 1, không chia 0."""
    art = fake(scale=[0.0, 1.0], mean=[0.5, 0.0])
    assert predict({"a": 1.0, "b": 0.0}, art) == pytest.approx(3.5)


def test_predict_rejects_missing_value(fake):
    with pytest.raises(ValueError, match="b"):
        predict({"a": 0.0, "b": None}, fake())


def test_predict_on_training_mean_returns_intercept(real_artifact):
    assert predict(_mean_values(real_artifact), real_artifact) == pytest.approx(
        real_artifact.intercept
    )
