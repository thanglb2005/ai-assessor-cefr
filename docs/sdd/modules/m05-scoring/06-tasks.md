# M05 — 06 Tasks (W2 task breakdown)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M05 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

Task dưới đây là **bản nháp để review**, chưa phát prompt hoặc chuyển sang Antigravity. ID giữ ổn định để liên kết evidence sau này.

| Task ID / owner | FR/AC và Test ID | Phạm vi file dự kiến | Đầu ra kiểm chứng |
| --- | --- | --- | --- |
| M05-TASK-001 / Sang | M05-FR-001, M05-FR-002, M05-AC-001 · M05-TEST-001, M05-TEST-002, M05-TEST-004 | Score schema/refusal path + tests | Chỉ overall + năm coverage; model chưa tương thích hoặc thiếu evidence thì NOT_EVALUATED |
| M05-TASK-002 / Sang | M05-FR-001, M05-AC-002 · M05-TEST-003, M05-TEST-006 | Viết mới model loader/predict từ artifact Ridge đã tái kiểm, có điều kiện | Overall chạy khi quyền và tương thích artifact được duyệt; nếu không BLOCKED |
| M05-TASK-003 / Sang | M05-FR-002, M05-AC-002 · M05-TEST-005 | Experiment manifest/evaluation, có điều kiện | Metric thật hoặc NOT_RUN với lý do |

## Handoff và điều kiện hoàn tất

- Mỗi task khi được duyệt phải có prompt file riêng trong `prompts/`, mã Prompt ID, phạm vi file, artifact versions, baseline/fingerprint, check và format raw report. Không ghi `SENT`/`DONE` trước khi có thao tác và evidence thật.
- Unit test bắt buộc cho logic có thể kiểm thử; integration/API/browser check theo Test Plan. Nếu test không áp dụng, giải thích tại task đã duyệt và dùng alternative evidence.
- Một task chỉ được đánh dấu hoàn thành sau actual diff, kết quả chạy thật, Code/Clean Code Review, Final Verification trên revision cuối và user verdict. Không chuyển metric/test của repo cũ sang.

**Trạng thái tất cả task:** DRAFT / NOT_STARTED. **Phase 05 verdict:** PENDING.
