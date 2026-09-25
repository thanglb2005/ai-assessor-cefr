# M01 — 03 Specification (Đặc tả)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M01 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Nguyên. **Cơ sở:** [Nguồn đề tài do nhóm tạo](../../../sources/README.md) và [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx). **Mục tiêu W2:** Sinh viên đã xác thực nộp một bài nói độc thoại qua upload, theo dõi trạng thái và chỉ xem báo cáo của mình.

## Boundary và hợp đồng đầu vào/đầu ra

| Artifact/boundary | Trường hoặc invariant bắt buộc | Owner/consumer |
| --- | --- | --- |
| SubmitRequest | `task_id`, `prompt_version`, file audio; owner lấy từ session, không nhận owner do client tự khai | M01 → M08/M02 |
| Response | `response_id`, owner pseudonym, `task_id`, `audio_ref`, status, created_at, `revision` | M01/M08 → pipeline |
| ResponseStatus | `QUEUED/RUNNING/COMPLETED/REVIEW_REQUIRED/REJECTED/FAILED`; reason code khi không hoàn tất | pipeline → M01 UI |
| ReportRef | nullable; chỉ xuất khi M06 có báo cáo hợp lệ và M08 xác nhận owner | M06/M08 → M01 |

## Hành vi có thể kiểm tra

- Kiểm tra session, role student, consent version và task đang mở **trước** khi ghi audio/Response; chỉ trả ID giả danh.
- Chấp nhận file qua whitelist định dạng/dung lượng do nhóm chốt trong config; lưu qua M08, sau đó tạo Response trạng thái `QUEUED` và chuyển M02.
- Hiển thị trạng thái xử lý của một Response; `COMPLETED` chỉ khi có artifact M06, `REVIEW_REQUIRED` không bị hiển thị như kết quả đã được giảng viên duyệt.
- Đường xem báo cáo kiểm tra cùng owner ở mỗi request; nếu chưa có report thì trả trạng thái và reason, không tạo score mặc định.

## Lỗi, thiếu dữ liệu và phục hồi

- Thiếu consent, sai role, file lỗi hoặc task không hợp lệ: trả lỗi xử lý được và không lưu Response nửa chừng.
- Pipeline lỗi: giữ Response với `FAILED`/reason hoặc trạng thái retry được quyết định sau; không âm thầm chuyển `COMPLETED`.
- Upload lặp/timeout: chính sách idempotency đang OPEN; cho đến khi chốt, không giả định exactly-once.

## Quyền, riêng tư và giao diện

- Owner/role lấy từ M08; cùng một lỗi truy cập cho ID không tồn tại và ID không thuộc chủ sở hữu để hạn chế lộ dữ liệu.
- Không trả đường dẫn blob, transcript/PII trong log; UI có nhãn “ước lượng/chưa duyệt” khi M06 trả kết quả tạm.
- Form upload có thông báo lỗi rõ và điều khiển bàn phím; responsive/browser QA ở W3 nếu UI được triển khai.

## Trace Requirement → AC

| Requirement | Acceptance Criteria | Cách quan sát |
| --- | --- | --- |
| M01-FR-001 | M01-AC-001 | Không consent/sai role không tạo Response |
| M01-FR-002 | M01-AC-002 | Owner thấy đúng trạng thái; người khác không xem được |

## Quyết định còn mở

- Định dạng audio và giới hạn kích thước nào được nhận ở W2?
- Có yêu cầu ghi âm trình duyệt W3 hay chỉ upload?
- Chính sách retry/idempotency cho submit timeout?

**CODEX CHECK RESULT:** DRAFT — đã đối chiếu FR/AC và ranh giới M01; chưa có verdict Phase 01, hợp đồng liên module và dữ liệu W2 cần review. **User verdict Phase 03:** PENDING.
