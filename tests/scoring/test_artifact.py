import hashlib

import pytest

from aicefr.contracts import ReasonCode
from aicefr.scoring.artifact import (
    MODEL_DIR_ENV,
    RIDGE_RESP_V2_SHA256,
    ModelArtifactError,
    default_artifact_path,
    load_artifact,
)


def test_load_artifact_missing_file_reports_model_version_missing(tmp_path):
    """M05-TEST-005."""
    with pytest.raises(ModelArtifactError) as err:
        load_artifact(tmp_path / "ridge_resp_v2.json")
    assert err.value.reason is ReasonCode.MODEL_VERSION_MISSING


def test_load_artifact_one_byte_changed_reports_artifact_invalid(tmp_path, real_artifact_path):
    """M05-TEST-006: sửa 1 byte thì hash lệch, không fallback."""
    tampered = tmp_path / "ridge_resp_v2.json"
    data = bytearray(real_artifact_path.read_bytes())
    data[-2] = ord(" ") if data[-2] != ord(" ") else ord("\n")
    tampered.write_bytes(bytes(data))
    with pytest.raises(ModelArtifactError) as err:
        load_artifact(tampered)
    assert err.value.reason is ReasonCode.MODEL_ARTIFACT_INVALID


def test_load_artifact_hash_mismatch_on_fake_reports_artifact_invalid(write_fake):
    """M05-TEST-006 (bản chạy được trên CI, không cần artifact thật)."""
    path, _ = write_fake()
    with pytest.raises(ModelArtifactError) as err:
        load_artifact(path, expected_sha256="0" * 64)
    assert err.value.reason is ReasonCode.MODEL_ARTIFACT_INVALID


@pytest.mark.parametrize("unit", ["ca bai thi", ""])
def test_load_artifact_wrong_unit_of_inference_is_rejected(write_fake, unit):
    """M05-TEST-007: đơn vị cả bài thi hoặc để trống đều bị từ chối."""
    path, sha = write_fake(unit_of_inference=unit)
    with pytest.raises(ModelArtifactError) as err:
        load_artifact(path, expected_sha256=sha)
    assert err.value.reason is ReasonCode.MODEL_ARTIFACT_INVALID


def test_load_artifact_missing_unit_field_is_rejected(write_fake):
    """M05-TEST-007: thiếu hẳn trường unit_of_inference."""
    path, sha = write_fake(drop=("unit_of_inference",))
    with pytest.raises(ModelArtifactError) as err:
        load_artifact(path, expected_sha256=sha)
    assert err.value.reason is ReasonCode.MODEL_ARTIFACT_INVALID


def test_load_artifact_vector_length_mismatch_is_rejected(write_fake):
    path, sha = write_fake(coef=[1.0])
    with pytest.raises(ModelArtifactError) as err:
        load_artifact(path, expected_sha256=sha)
    assert err.value.reason is ReasonCode.MODEL_ARTIFACT_INVALID


def test_load_artifact_unknown_band_thresholds_are_rejected(write_fake):
    path, sha = write_fake(band_thresholds={"A2_B1": 2.75})
    with pytest.raises(ModelArtifactError) as err:
        load_artifact(path, expected_sha256=sha)
    assert err.value.reason is ReasonCode.MODEL_ARTIFACT_INVALID


def test_load_artifact_invalid_json_is_rejected(tmp_path):
    path = tmp_path / "broken.json"
    path.write_bytes(b"{not json")
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ModelArtifactError) as err:
        load_artifact(path, expected_sha256=sha)
    assert err.value.reason is ReasonCode.MODEL_ARTIFACT_INVALID


def test_load_artifact_valid_fake_exposes_fields(write_fake):
    path, sha = write_fake()
    art = load_artifact(path, expected_sha256=sha)
    assert art.feature_order == ("a", "b")
    assert art.sha256 == sha
    assert art.trained_with["asr_model"] == "whisper-small"


def test_load_real_artifact_matches_pinned_hash_and_18_features(real_artifact):
    assert real_artifact.sha256 == RIDGE_RESP_V2_SHA256
    assert len(real_artifact.feature_order) == 18
    assert "filler_ratio" not in real_artifact.feature_order
    assert real_artifact.trained_with["asr_model"] == "whisper-small"


def test_default_artifact_path_requires_env(monkeypatch):
    monkeypatch.delenv(MODEL_DIR_ENV, raising=False)
    with pytest.raises(ModelArtifactError) as err:
        default_artifact_path()
    assert err.value.reason is ReasonCode.MODEL_VERSION_MISSING


def test_default_artifact_path_uses_env(monkeypatch, tmp_path):
    monkeypatch.setenv(MODEL_DIR_ENV, str(tmp_path))
    assert default_artifact_path() == tmp_path / "ridge_resp_v2.json"
