# M03 — ASR

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M03 / module |
| SCOPE ROOT | `docs/sdd/modules/m03-asr/` |
| OWNER | Sang (đề xuất W2–W3) |
| LIFECYCLE | proposed |
| PHASE 01 | **APPROVED** v0.2 — người dùng (Sang) duyệt ngày 26/09/2026 |
| RESEARCH MODE | **`RUN`** — theo đề xuất trong v0.2; người dùng duyệt Phase 01 không đổi đề xuất |
| TARGET | W2 |
| RELATED SCOPES | M02 `PASS/REVIEW` (DecodedAudio); M04 dùng transcript/timestamp; **M05 — model scoring ràng buộc ASR model** (xem M03-FR-003) |
| SOURCE BASIS | [Tài liệu nguồn do nhóm tạo](../../../sources/README.md), [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx), [kiểm tra scorer/model](../../../sources/scoring-audit.md); SDD hiện hành quyết định phạm vi, contract và approval của module |
| CODE TARGET | `src/aicefr/asr/` — đề xuất, chưa tạo |

## Requirement (Yêu cầu)

**Mục tiêu:** Chép lời bài nói có metadata và mức bất định đủ để các module sau sử dụng an toàn.

**Trong phạm vi:** `AsrEngine` test double chỉ cho kiểm thử và adapter local cho smoke; transcript, timestamp nếu có, model/config version; phát hiện lỗi và nghi ngờ ASR; so khớp ASR model với provenance của model scoring mà M05 dùng.

**Ngoài phạm vi W2–W3:** Tải model/dữ liệu người học lên cloud; dùng test double làm kết quả sản phẩm; cam kết word timestamp nếu engine không cung cấp.

| ID | Functional Requirement (Yêu cầu chức năng) |
| --- | --- |
| M03-FR-001 | Adapter ASR trả transcript có provenance; thiếu timestamp/confidence được biểu diễn rõ bằng status/null/reason. |
| M03-FR-002 | ASR lỗi hoặc nghi hallucination không được biến thành transcript hợp lệ hay score. |
| M03-FR-003 | Transcript ghi `asr_model`, và giá trị này phải khớp `trained_with.asr_model` của model scoring mà M05 dùng. Nếu lệch, transcript mang reason `ASR_VERSION_MISMATCH` để M05 không phát band tự động. |

## Acceptance Criteria (Tiêu chí chấp nhận)

| ID | Bằng chứng phải kiểm tra |
| --- | --- |
| M03-AC-001 | Test double cho output tất định và đánh dấu dữ liệu kiểm thử; failure fixture trả `ASR_FAILED`. |
| M03-AC-002 | Nếu chạy local thật, có smoke evidence về model/version và không có network mặc định; nếu chưa có evidence, trạng thái chỉ là pending. |
| M03-AC-003 | Test với cấu hình ASR khớp và lệch `trained_with.asr_model`: khớp thì không có reason lệch; lệch thì transcript mang `ASR_VERSION_MISMATCH`. |

## Quyết định của owner trong review Phase 01 (26/09/2026)

| ID | Quyết định | Căn cứ |
| --- | --- | --- |
| M03-D-001 | Model ASR mặc định W2 là **`whisper-small`**. | `ridge_resp_v2.json` — ứng viên baseline của M05 — ghi `trained_with.asr_model = "whisper-small"`. Hồ sơ kỹ thuật nội bộ của nhóm chạy `whisper-large-v3-turbo` trong khi model chấm điểm học trên transcript `whisper-small`, nên mọi bài bị gắn lệch phiên bản và chuyển giảng viên. Chọn đúng model từ đầu loại bỏ lệch này thay vì xử lý hậu quả ở M05. Artifact đã được đo SHA-256 `7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a` ngày 26/09/2026, khớp giá trị trong [scoring-audit](../../../sources/scoring-audit.md). |
| M03-D-002 | Giữ nguyên nguyên tắc không tự tải model khi chạy mặc định. Tải `whisper-small` là thao tác có chủ đích, ghi nguồn, checksum và license trong Research. | Tránh tải ngầm qua mạng; bảo toàn provenance của model. |

## W2 scope note (Ranh giới tuần 2)

W2 cần thử local ASR `whisper-small` trên audio có quyền sử dụng và ghi model/version/môi trường; adapter tất định chỉ phục vụ unit/integration test, không thay kết quả ASR thật.

## Điều kiện chung và câu hỏi mở

- Unit test dùng fixture tạo bởi nhóm; smoke/integration chỉ dùng audio có quyền sử dụng. Fixture kiểm thử không là số liệu thực nghiệm; không log audio, transcript hoặc PII.
- ID, enum, schema/API xuyên module phải được cả owner liên quan review; mọi feature code chỉ bắt đầu sau khi Phase 01, 03, 04 và 05 của **module này** được người dùng duyệt theo thứ tự.
- Chủ dự án đã chọn 5 tiêu chí độc thoại làm bản nháp W2; rubric học thuật vẫn cần xác minh. Giữ field `Interaction=null` cùng lý do `insufficient_evidence` cho độc thoại. Dữ liệu/model và lịch 3 tuần xem [roadmap](../../../plan/three-week-roadmap.md).
- **Tác động liên module:** M03-FR-003 tạo phụ thuộc M03 → M05 (đọc `trained_with.asr_model` từ artifact M05 chọn). M05 và M03 cùng owner nên review cùng lượt; không thay đổi hợp đồng của M02/M08.
- **Còn mở cho Research (`RUN`):** engine cụ thể theo máy (`faster-whisper` hay `mlx-whisper`), word timestamp hay segment timestamp, cấu hình máy smoke.

## Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
| --- | --- | --- |
| v0.1 | 25/09/2026 | Bản nháp đầu |
| v0.2 | 26/09/2026 | **APPROVED** Phase 01 ngày 26/09/2026. Owner review: thêm M03-FR-003, M03-AC-003; quyết định M03-D-001 (`whisper-small`), M03-D-002 |
