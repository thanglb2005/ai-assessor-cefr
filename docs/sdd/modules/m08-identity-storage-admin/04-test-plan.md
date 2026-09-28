# M08 — 04 Test Plan (Kế hoạch kiểm thử)

> **W2 v0.2 · 28/09/2026 · Phase 04 APPROVED by Thắng.** Specification v0.3 đã được duyệt Phase 03. Test chưa chạy; Phase 04 đã được duyệt, Phase 05 vẫn pending trước khi triển khai.

Mọi ca chạy với SQLite/blob trong `tmp_path`, clock giả và actor/tài khoản giả danh do nhóm tạo. Không cần HTTP/browser vì repo chưa có transport; không dùng dữ liệu thật.

| Test ID | FR/AC | Level | Tình huống | Kỳ vọng | Test file dự kiến |
| --- | --- | --- | --- | --- | --- |
| M08-TEST-001 | M08-FR-001 / M08-AC-001 | Unit + service integration | Actor student đọc response/blob của mình, actor khác hoặc ID không tồn tại | Chỉ owner được nội dung; trường hợp foreign/missing trả lỗi không phân biệt; BlobStore không bị đọc trước authorization | `tests/storage/test_authorization.py` |
| M08-TEST-002 | M08-FR-001 / M08-AC-001 | Service integration | Submit với consent active/version hiện hành; rút consent rồi thử submit mới | Submit hợp lệ được ghi; sau withdrawal submit mới bị chặn và audit được ghi; response/blob fixture cũ không bị xóa ngầm | `tests/auth/test_consent.py` |
| M08-TEST-003 | M08-FR-001/002 / M08-AC-001/002 | SQLite/filesystem integration | Lưu response, audit và blob; mở lại repository sau restart; thử checksum sai và lỗi transaction | Metadata/audit/session digest còn nhất quán sau restart; blob đúng checksum đọc được; corruption bị fail closed; lỗi commit được bù trừ; orphan chỉ được báo | `tests/storage/test_sqlite_blob_store.py` |
| M08-TEST-004 | M08-FR-001 / M08-AC-001 | Unit/security | Xác minh password Argon2id; client thử tự chọn role; session token hợp lệ, sai digest, idle hết hạn, absolute hết hạn | Role lấy từ Actor đã xác thực; chỉ digest được lưu; idle 30 phút và absolute 8 giờ được thực thi server-side; hết hạn không truy cập được; không log password/token | `tests/auth/test_auth.py` |
| M08-TEST-005 | M08-FR-002 / M08-AC-002 | Privacy/security | Quét caplog, DB/blob test root và diff của repo sau các luồng fixture | Không có password/hash, raw session token, PII, audio/transcript trong log/Git; data_dir test ở ngoài repo; không có dữ liệu thật | `tests/auth/test_privacy.py`, `tests/storage/test_privacy.py` |

## Mapping và lệnh dự kiến

| Mục | Lệnh / phạm vi |
| --- | --- |
| Cài môi trường dev | `python3 -m pip install -e '.[dev]'` |
| Unit + integration | `python3 -m pytest -q -m "not smoke" tests/auth tests/storage` |
| Coverage branch | `python3 -m pytest -q -m "not smoke" --cov=aicefr.auth --cov=aicefr.storage --cov-branch --cov-report=term-missing tests/auth tests/storage` |
| Test contracts nếu đổi shared model | `python3 -m pytest -q tests/test_contracts.py` |
| Coverage đề xuất | Line ≥ 90% và branch ≥ 85% trên logic thuần `aicefr.auth`/`aicefr.storage`; không lấy coverage phần phụ thuộc Argon2 C làm chỉ báo; mọi nhánh authorization, consent, expiry, rollback và integrity phải có assertion. Đây là đề xuất cho M08; TP-D-001 hiện chỉ áp dụng M03/M04/M05. |
| Smoke/browser | N/A trong scope hiện tại: chưa có HTTP/UI; không dùng dữ liệu thật. |

## Bằng chứng Phase 06/08

Ghi nguyên lệnh, thời gian, exit code, pass/fail/skip, coverage line/branch, revision/fingerprint và đường dẫn evidence. Không commit DB/blob phát sinh; tmp data được tạo/xóa bởi fixture test. Nếu một ca không chạy được do platform/dependency, ghi rõ skip và lý do, không báo thay thành PASS.

**CODEX CHECK RESULT:** PASS — AC đã ánh xạ đủ; test chạy bằng stack pytest hiện hữu; coverage target đã duyệt. **User verdict Phase 04:** APPROVED theo đề xuất · 28/09/2026.
