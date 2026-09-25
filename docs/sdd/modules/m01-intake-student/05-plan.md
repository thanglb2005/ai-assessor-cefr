# M01 — 05 Plan & Task Readiness (Kế hoạch)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M01 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Nguyên. **Scope source mới:** `src/aicefr/api/student.py, src/aicefr/api/templates/ (đề xuất)` (chưa tạo). Mã nguồn repo tiền nhiệm chỉ được khảo sát ở mức chức năng; implementation W2 viết trong repo mới theo Specification sau khi được duyệt.

## Kiến trúc và thứ tự triển khai

- Dựng schema request/response và API mỏng; dùng contract M08 cho session/consent/owner, không tự viết auth trong M01.
- Viết đường submit có validation, lưu blob/Response atomic hoặc rollback rõ; gọi pipeline qua port có kiểu.
- Viết status/report endpoint và giao diện tối thiểu; test quyền truy cập và trạng thái lỗi.

## Phụ thuộc và bàn giao

- M08 cung cấp auth, consent, BlobStore và ResponseRepository contract trước M01-TASK-001.
- M02–M06 trả artifact/status qua interface có kiểu; Thắng giữ orchestration, Nguyên giữ HTTP/UI M01.

## Required checks và review

- Trước task: đối chiếu `01` → `03` → `04`, chốt các quyết định `OPEN`, xác nhận đường dẫn được phép sửa và baseline/fingerprint của repo mới. Git đã được khởi tạo trong repo mới ngày 25/09/2026; dùng commit/diff và revision thực làm evidence sau khi có baseline commit.
- Khi triển khai: type hints cho contract public; validation tại boundary; hàm logic nhỏ và có test; không truyền trạng thái bằng dict vô kiểu giữa module. Không thêm dependency/model/download chỉ vì repo cũ đã có.
- Sau task: chạy các test ID của task, `ruff`/typecheck nếu được cấu hình, kiểm tra diff và privacy. Review code/test riêng tại Phase 07; chạy lại checks trên final revision tại Phase 08.
- Antigravity chỉ nhận prompt sau verdict `APPROVED` của Phase 01, 03, 04 và 05 đúng version. Prompt, raw report và review lưu trong scope root; `docs/evidence/` chỉ dẫn chiếu theo rubric.

## Rủi ro và phương án xử lý

- Nếu storage write thành công nhưng DB fail, blob rác phải được dọn có log; không coi response thành công.
- W2 thiếu local pipeline/model thì status/report được kiểm bằng integration contract, không báo E2E thực đạt.

## Definition of Ready (điều kiện phát prompt)

- M08 contract/consent decision được owner M01/M08 cùng review.
- Format/size và timeout policy có giá trị cấu hình được duyệt.
- AC và test plan Phase 01/03/04/05 được người dùng duyệt.

**CODEX CHECK RESULT:** DRAFT — ranh giới và phụ thuộc đã mô tả; các quyết định mở/approval khiến task chưa `READY`. **User verdict Phase 05:** PENDING.
