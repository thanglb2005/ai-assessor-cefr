# M02 — Audio QC

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M02 / module |
| SCOPE ROOT | docs/sdd/modules/m02-audio-qc/ |
| OWNER | Thắng |
| LIFECYCLE | proposed |
| PHASE 01 | APPROVED v0.2 — 28/09/2026 |
| RESEARCH MODE | RUN — người dùng chọn tại Phase 01 |
| TARGET | W2 |
| RELATED SCOPES | M01 cung cấp audio ref; M08 kiểm soát owner/storage; M03 nhận DecodedAudio và QCResult |
| SOURCE BASIS | docs/sources/README.md, báo cáo W1; SDD đã duyệt của consumer quyết định contract liên module |
| CODE TARGET | src/aicefr/audio/, src/aicefr/qc/ |

## Requirement (Yêu cầu)

Mục tiêu: Chuẩn hóa đầu vào kỹ thuật và trả kết quả QC đo được trước khi chạy ASR.

Trong phạm vi W2: Giải mã định dạng được duyệt; chuyển thành PCM float32, mono, 16 kHz; đo thời lượng, silence/clipping và các chỉ số có cấu hình version; trả PASS/REVIEW/REJECT cùng reason code. Raw audio không bị sửa.

Ngoài phạm vi W2–W3: Chẩn đoán phát âm, điểm CEFR, suy diễn chất lượng người nói từ thiết bị.

| ID | Functional Requirement (Yêu cầu chức năng) |
| --- | --- |
| M02-FR-001 | Audio rỗng, hỏng, không hỗ trợ, vượt giới hạn hoặc không đạt QC policy trả REJECT hoặc REVIEW với reason code; REJECT không gọi ASR. |
| M02-FR-002 | DecodedAudio có PCM float32 mono 16 kHz; QCResult có giá trị đo, đơn vị và config version; raw audio giữ nguyên. |

## Acceptance Criteria (Tiêu chí chấp nhận)

| ID | Bằng chứng phải kiểm tra |
| --- | --- |
| M02-AC-001 | Fixture rỗng/hỏng/quá ngắn cho kết quả xác định, có reason; không gọi ASR và không tạo score/transcript. |
| M02-AC-002 | Fixture hợp lệ trả PASS, metadata có đơn vị/config version; chạy lặp với cùng config cho cùng kết quả phần tất định. |

## W2 scope note (Ranh giới tuần 2)

Thắng đã duyệt Phase 01: đầu ra M02 phải là PCM float32 mono 16 kHz theo contract consumer M03 đã duyệt. Danh sách format đầu vào, giới hạn tài nguyên và giá trị QC threshold phải được duyệt tại Phase 03; không tự gán giá trị sản phẩm mặc định.

## Điều kiện chung

- Unit test dùng fixture tạo bởi nhóm; không commit audio thật, transcript, PII hay secret.
- Hệ thống không dùng QC để suy ra trình độ, accent hoặc điểm CEFR.
- Schema/API/reason code dùng chung cần owner M03/M04 review trước Phase 05.
- Feature code chỉ bắt đầu sau khi Phase 01, 03, 04, 05 của module được người dùng duyệt tuần tự.

## Phase 01 record

PHASE RECORD ID: M02-01-A1
PHASE: 01 — Requirement
SUBJECT: 01-requirement.md v0.2
CODEX CHECK RESULT: PASS — FR/AC có thể kiểm tra; scope audio kỹ thuật được tách khỏi chấm CEFR; dependency M03 được nêu rõ.
CODEX RECOMMENDATION: RECOMMEND APPROVAL
USER VERDICT: APPROVED theo đề xuất
VERIFIED/APPROVED BY: User (Thắng)
USER VERDICT AT: 28/09/2026
RESEARCH MODE: RUN — decoder, format, resampling và giới hạn tài nguyên
DECISION: M02 xuất PCM float32 mono 16 kHz; danh sách format và QC thresholds chờ Phase 03.
NEXT ACTION: Phase 02 — Research, sau đó Phase 03 — Specification
