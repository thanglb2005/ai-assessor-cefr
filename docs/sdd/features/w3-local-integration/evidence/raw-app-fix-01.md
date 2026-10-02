# W3 raw app correction evidence — FIX-01

**Prompt/task:** `W3-PROMPT-002-FIX-01`; W3-TASK-003, W3-TASK-004, W3-TASK-007. **Executor:** gpt-6-luna; Codex reviewed/integrated. **Measured:** 02/10/2026 (Asia/Ho_Chi_Minh). User verdict remains pending.

## Baseline and change

The correction worktree was created at integrated baseline `80c6707`; root subsequently cherry-picked the speech optional-dependency test correction `af5dc8a`, yielding tested starting HEAD `b6063dd`. The scoped implementation commit is `a7506393c9d023b2c695b48822d807f2ddd0e04c`; its source tree is `91c35cd3b96abb10602543ad37b23eef85b27a52`.

Implemented digest-only idempotent session deletion in both in-memory identity and SQLite repositories; enforced the configured active consent version at the local HTTP submission boundary while preserving the legacy API adapter; expanded real-SQLite factory/integration coverage for missing model and QC REVIEW paths, lazy VAD/artifact pinning, persistence/reopen, teacher override, malformed config/path and loopback CLI behavior; and rebuilt page templates as single valid documents with mobile viewport/focus styles and the demo data note on student/teacher pages. Added a reusable actual-browser harness at `scripts/qa/w3_app_browser.py`.

## Verification

Artifact-enabled full regression on tested HEAD `b6063dd`:

```text
PLAYWRIGHT_BROWSERS_PATH=/tmp/aicefr-w3-browsers \
AICEFR_MODEL_DIR=/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src/aicefr/scoring/models \
PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python -m pytest -q -m 'not smoke' \
  --cov=aicefr.auth --cov=aicefr.storage --cov=aicefr.local \
  --cov=aicefr.api.wsgi --cov=aicefr.api.templates --cov-branch \
  --cov-report=term-missing \
  --cov-report=json:/tmp/aicefr-w3-app-fix-coverage.json
```

Exit 0: **249 passed, 0 skipped**. Ruff command `/tmp/aicefr-w3-venv/bin/ruff check src tests scripts/qa/w3_app_browser.py` exited 0; `git diff --check` exited 0. Coverage JSON: `/tmp/aicefr-w3-app-fix-coverage.json`. Auth package aggregate: 95.1% line / 90.9% branch; storage package aggregate: 99.2% line / 92.1% branch. Changed repository/auth paths: `auth/service.py` 93.3% line / 90.0% branch, `auth/memory.py` 100% / 100%, `storage/sqlite.py` 98.7% / 95.8%. Integrated measurement: WSGI 72.6% line / 61.8% branch, templates 89.5% / 64.3%, local app 77.7% / 42.9%, CLI 68.1% / 50.0%. These integrated figures identify unexercised paths; no thresholds or exclusions were altered.

An earlier full run before root's optional-dependency test correction reported 244 passed and one failure: `test_missing_silero_package_is_controlled_error` assumed Silero was absent although the shared environment had it installed. Root corrected that test at `af5dc8a` by mocking the import boundary; the full rerun above passes without skipping it.

The actual Chromium journey and screenshot hashes are recorded in [browser-qa.md](browser-qa.md). Browser fixtures are generated temporarily and use the pinned Ridge artifact externally; no credentials, session token, request body or raw audio were written to repository evidence. This browser journey deliberately takes QC REVIEW and does not exercise ASR/VAD inference. Separate root smoke evidence reports real WAV/MP3 feature extraction with native decoder warnings retained; WER and CEFR accuracy remain `NOT_MEASURED`.

## Scope and limits

No production model, learner data, generated WAV, credential or session was added to Git. The `aicefr-w3-venv` and browser binaries are external temporary environment assets. `a750639` is a code/evidence contribution for review, not user acceptance, remote CI, or deployment.
