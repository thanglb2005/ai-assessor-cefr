# SCRUM-49 — Implementation evidence

- Task: M08-TASK-002; branch: `feat/SCRUM-49-M08-TASK-002-SQLite-BlobStore-persistence-va-audit`.
- Base revision: SCRUM-48 commit `2f6a9cb7409dd9f6f3296a0b35468de079fa6993`; branch is stacked on SCRUM-48.
- Pre-evidence workspace fingerprint: `05f3b7fa5a8f5df3effd015af9c04fe06ff6d14e41db99644a95b0807041f92d`.
- Verification at 28/09/2026 03:06 UTC with Python 3.12.3 in isolated `/tmp/ai-assessor-m08-venv`.
- All accounts, bytes and metadata used by tests are synthetic fixtures in pytest `tmp_path` outside repo.

| Check | Exit | Actual result |
| --- | --- | --- |
| `/tmp/ai-assessor-m08-venv/bin/python -m pytest -q tests/auth tests/storage tests/test_contracts.py` | 0 | 24 passed, 0 skipped |
| `/tmp/ai-assessor-m08-venv/bin/python -m pytest -q -m 'not smoke' --cov=aicefr.auth --cov=aicefr.storage --cov-branch --cov-report=term-missing tests/auth tests/storage` | 0 | 15 passed, 0 skipped; 302 statements, 5 missed = 98.3% line; 44 branches, 2 partial = 95.5% branch; pytest-cov aggregate 98% |
| `/tmp/ai-assessor-m08-venv/bin/python -m pytest -q -m 'not smoke'` | 0 | 139 passed, 10 skipped; skips require absent `ridge_resp_v2.json` in `$AICEFR_MODEL_DIR` |
| `/tmp/ai-assessor-m08-venv/bin/ruff check src/aicefr/auth src/aicefr/storage src/aicefr/contracts.py tests/auth tests/storage tests/test_contracts.py` | 0 | All checks passed |
| `git diff --check` | 0 | No whitespace error |
| Argon2id login verify, 5 calls in fixture repository with `time.perf_counter()` | 0 | min 0.0246 s; max 0.0320 s on local runner. This is a local observation, not a production latency guarantee. |

Mapping: M08-TEST-001 owner check precedes blob read and missing/foreign IDs share error; M08-TEST-002 withdrawal blocks new submission, preserves prior fixture; M08-TEST-003 restart, session digest, audit, checksum, SQLite rollback, blob compensation, schema and report-only orphan reconciliation; M08-TEST-004 session persistence/expiry; M08-TEST-005 repo-external data root, token absent from DB, no secret/token logs.

**Known integration risk:** Nguyên's M01/M07 shared-contract review remains PENDING. No owner approval, real-data readiness or PR merge verdict is claimed.
