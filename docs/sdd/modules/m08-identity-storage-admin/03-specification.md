# M08 — 03 Specification (Đặc tả)

> W2 v0.3 · 28/09/2026. Requirement v0.2 và Specification v0.3 đã được user duyệt Phase 01/03. Phase 04 Test Plan v0.2 đã được duyệt; Phase 05 còn chờ owner review và user verdict.

Owner: Thắng. Mục tiêu W2: cung cấp auth/session, consent, owner check và local persistence tối thiểu cho luồng fixture của dự án; dữ liệu người học thật chưa được phép dùng.

## Boundary và hợp đồng đầu vào/đầu ra

| Artifact | Trường/invariant | Owner → consumer |
| --- | --- | --- |
| Actor | pseudonymous actor_id, role student/teacher/admin; client không tự khai role | M08 → M01/M07 |
| Session | opaque random token chỉ gửi qua adapter; state nằm server-side; expiry enforced server-side; token không ghi log | M08 → M01/M07 |
| ConsentRecord | pseudonymous participant_id, consent_version, active/withdrawn, timestamps; rút consent chặn submit mới | M08 → M01 |
| ResponseRecord | response_id, pseudonymous owner_id, task/version, opaque audio_ref, checksum, status/revision | M08 → M01–M07 |
| BlobStore | opaque blob ID, resolved path nằm trong configured root, immutable content + SHA-256 verification | M08 → M01–M07 |
| AuditEvent | actor pseudonym, action, object ID, timestamp, reason; append-only; không PII/token/content | M08 → M07/admin |

## Authentication, role and consent

- No public signup for teacher/admin. Demo accounts are synthetic fixtures or provisioned by an explicit bootstrap function outside public request handling.
- Selected: pin argon2-cffi 25.1.0; use its Argon2id PasswordHasher at m=19456 KiB (19 MiB), t=2, p=1. Do not weaken parameters implicitly; record any approved versioned change and measure verification cost on the target runtime.
- Selected: generate each opaque session token from 32 random bytes using secrets; persist only its SHA-256 digest in the server-side SQLite SessionRepository. Store actor, role, created_at, last_seen_at, idle expiry and absolute expiry; never persist or log the raw token.
- Selected: 30-minute idle timeout and 8-hour absolute timeout, checked on every resolve. Successful activity updates last_seen_at but cannot extend the absolute expiry. Persist the digest and expiry state across process restart; inject a clock for deterministic tests.
- Owner checks compare authenticated Actor.actor_id to record owner_id before returning response/blob; do not distinguish missing ID from foreign-owned ID at API boundary.
- Active consent version is required before new submission. Withdrawal blocks new submission immediately; it does not delete existing data in W2.
- M08 exposes typed service/repository interfaces; HTTP routes, cookie flags and browser integration belong to an API/UI scope not present in current repo.

## Persistence and audit

- SQLite schema/migrations are versioned; SQLite and blob roots come from an injected `data_dir` configuration outside the repo; no implicit default path. Python 3.11 compatible explicit transactions, foreign_keys enabled, parameterized queries.
- Response metadata and its audit event commit in the same SQLite transaction.
- Blob save writes bounded bytes to a temp file under the configured blob root, computes SHA-256, flushes, uses atomic replace on the same filesystem, then stores metadata/audit. DB failure triggers compensating removal; startup reconciliation reports unreferenced blobs without deleting user data silently.
- Blob read verifies SHA-256 against metadata before returning bytes. Owner check happens before filesystem access.
- Audit is append-only through the repository interface; updates/deletes are not exposed in W2.
- W2 uses generated fixtures and accounts only. No real-data export/delete, retention execution, encryption-at-rest, key management or backup claims.

## Errors and recovery

- Invalid credentials, expired session, role mismatch, withdrawn consent and foreign owner return controlled authorization errors without accessing protected blob content.
- Invalid blob ID/path, missing blob, checksum mismatch or SQLite error fail closed; no Response points to a missing blob.
- Failed metadata transaction compensates the staged/final blob where possible; reconciliation reports crash leftovers for operator review.

## Privacy and security

- Never log passwords, password hashes, raw session tokens, audio bytes, transcripts, email or real identifiers.
- DB, blobs and local secret/config files stay outside Git. No network services or model data are used.
- Local SQLite/filesystem are for synthetic data only; they are not a production compliance or encryption guarantee.
- Accessibility: N/A — M08 has no user interface or HTTP surface in this scope.

## Trace Requirement → AC

| Requirement | Acceptance Criteria | Observation |
| --- | --- | --- |
| M08-FR-001 | M08-AC-001 | Cross-owner read denied; withdrawn consent blocks new submit; fixture data remains. |
| M08-FR-002 | M08-AC-002 | Restart restores metadata/blob/audit and validates checksum; logs/repo scan contain no secrets or PII. |

## Phase 03 decisions — APPROVED 28/09/2026

- Dùng argon2-cffi 25.1.0 / Argon2id (m=19456 KiB, t=2, p=1); account chỉ được bootstrap tường minh từ fixture giả danh.
- Session token 32 byte ngẫu nhiên; chỉ lưu SHA-256 digest; SQLite SessionRepository tồn tại qua restart; idle TTL 30 phút, absolute TTL 8 giờ.
- data_dir được inject qua cấu hình và phải nằm ngoài repo; không tự chọn đường dẫn lưu mặc định.
- SQLite transaction tường minh; BlobStore staging dưới cùng root, SHA-256, atomic replace, bù trừ khi DB lỗi; reconciliation chỉ báo blob mồ côi, không tự xóa.
- W2 chỉ dùng fixture/tài khoản giả danh. Export/xóa/retention dữ liệu thật vẫn để W3 sau policy.

**CODEX CHECK RESULT:** PASS về W2 data boundary, FR/AC trace, failure/recovery and privacy. **User verdict Phase 03:** APPROVED theo đề xuất · 28/09/2026.

**Phase 05 dependency:** Nguyên (M01/M07 owner) review Actor/Consent/Response/Blob/Audit contracts trước khi duyệt Plan/Tasks.

## Lịch sử phiên bản

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 25/09/2026 | Draft ban đầu |
| v0.2 | 28/09/2026 | Requirement Phase 01 approved; W2 synthetic-only scope and Research findings |
| v0.3 | 28/09/2026 | Phase 03 decisions approved by Thắng |
