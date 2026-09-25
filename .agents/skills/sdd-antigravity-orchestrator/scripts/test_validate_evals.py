#!/usr/bin/env python3
"""Tests for validate_evals.py."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("validate_evals.py")


def run(root: Path, *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--skill-root", str(root)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


class ValidateEvalsTests(unittest.TestCase):
    def make_skill(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory(prefix="eval-skill-")
        root = Path(temporary.name) / "sample-skill"
        (root / "evals").mkdir(parents=True)
        (root / "SKILL.md").write_text(
            "---\nname: sample-skill\ndescription: Test fixture.\n---\n",
            encoding="utf-8",
        )
        behavior = {
            "schema_version": 1,
            "eval_set_version": "test-v1",
            "skill_name": "sample-skill",
            "evals": [
                {
                    "id": 1,
                    "prompt": "Run the workflow",
                    "expected_output": "A verified result",
                    "files": [],
                    "expectations": ["Output contains inspectable evidence"],
                }
            ],
        }
        queries = []
        for index in range(8):
            queries.append(
                {
                    "id": f"YES-{index}",
                    "query": f"Trigger query {index}",
                    "should_trigger": True,
                    "expected_mode": "SDD_ORCHESTRATION",
                    "near_miss": False,
                    "rationale": "Requires orchestration",
                }
            )
            queries.append(
                {
                    "id": f"NO-{index}",
                    "query": f"Near miss query {index}",
                    "should_trigger": False,
                    "expected_mode": "NONE",
                    "near_miss": index < 6,
                    "rationale": "Adjacent but out of scope",
                }
            )
        (root / "evals" / "evals.json").write_text(
            json.dumps(behavior), encoding="utf-8"
        )
        (root / "evals" / "trigger-evals.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "eval_set_version": "test-v1",
                    "skill_name": "sample-skill",
                    "queries": queries,
                }
            ),
            encoding="utf-8",
        )
        return temporary, root

    def load(self, path: Path) -> dict[str, object]:
        return json.loads(path.read_text(encoding="utf-8"))

    def save(self, path: Path, value: object) -> None:
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_valid_fixture_passes(self) -> None:
        temporary, root = self.make_skill()
        self.addCleanup(temporary.cleanup)
        result = run(root)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("VALID:", result.stdout)

    def test_duplicate_behavior_id_fails(self) -> None:
        temporary, root = self.make_skill()
        self.addCleanup(temporary.cleanup)
        path = root / "evals" / "evals.json"
        data = self.load(path)
        evals = data["evals"]
        assert isinstance(evals, list)
        evals.append(dict(evals[0]))
        self.save(path, data)
        result = run(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("Duplicate behavioral eval id", result.stderr)

    def test_missing_expectations_fails(self) -> None:
        temporary, root = self.make_skill()
        self.addCleanup(temporary.cleanup)
        path = root / "evals" / "evals.json"
        data = self.load(path)
        evals = data["evals"]
        assert isinstance(evals, list) and isinstance(evals[0], dict)
        evals[0]["expectations"] = []
        self.save(path, data)
        result = run(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("expectations", result.stderr)

    def test_skill_name_mismatch_fails(self) -> None:
        temporary, root = self.make_skill()
        self.addCleanup(temporary.cleanup)
        path = root / "evals" / "evals.json"
        data = self.load(path)
        data["skill_name"] = "wrong-skill"
        self.save(path, data)
        result = run(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("skill_name", result.stderr)

    def test_unbalanced_trigger_set_fails(self) -> None:
        temporary, root = self.make_skill()
        self.addCleanup(temporary.cleanup)
        path = root / "evals" / "trigger-evals.json"
        data = self.load(path)
        queries = data["queries"]
        assert isinstance(queries, list)
        data["queries"] = [item for item in queries if item["should_trigger"]]
        self.save(path, data)
        result = run(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("at least 8 positive and 8 negative", result.stderr)

    def test_missing_input_file_fails(self) -> None:
        temporary, root = self.make_skill()
        self.addCleanup(temporary.cleanup)
        path = root / "evals" / "evals.json"
        data = self.load(path)
        evals = data["evals"]
        assert isinstance(evals, list) and isinstance(evals[0], dict)
        evals[0]["files"] = ["evals/files/missing.txt"]
        self.save(path, data)
        result = run(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("files is missing", result.stderr)

    def test_eval_set_versions_must_match(self) -> None:
        temporary, root = self.make_skill()
        self.addCleanup(temporary.cleanup)
        path = root / "evals" / "trigger-evals.json"
        data = self.load(path)
        data["eval_set_version"] = "test-v2"
        self.save(path, data)
        result = run(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("eval_set_version must match", result.stderr)


if __name__ == "__main__":
    unittest.main()
