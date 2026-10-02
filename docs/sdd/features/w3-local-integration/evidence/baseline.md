# W3 — Baseline and environment evidence

Date: 02/10/2026 Asia/Ho_Chi_Minh.
Code baseline: 2b428ceea9e4459f3235d4ce67f10bab31585ebf.
Implementation baseline commit: 7bb327b655c67d8eb5aafc4cd8ec9481fabdff28 (scope/delegation docs, unchanged source).

| Check | Command | Exit/result |
| --- | --- | --- |
| Non-smoke baseline | /tmp/aicefr-w3-venv/bin/python -m pytest -q -m 'not smoke' | 0; 189 passed, 10 skipped: missing Ridge artifact path |
| Baseline with model artifact | AICEFR_MODEL_DIR=/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src/aicefr/scoring/models /tmp/aicefr-w3-venv/bin/python -m pytest -q -m 'not smoke' | 0; 199 passed, 0 skipped |
| Artifact hash | hashlib.sha256(Path(.../ridge_resp_v2.json).read_bytes()).hexdigest() | 7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a; matches pinned M05 hash |
| Ruff | /tmp/aicefr-w3-venv/bin/ruff check src tests --output-format concise | 0; All checks passed |
| Markdown links | python3 scripts/ci/check_md_links.py | 0; no in-repo broken links; external links explicitly skipped |
| Forbidden-file guard | python3 scripts/ci/check_forbidden_files.py | 0; no extension/name violations; not a general content secret scanner |
| Browser preflight | PLAYWRIGHT_BROWSERS_PATH=/tmp/aicefr-w3-browsers /tmp/aicefr-w3-venv/bin/python + playwright.sync_api Chromium launch/headless fixture page | Restricted sandbox failed with operation-not-permitted; authorized escalated local run exited 0, Chromium 153.0.8010.12, visible fixture heading verified |
| Real ASR prerequisite | ls -ld /home/thanglvc/models/faster-whisper-small | 2; recorded old model location absent on this machine |

## Environment

Python 3.12.3; isolated /tmp/aicefr-w3-venv installed project .[dev], openpyxl 3.1.5 and Playwright 1.63.0. Chromium headless/FFmpeg downloaded to /tmp/aicefr-w3-browsers for QA only. No production dependency added by root. No ASR weight or audio downloaded, no learner data uploaded. Existing internal audio filenames alone do not establish permission/provenance for a real smoke; user was asked for allowed local model/audio paths asynchronously.

## Dispatch integrity

Each implementation prompt was saved in scope, copied to its isolated worktree, logged in Excel sheet Thắng, fingerprinted with sdd-workspace-v2 and verified with --expect before spawn. Initial placeholder fingerprints were stabilized and reverified before actual dispatch; issued values:

- Pipeline: 411c2366ca9d656366523883a3a6f7383506620208b8d0d7ba1495358c20aa84.
- App: 7b2ec2c41aca165ee429b50e0e1afd1158066055616d602f7ec7ed8c6626678c.
- Speech: 077da2ddbf9d18bdd92d48ed0d434619ee942398cbc3656b7400662205490881.

Each worktree includes baseline AI log/prompt metadata changes that agents must not commit; these are managed and committed by root. Executor gpt-6-luna; root Codex reviews actual commits. User acceptance PENDING.
