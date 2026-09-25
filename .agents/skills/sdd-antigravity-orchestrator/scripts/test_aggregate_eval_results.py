#!/usr/bin/env python3
"""Tests for aggregate_eval_results.py."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("aggregate_eval_results.py")


class AggregateEvalResultsTests(unittest.TestCase):
    def run_script(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def write_case(
        self,
        root: Path,
        name: str,
        current: list[bool | None],
        baseline: list[bool | None],
        current_timing: tuple[int, int],
        baseline_timing: tuple[int, int],
    ) -> None:
        case = root / name
        case.mkdir()
        for configuration, values in (("current", current), ("baseline", baseline)):
            grading = {
                "eval_set_version": "test-v1",
                "expectations": [
                    {"id": f"assertion-{index}", "text": f"assertion-{index}", "passed": value, "evidence": "evidence"}
                    for index, value in enumerate(values)
                ]
            }
            (case / f"grading-{configuration}.json").write_text(
                json.dumps(grading), encoding="utf-8"
            )
        timing = {
            "current": {
                "duration_ms": current_timing[0],
                "total_tokens": current_timing[1],
            },
            "baseline": {
                "duration_ms": baseline_timing[0],
                "total_tokens": baseline_timing[1],
            },
        }
        (case / "timing.json").write_text(json.dumps(timing), encoding="utf-8")

    def test_aggregates_current_and_baseline(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-benchmark-") as temporary:
            root = Path(temporary) / "iteration-1"
            root.mkdir()
            self.write_case(root, "eval-1", [True, True], [True, False], (100, 1000), (150, 1200))
            self.write_case(root, "eval-2", [True, False], [False, False], (300, 3000), (250, 2800))
            result = self.run_script(root)
            self.assertEqual(0, result.returncode, result.stderr)
            benchmark = json.loads((root / "benchmark.json").read_text(encoding="utf-8"))
            self.assertEqual(0.75, benchmark["configurations"]["current"]["assertions"]["pass_rate"])
            self.assertEqual(0.25, benchmark["configurations"]["baseline"]["assertions"]["pass_rate"])
            self.assertEqual(0.5, benchmark["delta_current_minus_baseline"]["assertion_pass_rate"])
            self.assertEqual("test-v1", benchmark["eval_set_version"])
            self.assertTrue((root / "benchmark.md").is_file())

    def test_not_verifiable_is_excluded_from_pass_rate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-benchmark-") as temporary:
            root = Path(temporary) / "iteration-1"
            root.mkdir()
            self.write_case(root, "eval-1", [True, None], [False, None], (1, 1), (1, 1))
            result = self.run_script(root)
            self.assertEqual(0, result.returncode, result.stderr)
            benchmark = json.loads((root / "benchmark.json").read_text(encoding="utf-8"))
            self.assertEqual(1.0, benchmark["configurations"]["current"]["assertions"]["pass_rate"])
            self.assertEqual(1, benchmark["configurations"]["current"]["assertions"]["not_verifiable"])

    def test_missing_baseline_grading_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-benchmark-") as temporary:
            root = Path(temporary) / "iteration-1"
            case = root / "eval-1"
            case.mkdir(parents=True)
            (case / "grading-current.json").write_text(
                json.dumps({"eval_set_version": "test-v1", "expectations": [{"id": "a", "text": "a", "passed": True, "evidence": "e"}]}),
                encoding="utf-8",
            )
            result = self.run_script(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("grading-baseline.json", result.stderr)

    def test_different_expectation_sets_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-benchmark-") as temporary:
            root = Path(temporary)
            self.write_case(root, "eval-1", [True], [True, False], (1, 1), (1, 1))
            result = self.run_script(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("expectation IDs and text must match", result.stderr)
            self.assertFalse((root / "benchmark.json").exists())

    def test_invalid_grading_contracts_fail(self) -> None:
        for mutation in ("missing_version", "different_version", "missing_id", "different_id",
                         "duplicate_id", "different_text", "missing_passed"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(prefix="skill-benchmark-") as temporary:
                root = Path(temporary)
                self.write_case(root, "eval-1", [True, False], [True, False], (1, 1), (1, 1))
                path = root / "eval-1" / "grading-current.json"
                grade = json.loads(path.read_text())
                if mutation == "missing_version":
                    del grade["eval_set_version"]
                elif mutation == "different_version":
                    grade["eval_set_version"] = "test-v2"
                elif mutation == "missing_id":
                    del grade["expectations"][0]["id"]
                elif mutation == "different_id":
                    grade["expectations"][0]["id"] = "other-id"
                elif mutation == "duplicate_id":
                    grade["expectations"][1]["id"] = grade["expectations"][0]["id"]
                elif mutation == "different_text":
                    grade["expectations"][0]["text"] = "different criterion"
                else:
                    del grade["expectations"][0]["passed"]
                path.write_text(json.dumps(grade))
                result = self.run_script(root)
                self.assertEqual(1, result.returncode, result.stdout)
                self.assertIn("INVALID:", result.stderr)
                self.assertFalse((root / "benchmark.json").exists())

    def test_expectation_order_does_not_affect_pairing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-benchmark-") as temporary:
            root = Path(temporary)
            self.write_case(root, "eval-1", [True, False], [True, False], (1, 1), (1, 1))
            path = root / "eval-1" / "grading-current.json"
            grade = json.loads(path.read_text())
            grade["expectations"].reverse()
            path.write_text(json.dumps(grade))
            result = self.run_script(root)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_versions_must_match_across_cases(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-benchmark-") as temporary:
            root = Path(temporary)
            self.write_case(root, "eval-1", [True], [True], (1, 1), (1, 1))
            self.write_case(root, "eval-2", [True], [True], (1, 1), (1, 1))
            for configuration in ("current", "baseline"):
                path = root / "eval-2" / f"grading-{configuration}.json"
                grade = json.loads(path.read_text())
                grade["eval_set_version"] = "test-v2"
                path.write_text(json.dumps(grade))
            result = self.run_script(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("same eval_set_version", result.stderr)


if __name__ == "__main__":
    unittest.main()
