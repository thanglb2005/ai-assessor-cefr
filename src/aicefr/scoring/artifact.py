"""Nạp artifact model chấm điểm (M05 Spec v0.2, bước 1–2).

Artifact giữ ngoài repo (P05-D-001): đường dẫn đọc từ biến môi trường
`AICEFR_MODEL_DIR`, SHA-256 ghim trong code. Chỉ nhận JSON, không pickle.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aicefr.contracts import ReasonCode

MODEL_DIR_ENV = "AICEFR_MODEL_DIR"
RIDGE_RESP_V2 = "ridge_resp_v2"
# Đo ngày 26/09/2026, khớp docs/sources/scoring-audit.md (M05-R-001).
RIDGE_RESP_V2_SHA256 = "7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a"

# Artifact ghi không dấu ("mot bai noi"); chấp nhận cả hai cách viết.
_SINGLE_RESPONSE_MARKERS = ("một bài nói", "mot bai noi")
_VECTOR_FIELDS = ("mean", "scale", "coef", "feature_lo", "feature_hi")


class ModelArtifactError(Exception):
    """Artifact không dùng được. `reason` là mã để scorer trả NOT_EVALUATED."""

    def __init__(self, reason: ReasonCode, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class ModelArtifact:
    name: str
    sha256: str
    model_version: str
    feature_version: str
    band_map_version: str | None
    calibration_version: str | None
    unit_of_inference: str
    trained_with: dict[str, Any]
    feature_order: tuple[str, ...]
    mean: tuple[float, ...]
    scale: tuple[float, ...]
    coef: tuple[float, ...]
    intercept: float
    feature_lo: tuple[float, ...]
    feature_hi: tuple[float, ...]
    ood_tolerance: float
    band_thresholds: dict[str, float]
    boundary_margin: float


def default_artifact_path(name: str = RIDGE_RESP_V2) -> Path:
    """Đường dẫn artifact trong thư mục `AICEFR_MODEL_DIR`."""
    model_dir = os.environ.get(MODEL_DIR_ENV)
    if not model_dir:
        raise ModelArtifactError(
            ReasonCode.MODEL_VERSION_MISSING, f"chưa đặt biến môi trường {MODEL_DIR_ENV}"
        )
    return Path(model_dir) / f"{name}.json"


def load_artifact(path: Path, expected_sha256: str = RIDGE_RESP_V2_SHA256) -> ModelArtifact:
    """Nạp và kiểm artifact; lỗi nào cũng ném `ModelArtifactError`, không fallback."""
    if not path.is_file():
        raise ModelArtifactError(ReasonCode.MODEL_VERSION_MISSING, f"không thấy artifact {path}")

    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ModelArtifactError(
            ReasonCode.MODEL_ARTIFACT_INVALID,
            f"SHA-256 của {path.name} là {digest}, khác giá trị ghim {expected_sha256}",
        )

    try:
        data = json.loads(raw.decode("utf-8"))
        artifact = _build(path.stem, digest, data)
    except (ValueError, KeyError, TypeError, OverflowError, AttributeError) as exc:
        raise ModelArtifactError(
            ReasonCode.MODEL_ARTIFACT_INVALID, f"artifact {path.name} sai cấu trúc: {exc}"
        ) from exc

    _require_single_response_unit(artifact)
    return artifact


def _build(name: str, digest: str, data: dict[str, Any]) -> ModelArtifact:
    order = tuple(str(n) for n in data["feature_order"])
    if not order or any(not value for value in order) or len(set(order)) != len(order):
        raise ValueError("feature_order must contain unique non-empty names")
    vectors = {f: tuple(float(x) for x in data[f]) for f in _VECTOR_FIELDS}
    for field, values in vectors.items():
        if len(values) != len(order):
            raise ValueError(f"{field} có {len(values)} phần tử, feature_order có {len(order)}")
        if not all(math.isfinite(value) for value in values):
            raise ValueError(f"{field} phải chứa số hữu hạn")
    if any(
        low > high
        for low, high in zip(vectors["feature_lo"], vectors["feature_hi"], strict=True)
    ):
        raise ValueError("feature_lo không được lớn hơn feature_hi")
    thresholds = {str(k): float(v) for k, v in data["band_thresholds"].items()}
    if set(thresholds) != {"A2_B1", "B1_B2"}:
        raise ValueError(f"band_thresholds phải gồm A2_B1, B1_B2, nhận {sorted(thresholds)}")
    if (not all(math.isfinite(value) and 1.0 <= value <= 6.0 for value in thresholds.values())
            or thresholds["A2_B1"] >= thresholds["B1_B2"]):
        raise ValueError("band thresholds must be finite, ordered, and within [1, 6]")
    intercept = float(data["intercept"])
    tolerance = float(data["ood_tolerance"])
    margin = float(data["boundary_margin"])
    if not all(math.isfinite(value) for value in (intercept, tolerance, margin)):
        raise ValueError("scalar model values must be finite")
    if tolerance < 0 or margin < 0:
        raise ValueError("tolerance and margin must be non-negative")
    return ModelArtifact(
        name=name,
        sha256=digest,
        model_version=str(data["model_version"]),
        feature_version=str(data["feature_version"]),
        band_map_version=data.get("band_map_version"),
        calibration_version=data.get("calibration_version"),
        unit_of_inference=str(data.get("unit_of_inference") or ""),
        trained_with=dict(data.get("trained_with") or {}),
        feature_order=order,
        intercept=intercept,
        ood_tolerance=tolerance,
        band_thresholds=thresholds,
        boundary_margin=margin,
        **vectors,
    )


def _require_single_response_unit(artifact: ModelArtifact) -> None:
    """Chặn model huấn luyện ở mức cả bài thi (M05-REF-05)."""
    unit = artifact.unit_of_inference.lower()
    if not any(marker in unit for marker in _SINGLE_RESPONSE_MARKERS):
        raise ModelArtifactError(
            ReasonCode.MODEL_ARTIFACT_INVALID,
            f"artifact {artifact.name} khai báo đơn vị suy luận {artifact.unit_of_inference!r},"
            " không phải một bài nói",
        )
