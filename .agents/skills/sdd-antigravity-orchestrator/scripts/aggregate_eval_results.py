#!/usr/bin/env python3
"""Aggregate current/baseline Skill eval grading and timing evidence."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any


CONFIGURATIONS = ("current", "baseline")


class AggregateError(ValueError):
    """Raised when iteration evidence is incomplete or malformed."""


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise AggregateError(f"Missing file: {path}") from error
    except json.JSONDecodeError as error:
        raise AggregateError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise AggregateError(f"Root must be an object: {path}")
    return value


def optional_number(value: Any, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise AggregateError(f"{label} must be a non-negative number or null")
    return float(value)


def mean_stddev(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"mean": None, "stddev": None}
    return {
        "mean": round(statistics.mean(values), 6),
        "stddev": round(statistics.pstdev(values), 6),
    }


def grade_case(path: Path) -> dict[str, Any]:
    data = read_object(path)
    version = data.get("eval_set_version")
    if not isinstance(version, str) or not version.strip():
        raise AggregateError(f"eval_set_version is required: {path}")
    expectations = data.get("expectations")
    if not isinstance(expectations, list) or not expectations:
        raise AggregateError(f"expectations must be a non-empty list: {path}")
    passed = failed = not_verifiable = 0
    contract: dict[str, str] = {}
    for index, item in enumerate(expectations):
        if not isinstance(item, dict):
            raise AggregateError(f"expectations[{index}] must be an object: {path}")
        if not isinstance(item.get("text"), str) or not item["text"].strip():
            raise AggregateError(f"expectations[{index}].text is required: {path}")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise AggregateError(f"expectations[{index}].id is required: {path}")
        if identifier in contract:
            raise AggregateError(f"Duplicate expectation id {identifier!r}: {path}")
        contract[identifier] = item["text"]
        if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
            raise AggregateError(f"expectations[{index}].evidence is required: {path}")
        if "passed" not in item:
            raise AggregateError(f"expectations[{index}].passed is required: {path}")
        result = item["passed"]
        if result is True:
            passed += 1
        elif result is False:
            failed += 1
        elif result is None:
            not_verifiable += 1
        else:
            raise AggregateError(
                f"expectations[{index}].passed must be true, false or null: {path}"
            )
    verifiable = passed + failed
    return {
        "eval_set_version": version,
        "expectation_contract": contract,
        "passed": passed,
        "failed": failed,
        "not_verifiable": not_verifiable,
        "pass_rate": passed / verifiable if verifiable else None,
    }


def timing_case(path: Path, configuration: str) -> dict[str, float | None]:
    if not path.exists():
        return {"duration_ms": None, "total_tokens": None}
    data = read_object(path)
    value = data.get(configuration)
    if value is None:
        return {"duration_ms": None, "total_tokens": None}
    if not isinstance(value, dict):
        raise AggregateError(f"{configuration} timing must be an object: {path}")
    return {
        "duration_ms": optional_number(
            value.get("duration_ms"), f"{path}:{configuration}.duration_ms"
        ),
        "total_tokens": optional_number(
            value.get("total_tokens"), f"{path}:{configuration}.total_tokens"
        ),
    }


def aggregate(iteration_root: Path) -> dict[str, Any]:
    eval_dirs = sorted(path for path in iteration_root.glob("eval-*") if path.is_dir())
    if not eval_dirs:
        raise AggregateError(f"No eval-* directories found in {iteration_root}")

    grades: dict[str, dict[str, dict[str, Any]]] = {}
    versions: set[str] = set()
    for eval_dir in eval_dirs:
        pair = {
            name: grade_case(eval_dir / f"grading-{name}.json")
            for name in CONFIGURATIONS
        }
        if pair["current"]["expectation_contract"] != pair["baseline"]["expectation_contract"]:
            raise AggregateError(f"Current/baseline expectation IDs and text must match: {eval_dir}")
        versions.update(grade["eval_set_version"] for grade in pair.values())
        grades[eval_dir.name] = pair
    if len(versions) != 1:
        raise AggregateError("All grading files must use the same eval_set_version")

    result: dict[str, Any] = {
        "schema_version": 2,
        "eval_set_version": next(iter(versions)),
        "iteration": iteration_root.name,
        "configurations": {},
        "delta_current_minus_baseline": {},
    }
    for configuration in CONFIGURATIONS:
        case_rates: list[float] = []
        durations: list[float] = []
        tokens: list[float] = []
        passed = failed = not_verifiable = 0
        per_case: list[dict[str, Any]] = []
        for eval_dir in eval_dirs:
            grade = grades[eval_dir.name][configuration]
            timing = timing_case(eval_dir / "timing.json", configuration)
            passed += grade["passed"]
            failed += grade["failed"]
            not_verifiable += grade["not_verifiable"]
            if grade["pass_rate"] is not None:
                case_rates.append(grade["pass_rate"])
            if timing["duration_ms"] is not None:
                durations.append(timing["duration_ms"])
            if timing["total_tokens"] is not None:
                tokens.append(timing["total_tokens"])
            per_case.append({"eval": eval_dir.name, "grading": grade, "timing": timing})
        verifiable = passed + failed
        result["configurations"][configuration] = {
            "cases": len(eval_dirs),
            "assertions": {
                "passed": passed,
                "failed": failed,
                "not_verifiable": not_verifiable,
                "pass_rate": round(passed / verifiable, 6) if verifiable else None,
            },
            "case_pass_rate": mean_stddev(case_rates),
            "duration_ms": mean_stddev(durations),
            "total_tokens": mean_stddev(tokens),
            "per_case": per_case,
        }

    current = result["configurations"]["current"]
    baseline = result["configurations"]["baseline"]
    for key, current_value, baseline_value in (
        (
            "assertion_pass_rate",
            current["assertions"]["pass_rate"],
            baseline["assertions"]["pass_rate"],
        ),
        ("duration_ms_mean", current["duration_ms"]["mean"], baseline["duration_ms"]["mean"]),
        ("total_tokens_mean", current["total_tokens"]["mean"], baseline["total_tokens"]["mean"]),
    ):
        result["delta_current_minus_baseline"][key] = (
            round(current_value - baseline_value, 6)
            if current_value is not None and baseline_value is not None
            else None
        )
    return result


def markdown_report(benchmark: dict[str, Any]) -> str:
    lines = [
        f"# Benchmark {benchmark['iteration']}",
        "",
        "| Cấu hình | Pass rate | Mean case ± stddev | Thời gian mean ± stddev | Token mean ± stddev |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for configuration in CONFIGURATIONS:
        value = benchmark["configurations"][configuration]
        assertions = value["assertions"]
        case_rate = value["case_pass_rate"]
        duration = value["duration_ms"]
        tokens = value["total_tokens"]
        lines.append(
            f"| {configuration} | {assertions['pass_rate']} | "
            f"{case_rate['mean']} ± {case_rate['stddev']} | "
            f"{duration['mean']} ± {duration['stddev']} | "
            f"{tokens['mean']} ± {tokens['stddev']} |"
        )
    lines.extend(
        [
            "",
            "## Delta current − baseline",
            "",
            "```json",
            json.dumps(
                benchmark["delta_current_minus_baseline"],
                ensure_ascii=False,
                indent=2,
            ),
            "```",
            "",
            "Pass rate không thay thế human feedback hoặc phân tích invariant/variance.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("iteration_root", help="Directory containing eval-* results")
    parser.add_argument("--json-output", default="benchmark.json")
    parser.add_argument("--markdown-output", default="benchmark.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.iteration_root).resolve()
    try:
        benchmark = aggregate(root)
        json_path = root / args.json_output
        markdown_path = root / args.markdown_output
        json_path.write_text(
            json.dumps(benchmark, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        markdown_path.write_text(markdown_report(benchmark), encoding="utf-8")
    except (AggregateError, OSError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(f"WROTE: {json_path} and {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
