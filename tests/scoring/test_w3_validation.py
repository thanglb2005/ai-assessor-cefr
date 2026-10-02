import pytest
from tests.scoring.test_scorer import make_fs, make_transcript, scorer_for, vec

from aicefr.contracts import AssessmentStatus, ReasonCode
from aicefr.scoring.artifact import ModelArtifactError, load_artifact
from aicefr.scoring.scorer import RidgeScorer


@pytest.fixture
def mid(fake18):
    return {name: 0.5 for name in fake18.feature_order}


@pytest.mark.parametrize(
    "override",
    [
        {"mean": [float("nan"), 0]},
        {"coef": [float("inf"), 1]},
        {"feature_order": ["a", "a"]},
        {"feature_order": ["", "b"]},
        {"band_thresholds": {"A2_B1": 3.5, "B1_B2": 3.0}},
        {"band_thresholds": {"A2_B1": 0, "B1_B2": 3.5}},
        {"intercept": float("nan")},
        {"ood_tolerance": float("inf")},
        {"boundary_margin": -1},
    ],
)
def test_invalid_artifact_values_fail_closed(write_fake, override):
    path, digest = write_fake(**override)
    with pytest.raises(ModelArtifactError) as err:
        load_artifact(path, expected_sha256=digest)
    assert err.value.reason is ReasonCode.MODEL_ARTIFACT_INVALID


def test_duplicate_feature_vector_is_refused_without_score(fake18, mid):
    fs = make_fs(fake18.feature_order, mid)
    duplicate = fs.model_copy(update={"values": (*fs.values, fs.values[0])})
    transcript = make_transcript().model_copy(update={"test_only": False})
    result = scorer_for(fake18).score(duplicate, transcript)
    assert result.status is AssessmentStatus.NOT_EVALUATED
    assert result.overall_score is None
    assert result.reasons == (ReasonCode.FEATURE_VERSION_MISMATCH,)


def test_nonfinite_feature_vector_is_refused(fake18):
    result = scorer_for(fake18).score(
        make_fs(
            fake18.feature_order,
            vec(fake18, "mean") | {fake18.feature_order[0]: float("nan")},
        ),
        make_transcript().model_copy(update={"test_only": False}),
    )
    assert result.status is AssessmentStatus.NOT_EVALUATED and result.overall_score is None
    assert result.reasons == (ReasonCode.FEATURE_NOT_COMPUTABLE,)


def test_zero_scale_artifact_refused_by_scorer(write_fake):
    path, digest = write_fake(scale=[0, 1])
    artifact = load_artifact(path, expected_sha256=digest)
    features = make_fs(artifact.feature_order, {"a": 0.5, "b": 0.5})
    result = RidgeScorer(artifact=artifact).score(
        features, make_transcript().model_copy(update={"test_only": False})
    )
    assert result.status is AssessmentStatus.NOT_EVALUATED
    assert result.reasons == (ReasonCode.MODEL_ARTIFACT_INVALID,)
    assert result.overall_score is None
