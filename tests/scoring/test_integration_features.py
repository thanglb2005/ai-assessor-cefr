"""M05-TASK-004 / M05-TEST-022: FeatureSet do extractor M04 dựng đi thẳng vào scorer M05.

Kiểm hợp đồng M04 → M05 (tên, thứ tự, provenance), không kiểm điểm. Bản ART-REAL
chỉ chạy khi có artifact ngoài repo; hai bản ART-FAKE chạy trên CI để hợp đồng
vẫn được kiểm ở mọi PR.
"""

import pytest
from tests.features.fixtures import (
    EXPECTED_TEXT,
    TRAINED_WITH,
    FakeVad,
    make_audio,
    make_transcript,
)

from aicefr.contracts import AssessmentStatus, Band, ReasonCode
from aicefr.features.extractor import FeatureExtractor
from aicefr.scoring.scorer import RidgeScorer

FIXED_CLOCK = "2026-10-03T00:00:00+00:00"


def run_chain(artifact, vad):
    """M04 dựng FeatureSet từ đúng artifact mà M05 dùng, rồi M05 chấm."""
    transcript = make_transcript()
    features = FeatureExtractor.from_artifact(artifact, vad).extract(transcript, make_audio())
    assessment = RidgeScorer(artifact=artifact, clock=lambda: FIXED_CLOCK).score(
        features, transcript
    )
    return features, assessment


def test_fixture_features_reach_the_real_model_and_only_log_uniq_is_out_of_range(real_artifact):
    """M05-TEST-022 (ART-REAL): fixture chỉ có 11 từ khác nhau nên log_uniq thấp hơn khoảng nhận."""
    features, a = run_chain(real_artifact, FakeVad())
    assert features.reasons == ()
    assert features.names() == real_artifact.feature_order
    assert a.status is AssessmentStatus.NOT_EVALUATED
    assert a.reasons == (ReasonCode.OUT_OF_DISTRIBUTION,)
    assert (a.overall_score, a.overall_band) == (None, None)
    [ood] = a.out_of_range
    assert (ood.feature, ood.too) == ("log_uniq", "low")
    assert ood.value == pytest.approx(EXPECTED_TEXT["log_uniq"], abs=1e-6)
    assert ood.value < ood.accepted_low
    assert a.provenance.model_sha256 == real_artifact.sha256


@pytest.fixture
def wide_fake18(write_fake, feature_order_v2):
    """ART-FAKE: 18 tên của Ridge v2, khoảng nhận rất rộng để chuỗi đi tới bước chấm."""
    from aicefr.scoring.artifact import load_artifact

    n = len(feature_order_v2)
    path, sha = write_fake(
        feature_order=list(feature_order_v2),
        mean=[0.0] * n,
        scale=[1.0] * n,
        coef=[0.0] * n,
        intercept=3.25,
        feature_lo=[-1e6] * n,
        feature_hi=[1e6] * n,
        boundary_margin=0.1,
        trained_with=TRAINED_WITH,
    )
    return load_artifact(path, expected_sha256=sha)


def test_extractor_output_is_accepted_by_the_scorer(wide_fake18):
    """M05-TEST-022 (biến thể CI): không lệch tên, thứ tự, provenance nên đi hết 8 bước."""
    features, a = run_chain(wide_fake18, FakeVad())
    assert features.names() == wide_fake18.feature_order
    assert all(v.value is not None for v in features.values)
    assert a.status is AssessmentStatus.ESTIMATED
    assert (a.overall_score, a.overall_band) == (pytest.approx(3.25), Band.B1)
    assert a.reasons == () and a.out_of_range == ()


def test_vad_setting_mismatch_travels_from_m04_to_m05(wide_fake18):
    """M05-TEST-022 (biến thể CI): VAD khác cấu hình huấn luyện thì M05 từ chối chấm."""
    features, a = run_chain(wide_fake18, FakeVad(threshold=0.3))
    assert ReasonCode.VAD_VERSION_MISMATCH in features.reasons
    assert a.status is AssessmentStatus.NOT_EVALUATED
    assert a.reasons == (ReasonCode.VAD_VERSION_MISMATCH,)
    assert a.overall_score is None
