#!/usr/bin/env python3
"""Validate behavioral and trigger eval data for this Skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


class EvalValidationError(ValueError):
    """Raised when an eval file violates the local schema."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise EvalValidationError(f"Missing eval file: {path}") from error
    except json.JSONDecodeError as error:
        raise EvalValidationError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise EvalValidationError(f"Root must be an object: {path}")
    return value


def skill_name(skill_root: Path) -> str:
    skill_file = skill_root / "SKILL.md"
    try:
        content = skill_file.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise EvalValidationError(f"Missing SKILL.md: {skill_file}") from error
    match = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", content)
    if match is None:
        raise EvalValidationError("SKILL.md must contain a lowercase kebab-case name")
    name = match.group(1)
    if skill_root.name != name:
        raise EvalValidationError(
            f"Skill directory {skill_root.name!r} does not match name {name!r}"
        )
    return name


def require_text(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise EvalValidationError(f"{label} must be a non-empty string")


def validate_metadata(data: dict[str, Any], path: Path, expected_name: str) -> str:
    if data.get("schema_version") != 1:
        raise EvalValidationError(f"{path}: schema_version must be 1")
    version = data.get("eval_set_version")
    require_text(version, f"{path}.eval_set_version")
    if data.get("skill_name") != expected_name:
        raise EvalValidationError(f"{path}: skill_name must be {expected_name!r}")
    return version


def validate_behavior_evals(skill_root: Path, expected_name: str) -> tuple[int, str]:
    path = skill_root / "evals" / "evals.json"
    data = read_json(path)
    version = validate_metadata(data, path, expected_name)
    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        raise EvalValidationError(f"{path}: evals must be a non-empty list")

    identifiers: set[int] = set()
    for index, item in enumerate(evals):
        label = f"evals[{index}]"
        if not isinstance(item, dict):
            raise EvalValidationError(f"{label} must be an object")
        identifier = item.get("id")
        if not isinstance(identifier, int) or isinstance(identifier, bool):
            raise EvalValidationError(f"{label}.id must be an integer")
        if identifier in identifiers:
            raise EvalValidationError(f"Duplicate behavioral eval id: {identifier}")
        identifiers.add(identifier)
        require_text(item.get("prompt"), f"{label}.prompt")
        require_text(item.get("expected_output"), f"{label}.expected_output")

        files = item.get("files", [])
        if not isinstance(files, list) or not all(isinstance(value, str) for value in files):
            raise EvalValidationError(f"{label}.files must be a list of paths")
        for relative in files:
            candidate = (skill_root / relative).resolve()
            try:
                candidate.relative_to(skill_root.resolve())
            except ValueError as error:
                raise EvalValidationError(f"{label}.files escapes skill root: {relative}") from error
            if not candidate.is_file():
                raise EvalValidationError(f"{label}.files is missing: {relative}")

        expectations = item.get("expectations")
        if (
            not isinstance(expectations, list)
            or not expectations
            or not all(isinstance(value, str) and value.strip() for value in expectations)
        ):
            raise EvalValidationError(f"{label}.expectations must contain non-empty strings")
    return len(evals), version


def validate_trigger_evals(
    skill_root: Path, expected_name: str
) -> tuple[int, int, int, str]:
    path = skill_root / "evals" / "trigger-evals.json"
    data = read_json(path)
    version = validate_metadata(data, path, expected_name)
    queries = data.get("queries")
    if not isinstance(queries, list) or not queries:
        raise EvalValidationError(f"{path}: queries must be a non-empty list")

    identifiers: set[str] = set()
    positives = 0
    negatives = 0
    negative_near_misses = 0
    allowed_modes = {"SDD_ORCHESTRATION", "REMOTE_PR_REVIEW", "NONE"}
    for index, item in enumerate(queries):
        label = f"queries[{index}]"
        if not isinstance(item, dict):
            raise EvalValidationError(f"{label} must be an object")
        identifier = item.get("id")
        require_text(identifier, f"{label}.id")
        if identifier in identifiers:
            raise EvalValidationError(f"Duplicate trigger eval id: {identifier}")
        identifiers.add(identifier)
        require_text(item.get("query"), f"{label}.query")
        require_text(item.get("rationale"), f"{label}.rationale")
        should_trigger = item.get("should_trigger")
        if not isinstance(should_trigger, bool):
            raise EvalValidationError(f"{label}.should_trigger must be boolean")
        mode = item.get("expected_mode")
        if mode not in allowed_modes:
            raise EvalValidationError(f"{label}.expected_mode is invalid: {mode!r}")
        if should_trigger and mode == "NONE":
            raise EvalValidationError(f"{label}: triggering query cannot expect NONE")
        if not should_trigger and mode != "NONE":
            raise EvalValidationError(f"{label}: non-triggering query must expect NONE")
        near_miss = item.get("near_miss")
        if not isinstance(near_miss, bool):
            raise EvalValidationError(f"{label}.near_miss must be boolean")
        if should_trigger:
            positives += 1
        else:
            negatives += 1
            negative_near_misses += int(near_miss)

    if positives < 8 or negatives < 8:
        raise EvalValidationError("Trigger evals require at least 8 positive and 8 negative queries")
    if abs(positives - negatives) > 2:
        raise EvalValidationError("Trigger evals must be approximately balanced")
    if negative_near_misses < 6:
        raise EvalValidationError("Trigger evals require at least 6 negative near-miss queries")
    return positives, negatives, negative_near_misses, version


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", required=True, help="Path to the Skill directory")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.skill_root).resolve()
    try:
        name = skill_name(root)
        behavior_count, behavior_version = validate_behavior_evals(root, name)
        positives, negatives, near_misses, trigger_version = validate_trigger_evals(root, name)
        if behavior_version != trigger_version:
            raise EvalValidationError(
                "Behavior and trigger eval_set_version must match: "
                f"{behavior_version!r} != {trigger_version!r}"
            )
    except (EvalValidationError, OSError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(
        "VALID: "
        f"eval_set_version={behavior_version}, behavior={behavior_count}, "
        f"trigger_positive={positives}, "
        f"trigger_negative={negatives}, negative_near_miss={near_misses}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
