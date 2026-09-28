# M01 — 06 Tasks (W2 task breakdown)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M01 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

Task dưới đây là **bản nháp để review**, chưa phát prompt hoặc chuyển sang Antigravity. ID giữ ổn định để liên kết evidence sau này.

| Task ID / owner | FR/AC và Test ID | Phạm vi file dự kiến | Đầu ra kiểm chứng |
| --- | --- | --- | --- |
| M01-TASK-001 / Nguyên | M01-FR-001, M01-AC-001 · M01-TEST-001, M01-TEST-002, M01-TEST-005 | API submit + tests M01 | Nộp hợp lệ tạo Response; sai quyền/file không tạo dữ liệu |
| M01-TASK-002 / Nguyên | M01-FR-002, M01-AC-002 · M01-TEST-003, M01-TEST-004 | API status/report + tests M01 | Owner xem đúng trạng thái; cross-owner bị chặn |
| M01-TASK-003 / Nguyên | M01-AC-002 · browser QA khi UI có | Template/form/status tối thiểu | Ảnh/browser record thực và lỗi có thể hiểu |

## Handoff và điều kiện hoàn tất

- Mỗi task khi được duyệt phải có prompt file riêng trong `prompts/`, mã Prompt ID, phạm vi file, artifact versions, baseline/fingerprint, check và format raw report. Không ghi `SENT`/`DONE` trước khi có thao tác và evidence thật.
- Unit test bắt buộc cho logic có thể kiểm thử; integration/API/browser check theo Test Plan. Nếu test không áp dụng, giải thích tại task đã duyệt và dùng alternative evidence.
- Một task chỉ được đánh dấu hoàn thành sau actual diff, kết quả chạy thật, Code/Clean Code Review, Final Verification trên revision cuối và user verdict. Metric/test báo cáo phải gắn với lệnh chạy, revision và evidence của dự án.

**Trạng thái task:** direct implementation/test evidence đã được ghi theo chỉ dẫn trực tiếp ngày 28/09/2026; không task nào được đánh dấu DONE/APPROVED. Browser automation M01-TASK-003 là `NOT_RUN`. **Phase 05 verdict:** PENDING.
