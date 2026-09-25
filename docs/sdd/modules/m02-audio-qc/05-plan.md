# M02 — 05 Plan & Task Readiness (Kế hoạch)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M02 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Thắng. **Scope source mới:** `src/aicefr/audio/, src/aicefr/qc/ (đề xuất)` (chưa tạo). Mã nguồn repo tiền nhiệm chỉ được khảo sát ở mức chức năng; implementation W2 viết trong repo mới theo Specification sau khi được duyệt.

## Kiến trúc và thứ tự triển khai

- Thiết kế AudioInput/DecodedAudio/QCResult typed và bộ config ngoài code.
- Dựng decoder và đo chỉ số với giới hạn tài nguyên; giữ raw blob bất biến.
- Nối policy PASS/REVIEW/REJECT vào pipeline port M03; viết test edge cases trước smoke.

## Phụ thuộc và bàn giao

- M01/M08 cung cấp audio_ref có quyền; M03 chỉ nhận DecodedAudio/QCResult hợp lệ.
- Chủ dự án chốt format/ngưỡng qua Phase 01/03; không mượn số từ mã cũ.

## Required checks và review

- Trước task: đối chiếu `01` → `03` → `04`, chốt các quyết định `OPEN`, xác nhận đường dẫn được phép sửa và baseline/fingerprint của repo mới. Git đã được khởi tạo trong repo mới ngày 25/09/2026; dùng commit/diff và revision thực làm evidence sau khi có baseline commit.
- Khi triển khai: type hints cho contract public; validation tại boundary; hàm logic nhỏ và có test; không truyền trạng thái bằng dict vô kiểu giữa module. Không thêm dependency/model/download chỉ vì repo cũ đã có.
- Sau task: chạy các test ID của task, `ruff`/typecheck nếu được cấu hình, kiểm tra diff và privacy. Review code/test riêng tại Phase 07; chạy lại checks trên final revision tại Phase 08.
- Antigravity chỉ nhận prompt sau verdict `APPROVED` của Phase 01, 03, 04 và 05 đúng version. Prompt, raw report và review lưu trong scope root; `docs/evidence/` chỉ dẫn chiếu theo rubric.

## Rủi ro và phương án xử lý

- QC phụ thuộc thiết bị; không dùng threshold chưa khảo sát để tuyên bố đánh giá người học.
- Sai format/decoder có thể tiêu tốn tài nguyên; cần giới hạn trước giải mã.

## Definition of Ready (điều kiện phát prompt)

- Format, ngưỡng và policy REVIEW được duyệt hoặc ghi rõ test-only config.
- Contract audio_ref/ownership M08 có bản version.
- Test IDs và check được duyệt đúng phase.

**CODEX CHECK RESULT:** DRAFT — ranh giới và phụ thuộc đã mô tả; các quyết định mở/approval khiến task chưa `READY`. **User verdict Phase 05:** PENDING.
