# M08 — 05 Plan & Task Readiness

> **W2 v0.3 · 28/09/2026 · Phase 05 APPROVED by Thắng ('duyệt đi, cứ done task đã rồi tính, gấp').** Phase 01, 03 and 04 were approved earlier.

**Owner:** Thắng. **Module source scope:** `src/aicefr/auth/`, `src/aicefr/storage/`, M08 additions to `src/aicefr/contracts.py`, M08 dependency pins in `pyproject.toml`, and listed tests only. Only generated fixture accounts/data may be used.

## Architecture and task order

1. **M08-TASK-001 / SCRUM-48:** typed Actor/auth/password/session service, fixture-only account bootstrap, consent gate, owner authorization. The auth/session service depends on repository protocols; database-backed persistence is delivered by Task 002.
2. **M08-TASK-002 / SCRUM-49:** SQLite repositories/schema, persistent session digest/consent/response/audit metadata and filesystem BlobStore. Use explicit transactions and injected `data_dir`; stage/hash/atomic-replace blobs and compensate on DB failure; startup reconciliation reports orphan blobs without deleting them.

Task 002 depends on Task 001 interfaces. Overall proposed integration order across the four branches is SCRUM-46 → SCRUM-47 → SCRUM-48 → SCRUM-49, to serialize edits to `contracts.py` and `pyproject.toml`. Within M08, Task 002 depends on Task 001. Finish/review Task 001 first, then rebase Task 002 to latest `main` after SCRUM-48 merges before requesting its PR merge.

## Shared-contract review — pending

Nguyên (M01/M07) has not yet reviewed Actor/Consent/Response/Blob/Audit schemas, ownership semantics or audit fields. Thắng explicitly authorized implementation first on 28/09/2026; this does not claim Nguyên approved the contract. Keep the pending review visible before PR merge. No HTTP routes, export/delete of real records, retention execution, encryption-at-rest, backup, cloud storage or production privacy claim is in W2. Record cross-owner feedback in the review log.

## File scope by task

| Jira | Allowed files |
| --- | --- |
| SCRUM-48 / M08-TASK-001 | `pyproject.toml`; `src/aicefr/contracts.py` (Actor/Session/Consent types only); `src/aicefr/auth/**`; `tests/auth/test_auth.py`; `tests/auth/test_consent.py`; `tests/storage/test_authorization.py`; `tests/auth/test_privacy.py` |
| SCRUM-49 / M08-TASK-002 | `src/aicefr/contracts.py` (Response/Blob/Audit types only); `src/aicefr/storage/**`; `src/aicefr/infra/**`; `tests/storage/test_sqlite_blob_store.py`; `tests/storage/test_privacy.py`; M08 assertions in `tests/test_contracts.py` |

No user data, transcript, audio, secrets, generated database/blob, unrelated module or model files. The draft M08-TASK-003 for admin/export/delete is deferred to W3 and has no branch in this W2 delivery.

## Required checks and evidence

- Phase 04 approved commands: `python3 -m pytest -q -m "not smoke" tests/auth tests/storage`; coverage with `--cov=aicefr.auth --cov=aicefr.storage --cov-branch --cov-report=term-missing`; run `python3 -m pytest -q tests/test_contracts.py` for shared types.
- Gate: line ≥ 90% and branch ≥ 85% on pure M08 Python logic; assertions cover role/owner/consent/expiry, rollback, restart, checksum and privacy. No browser/API check applies because the repository has no HTTP/UI surface.
- Record command, timestamp, exit code, pass/fail/skip, coverage, revision and workspace fingerprint under module `evidence/`. No DB/blob test output is committed.
- Initial observed branch base was `55d8952`; verify branch head and capture a fresh fingerprint before implementation. Thắng asked Codex to implement the tasks directly and push the branches. No Antigravity prompt is issued for this direct implementation.

## Risks and Definition of Ready

- Session tokens are random 32-byte opaque values; store only SHA-256 digests. Argon2id uses argon2-cffi 25.1.0 at 19 MiB/t=2/p=1. These settings are approved; measure local verification timing in implementation evidence.
- SQLite/filesystem work only for generated fixtures. Atomic filesystem replace and SQLite commit are not one transaction; compensate known failures and report crash leftovers for review.
- **Phase 05 decision:** Thắng approved proceeding immediately with the concrete task scopes. M01/M07 review remains pending and is recorded as a PR integration risk; do not represent it as completed.

**CODEX CHECK RESULT:** PASS for scoped implementation readiness; M01/M07 review remains PENDING. **USER VERDICT:** APPROVED to implement and push, 28/09/2026.
