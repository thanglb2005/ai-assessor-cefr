import numpy as np
import pytest
from pydantic import ValidationError

from aicefr import __version__
from aicefr.contracts import (
    Assessment,
    AssessmentStatus,
    Criterion,
    CriterionCoverage,
    DecodedAudio,
    FeatureSet,
    FeatureValue,
    Provenance,
    ReasonCode,
    Word,
)


def _feature_set() -> FeatureSet:
    return FeatureSet(
        response_id="r1",
        values=(
            FeatureValue(name="n_words", value=14.0, unit="từ"),
            FeatureValue(
                name="ttr", value=None, unit="tỷ lệ", missing_reason=ReasonCode.TOO_FEW_WORDS
            ),
        ),
        feature_version="v3",
        vad_name="silero",
        vad_version="6.2.1",
        vad_threshold=0.5,
        vad_min_silence_ms=150,
        asr_model="whisper-small",
        transcript_ref="t1",
        audio_sha256="0" * 64,
    )


def test_package_exposes_version():
    assert __version__ == "0.1.0"


def test_reason_codes_include_new_codes_requested_by_m04_m05():
    assert ReasonCode.FEATURE_VERSION_MISMATCH == "FEATURE_VERSION_MISMATCH"
    assert ReasonCode.MODEL_ARTIFACT_INVALID == "MODEL_ARTIFACT_INVALID"


def test_feature_set_keeps_missing_value_as_none_not_zero():
    fs = _feature_set()
    assert fs.names() == ("n_words", "ttr")
    assert fs.value_of("n_words") == 14.0
    assert fs.value_of("ttr") is None


def test_feature_set_value_of_unknown_name_raises():
    with pytest.raises(KeyError):
        _feature_set().value_of("filler_ratio")


def test_word_rejects_probability_outside_unit_interval():
    with pytest.raises(ValidationError):
        Word(text="hi", start_s=0.0, end_s=0.2, prob=1.5)


def test_decoded_audio_rejects_stereo_samples():
    with pytest.raises(ValidationError):
        DecodedAudio(
            samples=np.zeros((2, 10), dtype=np.float32),
            sample_rate_hz=16_000,
            duration_s=0.0,
            audio_sha256="0" * 64,
        )


def test_criterion_coverage_has_no_score_or_band_field():
    fields = set(CriterionCoverage.model_fields)
    assert "score" not in fields and "band" not in fields


def test_assessment_defaults_interaction_to_insufficient_evidence():
    a = Assessment(
        response_id="r1",
        status=AssessmentStatus.NOT_EVALUATED,
        criteria=tuple(CriterionCoverage(criterion=c) for c in Criterion),
        provenance=Provenance(
            model_version=None,
            model_sha256=None,
            feature_version=None,
            band_map_version=None,
            calibration_version=None,
            unit_of_inference=None,
            scored_at="2026-09-26T00:00:00+00:00",
        ),
    )
    assert a.interaction.level is None
    assert a.interaction.score_status == "insufficient_evidence"
    assert a.overall_score is None and a.teacher_verified is False


def test_m08_blob_and_actor_contracts_are_strict():
    from aicefr.contracts import Actor, ActorRole, BlobRef

    actor = Actor(actor_id="fixture-a", role=ActorRole.STUDENT)
    assert actor.role == ActorRole.STUDENT
    with pytest.raises(ValidationError):
        Actor(actor_id="", role=ActorRole.STUDENT)
    with pytest.raises(ValidationError):
        BlobRef(blob_id="../outside", sha256="0" * 64, size_bytes=1)
