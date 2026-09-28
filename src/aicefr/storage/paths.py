"""Explicit data roots outside the source repository."""

from __future__ import annotations

from pathlib import Path


def external_data_dir(data_dir: Path | str) -> Path:
    if not data_dir:
        raise ValueError("data_dir is required")
    root = Path(data_dir).expanduser().resolve()
    repo_root = Path(__file__).resolve().parents[3]
    if root == repo_root or root.is_relative_to(repo_root):
        raise ValueError("data_dir must be outside the repository")
    root.mkdir(parents=True, exist_ok=True)
    return root
