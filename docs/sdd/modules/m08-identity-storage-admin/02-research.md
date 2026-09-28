# M08 — 02 Research

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M08 / module |
| DATE | 28/09/2026 |
| RESEARCH MODE | RUN — được người dùng duyệt trong M08 Phase 01 |
| OBJECTIVE | Chọn hướng password/session, SQLite transaction và local BlobStore phù hợp Python 3.11+; không thiết kế policy dữ liệu thật |

## Sources and findings

| Source | Fact |
| --- | --- |
| OWASP Password Storage Cheat Sheet | Mật khẩu cần password hashing chậm; Argon2id được ưu tiên, với cấu hình khuyến nghị tối thiểu m=19 MiB, t=2, p=1. Work factor cần cân bằng với hiệu năng và đo trên môi trường đích. |
| argon2-cffi 25.1.0 documentation | PasswordHasher dùng Argon2id và salt ngẫu nhiên; lưu encoded hash và có API verify/check_needs_rehash. Thư viện có thể cấu hình memory/time/parallelism. |
| OWASP Session Management Cheat Sheet | Session ID phải vô nghĩa, CSPRNG và tối thiểu 128 bit; state/quyền giữ phía server; session có idle/absolute expiration; không log session ID. Browser integration nên dùng secure HttpOnly cookies qua HTTPS. |
| Python 3.11 secrets documentation | secrets.token_urlsafe(nbytes) tạo token ngẫu nhiên an toàn; docs cho rằng 32 byte đủ cho thông thường. |
| Python 3.11 sqlite3 documentation | Với isolation_level=None, SQLite không tự mở transaction; app có thể điều khiển explicit SQL transaction; đây là cách tương thích Python 3.11. autocommit attribute được thêm ở Python 3.12. |
| Python 3.11 os documentation | os.replace thay file đích; successful replace atomic theo yêu cầu POSIX và có thể lỗi nếu nguồn/đích ở filesystem khác. |
| Project pyproject.toml | Python >=3.11; chỉ có NumPy/Pydantic trong base dependencies; chưa có web framework/auth/storage implementation. |

## Options

| Area | Option | Trade-off | Recommendation |
| --- | --- | --- | --- |
| Password | argon2-cffi Argon2id | Một dependency native/compiled; verify latency/memory cần đo; OWASP ưu tiên. | ADAPT — dùng high-level PasswordHasher, không tự triển khai crypto. |
| Password | hashlib.scrypt | Không thêm dependency; availability phụ thuộc OpenSSL build; cấu hình/an toàn vẫn cần tuning. | OPEN — fallback nếu Argon2id không thể cài trên target. |
| Session | Framework session management | OWASP khuyên ưu tiên implementation có sẵn; repo chưa có HTTP framework. | ADAPT — M08 chỉ cung cấp SessionService/repository; không tự viết HTTP/cookie transport. |
| Session | Opaque token + server-side record | Hợp với domain module; cần persistent session repo, TTL rõ; không log token. | ADAPT — token 32 random bytes, lưu digest thay token thô; cookie integration thuộc API layer sau. |
| Persistence | sqlite3 + filesystem BlobStore | DB transaction không bao trùm filesystem; cần staging, atomic replace và compensating cleanup. | ADAPT — audit + metadata trong một transaction; staging blob trong cùng blob root; kiểm tra hash. |
| Persistence | Store audio as SQLite BLOB | Cùng DB transaction dễ hơn; DB phình lớn và không phù hợp audio files. | REJECT cho W2 local blob store. |

## Technical constraints and risks

- SQLite không cung cấp encryption-at-rest; không dùng implementation này với dữ liệu thật.
- Không có một atomic transaction chung cho SQLite và filesystem. Write flow cần staging temp trong cùng filesystem, hash verify, os.replace, transaction metadata/audit và cleanup khi DB commit fail. Crash window có thể để orphan blob; phải có reconciliation evidence/strategy.
- Blob path phải được tạo từ opaque ID và cấu hình root; không ghép trực tiếp user-controlled path.
- Owner authorization nằm trước mọi read/write; owner ID lấy từ verified server-side Actor/session, không nhận từ client payload.
- Consent withdrawn không tự xóa existing records vì retention/delete policy chưa được duyệt; W2 chỉ block new submit.
- Session expiry durations, account bootstrap flow, DB path/permissions và cleanup orphan policy là decision của owner.

## Recommendation for Phase 03

- Argon2id qua argon2-cffi; bắt đầu bằng OWASP min (19 MiB, t=2, p=1) và đo local; rehash khi parameters cần nâng.
- Dùng opaque 32-byte session token; chỉ lưu SHA-256 digest trong server-side SessionRepository; server enforce idle + absolute expiry; chưa xây cookie/HTTP transport vì repo chưa có server.
- Đề xuất idle timeout 30 phút và absolute timeout 8 giờ cho local demo; cho phép cấu hình và test bằng injected clock. Owner cần approve.
- SQLite dùng sqlite3 Python 3.11 compatibility mode, transaction explicit, foreign_keys bật; audit row đi cùng transaction metadata.
- BlobStore dùng opaque blob ID, staging trong blob root, SHA-256 kiểm tra integrity, atomic replace rồi metadata/audit commit; compensation và orphan detection được test.
- W2 data dir lấy từ config/env và phải ở ngoài repo; không bật real user data, export/delete real data, backup hoặc encryption claims.

## Decisions required from owner

- Approve argon2-cffi dependency and Argon2id parameters after local timing evidence.
- Approve idle/absolute session TTL and whether SessionRepository persists across restart.
- Approve synthetic account bootstrap flow and username/user-id format.
- Approve blob root configuration, blob commit/compensation behavior and orphan reconciliation.
- M01/M07 owners must review shared Actor/Consent/Response/Blob/Audit schema before Phase 05.

## References

- OWASP Password Storage: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- OWASP Session Management: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- argon2-cffi API: https://argon2-cffi.readthedocs.io/en/25.1.0/api.html
- Python sqlite3: https://docs.python.org/3.11/library/sqlite3.html
- Python secrets: https://docs.python.org/3.11/library/secrets.html
- Python os.replace: https://docs.python.org/3.11/library/os.html#os.replace
- M01 Requirement/Spec: ../m01-intake-student/01-requirement.md; ../m01-intake-student/03-specification.md
- M07 requirement: ../m07-teacher-review/01-requirement.md

## CODEX CHECK RESULT

PASS — sources are distinguished from recommendations; W2 synthetic-data limitation is preserved; no legal/data-retention policy is inferred.
