#!/usr/bin/env python3
"""Behavioral tests for workspace_fingerprint.py."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("workspace_fingerprint.py")


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


class WorkspaceFingerprintTests(unittest.TestCase):
    def make_git_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        git(root, "init", "-q")
        git(root, "config", "user.email", "skill-test@example.invalid")
        git(root, "config", "user.name", "Skill Test")
        (root / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
        (root / "README.md").write_text("initial\n", encoding="utf-8")
        git(root, "add", ".")
        git(root, "commit", "-qm", "initial")
        return temporary, root

    def fingerprint(self, root: Path, *options: str) -> str:
        result = run("--root", str(root), *options)
        return str(json.loads(result.stdout)["fingerprint"])

    def make_submodule(self, root: Path) -> Path:
        temporary, source = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        git(root, "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(source), "library")
        return root / "library"

    def test_regular_change_changes_fingerprint(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        before = self.fingerprint(root)
        (root / "README.md").write_text("changed\n", encoding="utf-8")
        self.assertNotEqual(before, self.fingerprint(root))

    def test_fingerprint_field_is_self_normalized(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        status = root / "STATUS.md"
        status.write_text("WORKSPACE FINGERPRINT: first\n", encoding="utf-8")
        first = self.fingerprint(root, "--metadata-file", "STATUS.md")
        status.write_text("WORKSPACE FINGERPRINT: second\n", encoding="utf-8")
        self.assertEqual(first, self.fingerprint(root, "--metadata-file", "STATUS.md"))

    def test_ordinary_source_is_hashed_verbatim(self) -> None:
        for use_git in (False, True):
            with self.subTest(use_git=use_git):
                if use_git:
                    temporary, root = self.make_git_repo()
                else:
                    temporary = tempfile.TemporaryDirectory()
                    root = Path(temporary.name)
                self.addCleanup(temporary.cleanup)
                source = root / "app.js"
                source.write_text("export const value = `\nWORKSPACE FINGERPRINT: first\n`;\n")
                before = self.fingerprint(root)
                source.write_text("export const value = `\nWORKSPACE FINGERPRINT: second\n`;\n")
                self.assertNotEqual(before, self.fingerprint(root))

    def test_unselected_markdown_is_hashed_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            status = root / "STATUS.md"
            status.write_text("WORKSPACE FINGERPRINT: first\n")
            before = self.fingerprint(root)
            status.write_text("WORKSPACE FINGERPRINT: second\n")
            self.assertNotEqual(before, self.fingerprint(root))

    def test_metadata_roundtrip_and_other_field_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            status, prompt = root / "STATUS.md", root / "PROMPT.md"
            status.write_text("- **WORKSPACE FINGERPRINT:** <SELF>\nTask: one\n")
            prompt.write_text("WORKSPACE FINGERPRINT: <SELF>\n")
            options = ("--metadata-file", "STATUS.md", "--metadata-file", "PROMPT.md")
            first = self.fingerprint(root, *options)
            status.write_text(f"- **WORKSPACE FINGERPRINT:** {first}\nTask: one\n")
            prompt.write_text(f"WORKSPACE FINGERPRINT: {first}\n")
            self.assertEqual(0, run("--root", str(root), *options, "--expect", first).returncode)
            status.write_text(f"- **WORKSPACE FINGERPRINT:** {first}\nTask: two\n")
            self.assertNotEqual(first, self.fingerprint(root, *options))

    def test_metadata_rejects_source_missing_and_outside_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.js").write_text("const x = 1;\n")
            (root / "STATUS.md").write_text("WORKSPACE FINGERPRINT: <SELF>\n")
            (root / "link.md").symlink_to(root / "STATUS.md")
            for value in ("app.js", "missing.md", "../outside.md", str(root / "STATUS.md"), "link.md"):
                with self.subTest(value=value):
                    result = run("--root", str(root), "--metadata-file", value, check=False)
                    self.assertEqual(2, result.returncode)
                    self.assertIn("Metadata file", result.stderr)

    def test_ignored_or_excluded_metadata_is_rejected(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        (root / "ignored.txt").write_text("WORKSPACE FINGERPRINT: first\n")
        result = run("--root", str(root), "--metadata-file", "ignored.txt", check=False)
        self.assertEqual(2, result.returncode)
        (root / "STATUS.md").write_text("WORKSPACE FINGERPRINT: first\n")
        result = run("--root", str(root), "--metadata-file", "STATUS.md", "--exclude", "STATUS.md", check=False)
        self.assertEqual(2, result.returncode)

    def test_submodule_tracked_and_untracked_changes_are_detected(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        child = self.make_submodule(root)
        before = self.fingerprint(root)
        (child / "README.md").write_text("changed child\n")
        tracked_change = self.fingerprint(root)
        self.assertNotEqual(before, tracked_change)
        (child / "new.txt").write_text("untracked child\n")
        self.assertNotEqual(tracked_change, self.fingerprint(root))

    def test_submodule_ignored_changes_do_not_change_fingerprint(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        child = self.make_submodule(root)
        before = self.fingerprint(root)
        (child / "ignored.txt").write_text("ignored child\n")
        self.assertEqual(before, self.fingerprint(root))

    def test_submodule_head_changes_are_detected(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        child = self.make_submodule(root)
        before = self.fingerprint(root)
        git(child, "-c", "user.name=Skill Test", "-c", "user.email=skill-test@example.invalid",
            "-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-qm", "new child revision")
        self.assertNotEqual(before, self.fingerprint(root))

    def test_nested_submodule_changes_are_detected(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        child = self.make_submodule(root)
        grandchild = self.make_submodule(child)
        before = self.fingerprint(root)
        (grandchild / "README.md").write_text("changed grandchild\n")
        self.assertNotEqual(before, self.fingerprint(root))

    def test_uninitialized_submodule_fails_closed(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        child = self.make_submodule(root)
        (child / ".git").rename(child / "git-marker-backup")
        result = run("--root", str(root), check=False)
        self.assertEqual(2, result.returncode)
        self.assertIn("not initialized", result.stderr)

    def test_excluded_submodule_is_not_hashed(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        child = self.make_submodule(root)
        before = self.fingerprint(root, "--exclude", "library")
        (child / "README.md").write_text("excluded child\n")
        self.assertEqual(before, self.fingerprint(root, "--exclude", "library"))

    def test_untracked_content_is_included(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        before = self.fingerprint(root)
        (root / "new.txt").write_text("new\n", encoding="utf-8")
        self.assertNotEqual(before, self.fingerprint(root))

    def test_git_ignored_content_is_excluded(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        before = self.fingerprint(root)
        (root / "ignored.txt").write_text("ignored\n", encoding="utf-8")
        self.assertEqual(before, self.fingerprint(root))

    def test_non_git_manifest_excludes_dependency_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.txt").write_text("app\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            before = self.fingerprint(root)
            (root / "node_modules" / "package.txt").write_text("generated\n", encoding="utf-8")
            self.assertEqual(before, self.fingerprint(root))

    def test_expect_reports_mismatch(self) -> None:
        temporary, root = self.make_git_repo()
        self.addCleanup(temporary.cleanup)
        result = run("--root", str(root), "--expect", "0" * 64, check=False)
        self.assertEqual(1, result.returncode)
        self.assertIn("MISMATCH", result.stderr)


if __name__ == "__main__":
    unittest.main()
