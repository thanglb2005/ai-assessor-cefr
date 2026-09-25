# M04 — 05 Plan & Task Readiness (Kế hoạch)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M04 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Sang. **Phạm vi source:** `src/aicefr/features/ (đề xuất)` (chưa tạo). Implementation W2 được phát triển trong repo dự án theo Specification sau khi được duyệt.

## Kiến trúc và thứ tự triển khai

- Soạn catalogue W2 gồm công thức, unit, nguồn và missing policy, chờ review.
- Viết extractor thuần nhận typed input, không đọc file/DB trực tiếp; I/O nằm ở orchestration.
- Viết tests cho null/NaN/version mismatch và scan output/log privacy.

## Phụ thuộc và bàn giao

- M02 cung cấp duration/QC; M03 cung cấp transcript/timestamp/quality flags có version.
- M05 chỉ đọc feature đủ điều kiện; không tự suy criterion score từ proxy.

## Required checks và review

- Trước task: đối chiếu `01` → `03` → `04`, chốt các quyết định `OPEN`, xác nhận đường dẫn được phép sửa và baseline/fingerprint của repo dự án. Git đã được khởi tạo trong repo dự án ngày 25/09/2026; dùng commit/diff và revision thực làm evidence sau khi có baseline commit.
- Khi triển khai: type hints cho contract public; validation tại boundary; hàm logic nhỏ và có test; không truyền trạng thái bằng dict vô kiểu giữa module. Mỗi dependency, model và download phải có lý do gắn với task cùng provenance rõ.
- Sau task: chạy các test ID của task, `ruff`/typecheck nếu được cấu hình, kiểm tra diff và privacy. Review code/test riêng tại Phase 07; chạy lại checks trên final revision tại Phase 08.
- Antigravity chỉ nhận prompt sau verdict `APPROVED` của Phase 01, 03, 04 và 05 đúng version. Prompt, raw report và review lưu trong scope root; `docs/evidence/` chỉ dẫn chiếu theo rubric.

## Rủi ro và phương án xử lý

- Các proxy ngôn ngữ có construct coverage yếu; tách feature kỹ thuật khỏi kết luận CEFR.
- Mất timestamp hoặc ASR sai ảnh hưởng phép đo; fail closed bằng null/reason.

## Definition of Ready (điều kiện phát prompt)

- Catalogue feature, công thức và missing policy được review bởi Sang/Thắng.
- M02/M03 contracts có version; AC/test đã được duyệt.

**CODEX CHECK RESULT:** DRAFT — ranh giới và phụ thuộc đã mô tả; các quyết định mở/approval khiến task chưa `READY`. **User verdict Phase 05:** PENDING.
