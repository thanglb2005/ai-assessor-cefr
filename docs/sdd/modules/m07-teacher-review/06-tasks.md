# M07 — 06 Tasks (W2 task breakdown)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M07 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

Task dưới đây là **bản nháp để review**, chưa phát prompt hoặc chuyển sang Antigravity. ID giữ ổn định để liên kết evidence sau này.

| Task ID / owner | FR/AC và Test ID | Phạm vi file dự kiến | Đầu ra kiểm chứng |
| --- | --- | --- | --- |
| M07-TASK-001 / Nguyên | M07-FR-001, M07-FR-002, M07-AC-001, M07-AC-002 · M07-TEST-001 | SDD contract/reason map W2, không source code | M05/M06/M08 nhận interface pack để review |
| M07-TASK-002 / Nguyên | M07-FR-001, M07-FR-002, M07-AC-001, M07-AC-002 · M07-TEST-002, M07-TEST-003, M07-TEST-004, M07-TEST-005 | review repository/API/UI W3, chưa phát prompt | Queue/action/audit/permission có evidence W3 |

## Handoff và điều kiện hoàn tất

- Mỗi task khi được duyệt phải có prompt file riêng trong `prompts/`, mã Prompt ID, phạm vi file, artifact versions, baseline/fingerprint, check và format raw report. Không ghi `SENT`/`DONE` trước khi có thao tác và evidence thật.
- Unit test bắt buộc cho logic có thể kiểm thử; integration/API/browser check theo Test Plan. Nếu test không áp dụng, giải thích tại task đã duyệt và dùng alternative evidence.
- Một task chỉ được đánh dấu hoàn thành sau actual diff, kết quả chạy thật, Code/Clean Code Review, Final Verification trên revision cuối và user verdict. Không chuyển metric/test của repo cũ sang.

**Trạng thái tất cả task:** DRAFT / NOT_STARTED. **Phase 05 verdict:** PENDING.
