# SCRUM-48 — Implementation evidence

- Task: M08-TASK-001; branch: `feat/SCRUM-48-M08-TASK-001-Auth-consent-va-kiểm-tra-owner`.
- Base revision: `55d89524bce7b62d04835d73c723696976f773be`.
- Pre-evidence workspace fingerprint: `ebe405ae92638f2c6dee2a7041d95cd6b0b0a3c01e4f5799f82daa907ec3a699`.
- Runtime: Python 3.12.3, isolated venv at `/tmp/ai-assessor-m08-venv`; 28/09/2026 02:59 UTC.
- Fixture-only data; no generated account secret, token, DB or blob committed.

| Check (working tree after implementation) | Exit | Actual result |
| --- | --- | --- |
| `/tmp/ai-assessor-m08-venv/bin/python -m pytest -q tests/auth tests/storage tests/test_contracts.py` | 0 | 13 passed, 0 skipped |
| `/tmp/ai-assessor-m08-venv/bin/python -m pytest -q --cov=aicefr.auth --cov-branch --cov-report=term-missing tests/auth tests/storage` | 0 | 5 passed; auth TOTAL 111 statements, 4 missed, 20 branches, 1 partial; 96% aggregate coverage, branch at least 19/20 = 95% |
| `/tmp/ai-assessor-m08-venv/bin/ruff check src/aicefr/auth tests/auth tests/storage src/aicefr/contracts.py` | 0 | All checks passed |
| `/tmp/ai-assessor-m08-venv/bin/python -m pytest -q -m 'not smoke'` | 0 | 128 passed, 10 skipped; all skips require absent `ridge_resp_v2.json` in `$AICEFR_MODEL_DIR` |
| `git diff --check` | 0 | No whitespace error |

Mapping: M08-TEST-001 owner denial with indistinguishable missing/foreign errors; M08-TEST-002 versioned consent withdrawal gate; M08-TEST-004 Argon2id, digest-only token, role and TTL; M08-TEST-005 caplog contains no credential/hash/token.

**Review limitation:** Nguyên's M01/M07 contract review is PENDING. The user authorized implementation first; do not infer owner approval or PR merge readiness from this evidence.

## Integration after M02 task completion

- Merged `feat/SCRUM-47-M02-TASK-002-QC-policy-va-pipeline-boundary-tests` into SCRUM-48 after both task pairs were implemented, retaining M02 and M08 types in `src/aicefr/contracts.py` and all three pinned dependencies in `pyproject.toml`.
- Combined check: `PYTHONPATH=src /tmp/ai-assessor-cefr-m02-venv/bin/python -m pytest -q -m 'not smoke'` → exit 0, 149 passed, 10 skipped for absent `ridge_resp_v2.json` in `$AICEFR_MODEL_DIR`.
- Combined Ruff check over M02/M08 source, shared contract and corresponding tests → exit 0, all checks passed. `git diff --cached --check` → exit 0.
- Sang (M03/M04) and Nguyên (M01/M07) cross-owner reviews remain pending. No main merge was performed.
