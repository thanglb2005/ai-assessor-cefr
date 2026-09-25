# M03 — 05 Plan & Task Readiness (Kế hoạch)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M03 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Sang. **Scope source mới:** `src/aicefr/asr/ (đề xuất)` (chưa tạo). Mã nguồn repo tiền nhiệm chỉ được khảo sát ở mức chức năng; implementation W2 viết trong repo mới theo Specification sau khi được duyệt.

## Kiến trúc và thứ tự triển khai

- Chốt engine/model sau Research + license/hardware check; không kế thừa dependency hoặc model file cũ.
- Dựng typed AsrEngine port và adapter local; test double nằm trong tests hoặc đánh dấu test-only.
- Viết validator timestamp/quality và smoke command offline; lưu log/model config không chứa transcript người thật.

## Phụ thuộc và bàn giao

- M02 giao QCResult/DecodedAudio có version; M08 cung cấp artifact storage/access.
- M04 chỉ dùng transcript OK hoặc theo policy UNRELIABLE được duyệt; M06 trỏ timestamp đã xác minh.

## Required checks và review

- Trước task: đối chiếu `01` → `03` → `04`, chốt các quyết định `OPEN`, xác nhận đường dẫn được phép sửa và baseline/fingerprint của repo mới. Git đã được khởi tạo trong repo mới ngày 25/09/2026; dùng commit/diff và revision thực làm evidence sau khi có baseline commit.
- Khi triển khai: type hints cho contract public; validation tại boundary; hàm logic nhỏ và có test; không truyền trạng thái bằng dict vô kiểu giữa module. Không thêm dependency/model/download chỉ vì repo cũ đã có.
- Sau task: chạy các test ID của task, `ruff`/typecheck nếu được cấu hình, kiểm tra diff và privacy. Review code/test riêng tại Phase 07; chạy lại checks trên final revision tại Phase 08.
- Antigravity chỉ nhận prompt sau verdict `APPROVED` của Phase 01, 03, 04 và 05 đúng version. Prompt, raw report và review lưu trong scope root; `docs/evidence/` chỉ dẫn chiếu theo rubric.

## Rủi ro và phương án xử lý

- Model có thể tự tải mạng hoặc thiếu license/hardware; khóa local path và ghi NOT_RUN nếu chưa sẵn.
- ASR lỗi với accent/noise có thể làm sai feature; không dùng smoke để tuyên bố WER/độ chính xác.

## Definition of Ready (điều kiện phát prompt)

- Engine/model/license/runtime và quyền dùng audio được ghi rõ.
- Timestamp contract và failure policy với M04/M05 được review.
- Phase verdict và test smoke criteria được duyệt.

**CODEX CHECK RESULT:** DRAFT — ranh giới và phụ thuộc đã mô tả; các quyết định mở/approval khiến task chưa `READY`. **User verdict Phase 05:** PENDING.
