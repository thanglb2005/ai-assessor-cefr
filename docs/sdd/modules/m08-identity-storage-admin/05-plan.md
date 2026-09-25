# M08 — 05 Plan & Task Readiness (Kế hoạch)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M08 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Thắng. **Scope source mới:** `src/aicefr/auth/, src/aicefr/storage/, src/aicefr/infra/ (đề xuất)` (chưa tạo). Mã nguồn repo tiền nhiệm chỉ được khảo sát ở mức chức năng; implementation W2 viết trong repo mới theo Specification sau khi được duyệt.

## Kiến trúc và thứ tự triển khai

- Chốt schema Actor/Consent/Response/Blob/Audit và boundary với M01/M07; quyết định demo-only vs dữ liệu thật.
- Dựng auth/session/consent và repository SQLite/BlobStore local với path config; test quyền, rollback và restart.
- Bổ sung admin tối thiểu và audit; W3 chỉ triển khai export/delete thật sau policy/approval riêng.

## Phụ thuộc và bàn giao

- M01 cần auth/consent/repository trước submit; M07 cần teacher role/audit/revision W3.
- Data management/consent của nguồn đề tài là draft; người dùng/GVHD cần duyệt policy trước dữ liệu thật.

## Required checks và review

- Trước task: đối chiếu `01` → `03` → `04`, chốt các quyết định `OPEN`, xác nhận đường dẫn được phép sửa và baseline/fingerprint của repo mới. Git đã được khởi tạo trong repo mới ngày 25/09/2026; dùng commit/diff và revision thực làm evidence sau khi có baseline commit.
- Khi triển khai: type hints cho contract public; validation tại boundary; hàm logic nhỏ và có test; không truyền trạng thái bằng dict vô kiểu giữa module. Không thêm dependency/model/download chỉ vì repo cũ đã có.
- Sau task: chạy các test ID của task, `ruff`/typecheck nếu được cấu hình, kiểm tra diff và privacy. Review code/test riêng tại Phase 07; chạy lại checks trên final revision tại Phase 08.
- Antigravity chỉ nhận prompt sau verdict `APPROVED` của Phase 01, 03, 04 và 05 đúng version. Prompt, raw report và review lưu trong scope root; `docs/evidence/` chỉ dẫn chiếu theo rubric.

## Rủi ro và phương án xử lý

- Auth/PII/consent là phần nhạy cảm; không dùng Fast Path hoặc hard-code credential.
- SQLite không đồng nghĩa mã hóa/backup; phải ghi cơ chế cụ thể và kiểm trên môi trường thật.

## Definition of Ready (điều kiện phát prompt)

- Owner chốt login/session và demo/data thật; policy storage có approver.
- M01/M07 cùng review schema và permission matrix.
- Phase 01/03/04/05 đúng version được duyệt.

**CODEX CHECK RESULT:** DRAFT — ranh giới và phụ thuộc đã mô tả; các quyết định mở/approval khiến task chưa `READY`. **User verdict Phase 05:** PENDING.
