# M05 — 05 Plan & Task Readiness (Kế hoạch)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M05 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Sang. **Scope source mới:** `src/aicefr/scoring/ (đề xuất)` (chưa tạo). Mã nguồn repo tiền nhiệm chỉ được khảo sát ở mức chức năng; implementation W2 viết trong repo mới theo Specification sau khi được duyệt.

## Kiến trúc và thứ tự triển khai

- Chốt output schema và refusal path; dùng [scoring audit](../../../sources/scoring-audit.md) để xác định ứng viên Ridge/DeBERTa do nhóm tạo và các gap. Không chuyển code cũ.
- Thiết kế model loader chỉ nhận artifact có manifest/hash/config và đúng `unit_of_inference`, feature order, ASR/VAD; tách predict overall, band mapping và review policy. DeBERTa là nhánh tích hợp riêng, không mặc định W2.
- Ưu tiên tích hợp mới Ridge v2 do nhóm đã huấn luyện cho overall estimate sau khi kiểm quyền, hash và tương thích pipeline; chạy test/smoke mới và lưu provenance. Nếu artifact không khớp, trả `NOT_EVALUATED`. Năm criterion score độc lập cần rubric/nhãn riêng, hiện chưa có.

## Phụ thuộc và bàn giao

- M04 FeatureSet và M06 Report cần thống nhất criterion coverage/evidence IDs.
- Data owner xác nhận quyền dùng model/nhãn/audio; giảng viên cần duyệt rubric trước khi công bố năm điểm tiêu chí riêng. Ridge v2 là artifact đã có của nhóm, nhưng test/metric bản tham chiếu không thay kiểm tra của app mới.

## Required checks và review

- Trước task: đối chiếu `01` → `03` → `04`, chốt các quyết định `OPEN`, xác nhận đường dẫn được phép sửa và baseline/fingerprint của repo mới. Git đã được khởi tạo trong repo mới ngày 25/09/2026; dùng commit/diff và revision thực làm evidence sau khi có baseline commit.
- Khi triển khai: type hints cho contract public; validation tại boundary; hàm logic nhỏ và có test; không truyền trạng thái bằng dict vô kiểu giữa module. Không thêm dependency/model/download chỉ vì repo cũ đã có.
- Sau task: chạy các test ID của task, `ruff`/typecheck nếu được cấu hình, kiểm tra diff và privacy. Review code/test riêng tại Phase 07; chạy lại checks trên final revision tại Phase 08.
- Antigravity chỉ nhận prompt sau verdict `APPROVED` của Phase 01, 03, 04 và 05 đúng version. Prompt, raw report và review lưu trong scope root; `docs/evidence/` chỉ dẫn chiếu theo rubric.

## Rủi ro và phương án xử lý

- Ridge đã có overall model, nhưng dữ liệu/approval để chứng minh band trên pipeline và population mới chưa xác nhận; không xóa công sức cũ hoặc gọi metric lịch sử là kết quả mới.
- Model artifact không đáng tin hoặc không tái lập: từ chối load; giữ manifest/checksum/config.

## Definition of Ready (điều kiện phát prompt)

- Quyền và tương thích Ridge v2 được xác minh cho task phát overall; task refusal path có thể triển khai độc lập. Rubric/nhãn riêng là gate của điểm tiêu chí độc lập.
- Band mapping/review thresholds được quyết định; nếu OPEN thì không phát prompt score thật.
- Phase 01/03/04/05 đúng version được duyệt.

**CODEX CHECK RESULT:** DRAFT — ranh giới và phụ thuộc đã mô tả; các quyết định mở/approval khiến task chưa `READY`. **User verdict Phase 05:** PENDING.
