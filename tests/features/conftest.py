import pytest
from tests.features.fixtures import FX_PROBS, FX_TOKENS, TRAINED_WITH, make_words


@pytest.fixture
def fx_words():
    return make_words(FX_TOKENS, FX_PROBS)


@pytest.fixture
def real_artifact_path():
    import os
    from pathlib import Path

    from aicefr.scoring.artifact import MODEL_DIR_ENV, RIDGE_RESP_V2

    model_dir = os.environ.get(MODEL_DIR_ENV)
    path = Path(model_dir) / f"{RIDGE_RESP_V2}.json" if model_dir else None
    if path is None or not path.is_file():
        pytest.skip(f"cần {RIDGE_RESP_V2}.json trong ${MODEL_DIR_ENV}")
    return path


@pytest.fixture
def write_fake_artifact(tmp_path):
    import hashlib
    import json

    from aicefr.scoring.artifact import load_artifact

    def _write(order):
        n = len(order)
        payload = {
            "model_version": "fake", "feature_version": "v3", "unit_of_inference": "mot bai noi",
            "trained_with": TRAINED_WITH, "feature_order": list(order), "mean": [0.0] * n,
            "scale": [1.0] * n, "coef": [0.0] * n, "intercept": 3.0, "feature_lo": [0.0] * n,
            "feature_hi": [1.0] * n, "ood_tolerance": 0.5,
            "band_thresholds": {"A2_B1": 2.75, "B1_B2": 3.75}, "boundary_margin": 0.5,
        }  # fmt: skip
        path = tmp_path / "fake.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return load_artifact(path, hashlib.sha256(path.read_bytes()).hexdigest())

    return _write
