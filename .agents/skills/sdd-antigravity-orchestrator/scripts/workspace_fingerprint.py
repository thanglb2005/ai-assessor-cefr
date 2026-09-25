#!/usr/bin/env python3
"""Create a deterministic fingerprint for an SDD handoff workspace.

The fingerprint covers the base Git revision and current tracked/untracked file
content, including initialized submodules recursively. Git-ignored files are
excluded. Without Git, a deterministic manifest is built while common
generated/dependency directories are excluded.

Only in explicitly selected ``--metadata-file`` Markdown/text files, lines
whose field name is exactly ``WORKSPACE FINGERPRINT:`` are normalized to
``<SELF>``. All other files are hashed verbatim. Version 1 fingerprints must be
reissued with version 2 and the same options must be used for verification.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from typing import Iterable


ALGORITHM_VERSION = "sdd-workspace-v2"
DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".cache",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".turbo",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
FINGERPRINT_FIELD = "workspace fingerprint:"


class FingerprintError(RuntimeError):
    """Raised when a workspace cannot be fingerprinted reliably."""


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise FingerprintError(f"git {' '.join(args)} failed: {message}")
    return result


def git_root(root: Path) -> Path | None:
    try:
        result = run_git(root, "rev-parse", "--show-toplevel", check=False)
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return Path(result.stdout.decode("utf-8", errors="strict").strip()).resolve()


def normalize_fingerprint_field(content: bytes) -> bytes:
    """Normalize plain Markdown/text WORKSPACE FINGERPRINT fields.

    Binary or non-UTF-8 content is returned unchanged. The accepted field can be
    plain, a bullet, or bold Markdown, but must otherwise be an exact field name.
    """

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content

    output: list[str] = []
    changed = False
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body) :]
        probe = body.lstrip()
        indent = body[: len(body) - len(probe)]
        bullet = ""
        if probe.startswith(("- ", "* ")):
            bullet, probe = probe[:2], probe[2:]
        bold = probe.startswith("**")
        if bold:
            probe = probe[2:]
        lowered = probe.lower()
        if lowered.startswith(FINGERPRINT_FIELD):
            field_end = len(FINGERPRINT_FIELD)
            if bold and probe[field_end:].startswith("**"):
                field_end += 2
            if probe[:field_end].replace("**", "").lower() == FINGERPRINT_FIELD:
                label = probe[:field_end]
                output.append(f"{indent}{bullet}{'**' if bold else ''}{label} <SELF>{ending}")
                changed = True
                continue
        output.append(line)

    return "".join(output).encode("utf-8") if changed else content


def path_is_excluded(
    relative: str,
    extra_patterns: Iterable[str],
    *,
    use_default_dirs: bool = True,
) -> bool:
    parts = Path(relative).parts
    if use_default_dirs and any(part in DEFAULT_EXCLUDED_DIRS for part in parts[:-1]):
        return True
    return any(fnmatch.fnmatch(relative, pattern) for pattern in extra_patterns)


def non_git_paths(root: Path, extra_patterns: Iterable[str]) -> list[str]:
    paths: list[str] = []
    for current, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        relative_dir = current_path.relative_to(root)
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name not in DEFAULT_EXCLUDED_DIRS
            and not path_is_excluded((relative_dir / name).as_posix(), extra_patterns)
        )
        for name in sorted(file_names):
            relative = (relative_dir / name).as_posix()
            if not path_is_excluded(relative, extra_patterns):
                paths.append(relative)
    return sorted(set(paths))


def git_paths(root: Path, extra_patterns: Iterable[str]) -> list[str]:
    result = run_git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    decoded = result.stdout.decode("utf-8", errors="surrogateescape")
    return sorted(
        path
        for path in decoded.split("\0")
        if path and not path_is_excluded(path, extra_patterns, use_default_dirs=False)
    )


def metadata_paths(root: Path, requested: Iterable[str]) -> frozenset[str]:
    """Validate exact metadata paths; reject source files and symlink targets."""
    selected: set[str] = set()
    for value in requested:
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts:
            raise FingerprintError(f"Metadata file must be relative to --root: {value}")
        path = root / relative
        if relative.suffix.lower() not in {".md", ".txt"}:
            raise FingerprintError(f"Metadata file must be Markdown or text: {value}")
        if path.resolve() != path or not path.is_file():
            raise FingerprintError(f"Metadata file must exist and not use symlinks: {value}")
        selected.add(relative.as_posix())
    return frozenset(selected)


def hash_entry(
    root: Path, relative: str, selected_metadata: frozenset[str] = frozenset()
) -> tuple[str, str]:
    path = root / relative
    try:
        info = path.lstat()
    except FileNotFoundError:
        return "missing", hashlib.sha256(b"<MISSING>").hexdigest()

    executable = bool(info.st_mode & stat.S_IXUSR)
    if stat.S_ISLNK(info.st_mode):
        payload = os.readlink(path).encode("utf-8", errors="surrogateescape")
        kind = "symlink"
    elif stat.S_ISREG(info.st_mode):
        payload = path.read_bytes()
        if relative in selected_metadata:
            payload = normalize_fingerprint_field(payload)
        kind = "file+x" if executable else "file"
    elif stat.S_ISDIR(info.st_mode):
        if not (path / ".git").exists() or git_root(path) != path:
            raise FingerprintError(f"Submodule is not initialized or cannot be inspected: {relative}")
        # Hash the complete child workspace. Parent exclusions and metadata
        # options select parent entries, not paths inside a submodule.
        child = compute_fingerprint(path, ())
        payload = str(child["fingerprint"]).encode("ascii")
        kind = "submodule"
    else:
        payload = f"<SPECIAL:{stat.S_IFMT(info.st_mode)}>".encode("ascii")
        kind = "special"
    return kind, hashlib.sha256(payload).hexdigest()


def compute_fingerprint(
    root: Path, extra_patterns: Iterable[str], metadata_files: Iterable[str] = ()
) -> dict[str, object]:
    root = root.resolve()
    if not root.is_dir():
        raise FingerprintError(f"Repo root is not a directory: {root}")
    extra_patterns = tuple(extra_patterns)
    selected_metadata = metadata_paths(root, metadata_files)

    discovered_git_root = git_root(root)
    if discovered_git_root is not None and discovered_git_root != root:
        raise FingerprintError(
            f"--root must be the Git repository root ({discovered_git_root}), got {root}"
        )

    if discovered_git_root is not None:
        mode = "git"
        head = run_git(root, "rev-parse", "--verify", "HEAD", check=False)
        base_revision = (
            head.stdout.decode("ascii").strip() if head.returncode == 0 else "no-commits"
        )
        paths = git_paths(root, extra_patterns)
        index_manifest = run_git(root, "ls-files", "-s", "-z").stdout
        index_digest = hashlib.sha256(index_manifest).hexdigest()
        status_result = run_git(
            root, "status", "--short", "--untracked-files=all", check=True
        )
        status = status_result.stdout.decode("utf-8", errors="replace").splitlines()
    else:
        mode = "manifest"
        base_revision = "Git not initialized"
        paths = non_git_paths(root, extra_patterns)
        status = []
        index_digest = None

    unavailable_metadata = selected_metadata.difference(paths)
    if unavailable_metadata:
        raise FingerprintError(
            "Metadata files must be included in the root manifest (not ignored, excluded, "
            f"or inside submodules): {', '.join(sorted(unavailable_metadata))}"
        )

    accumulator = hashlib.sha256()
    accumulator.update(f"{ALGORITHM_VERSION}\0{mode}\0{base_revision}\0".encode("utf-8"))
    for relative in sorted(selected_metadata):
        accumulator.update(b"metadata\0" + relative.encode("utf-8") + b"\0")
    if index_digest is not None:
        accumulator.update(f"index\0{index_digest}\0".encode("ascii"))
    for relative in paths:
        kind, content_hash = hash_entry(root, relative, selected_metadata)
        encoded_path = relative.encode("utf-8", errors="surrogateescape")
        accumulator.update(encoded_path)
        accumulator.update(b"\0")
        accumulator.update(kind.encode("ascii"))
        accumulator.update(b"\0")
        accumulator.update(content_hash.encode("ascii"))
        accumulator.update(b"\0")

    return {
        "algorithm": ALGORITHM_VERSION,
        "mode": mode,
        "root": str(root),
        "base_revision": base_revision,
        "index_digest": index_digest,
        "metadata_files": sorted(selected_metadata),
        "file_count": len(paths),
        "fingerprint": accumulator.hexdigest(),
        "git_status": status,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root; defaults to cwd")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="Additional relative-path glob to exclude; may be repeated",
    )
    parser.add_argument(
        "--metadata-file",
        action="append",
        default=[],
        metavar="PATH",
        help="Exact relative .md/.txt file whose WORKSPACE FINGERPRINT fields are normalized; repeatable",
    )
    parser.add_argument(
        "--expect",
        metavar="HASH",
        help="Exit 1 when the computed fingerprint does not match this value",
    )
    parser.add_argument(
        "--value-only",
        action="store_true",
        help="Print only the fingerprint value",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = compute_fingerprint(Path(args.root), args.exclude, args.metadata_file)
    except (FingerprintError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    fingerprint = str(result["fingerprint"])
    if args.value_only:
        print(fingerprint)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

    if args.expect and fingerprint.lower() != args.expect.lower():
        print(
            f"MISMATCH: expected {args.expect.lower()}, computed {fingerprint}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
