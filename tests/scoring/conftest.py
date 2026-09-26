import hashlib
import json
import os
from pathlib import Path

import pytest

from aicefr.scoring.artifact import MODEL_DIR_ENV, RIDGE_RESP_V2, load_artifact


def _fake_payload(**overrides):
    """ART-FAKE: 2 đặc trưng, hệ số dễ tính (raw = 3 + a + b)."""
    payload = {
        "model_version": "fake_v1",
        "feature_version": "v3",
        "band_map_version": "band-v1",
        "calibration_version": "chua-hieu-chuan",
        "unit_of_inference": "mot bai noi (fixture)",
        "trained_with": {"asr_model": "whisper-small", "vad_name": "silero"},
        "feature_order": ["a", "b"],
        "mean": [0.0, 0.0],
        "scale": [1.0, 1.0],
        "coef": [1.0, 1.0],
        "intercept": 3.0,
        "feature_lo": [0.0, 0.0],
        "feature_hi": [1.0, 1.0],
        "ood_tolerance": 0.5,
        "band_thresholds": {"A2_B1": 2.75, "B1_B2": 3.75},
        "boundary_margin": 0.5,
    }
    payload.update(overrides)
    return payload


@pytest.fixture
def write_fake(tmp_path):
    """Ghi ART-FAKE ra file, trả (đường dẫn, SHA-256) để loader kiểm hash."""

    def _write(drop=(), **overrides):
        payload = _fake_payload(**overrides)
        for key in drop:
            payload.pop(key)
        path = tmp_path / "fake.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    return _write


@pytest.fixture
def real_artifact_path() -> Path:
    """ART-REAL ngoài repo (P05-D-001). Thiếu thì SKIP, không tính là PASS."""
    model_dir = os.environ.get(MODEL_DIR_ENV)
    path = Path(model_dir) / f"{RIDGE_RESP_V2}.json" if model_dir else None
    if path is None or not path.is_file():
        pytest.skip(f"cần {RIDGE_RESP_V2}.json trong ${MODEL_DIR_ENV}")
    return path


@pytest.fixture
def real_artifact(real_artifact_path):
    return load_artifact(real_artifact_path)
