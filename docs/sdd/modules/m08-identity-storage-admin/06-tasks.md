# M08 — 06 Tasks (W2 task breakdown)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M08 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

Task dưới đây là **bản nháp để review**, chưa phát prompt hoặc chuyển sang Antigravity. ID giữ ổn định để liên kết evidence sau này.

| Task ID / owner | FR/AC và Test ID | Phạm vi file dự kiến | Đầu ra kiểm chứng |
| --- | --- | --- | --- |
| M08-TASK-001 / Thắng | M08-FR-001, M08-AC-001 · M08-TEST-001, M08-TEST-002, M08-TEST-004 | auth/consent/session + tests | Role/consent/owner bảo vệ submit/read |
| M08-TASK-002 / Thắng | M08-FR-002, M08-AC-002 · M08-TEST-003, M08-TEST-005 | SQLite/BlobStore/audit + tests | Persist/restart/checksum và log sạch |
| M08-TASK-003 / Thắng | M08-FR-002, M08-AC-001, M08-AC-002 · policy pending | admin/export/delete contract; có điều kiện W3 | Không vận hành dữ liệu thật trước data plan approval |

## Handoff và điều kiện hoàn tất

- Mỗi task khi được duyệt phải có prompt file riêng trong `prompts/`, mã Prompt ID, phạm vi file, artifact versions, baseline/fingerprint, check và format raw report. Không ghi `SENT`/`DONE` trước khi có thao tác và evidence thật.
- Unit test bắt buộc cho logic có thể kiểm thử; integration/API/browser check theo Test Plan. Nếu test không áp dụng, giải thích tại task đã duyệt và dùng alternative evidence.
- Một task chỉ được đánh dấu hoàn thành sau actual diff, kết quả chạy thật, Code/Clean Code Review, Final Verification trên revision cuối và user verdict. Metric/test báo cáo phải gắn với lệnh chạy, revision và evidence của dự án.

**Trạng thái tất cả task:** DRAFT / NOT_STARTED. **Phase 05 verdict:** PENDING.
