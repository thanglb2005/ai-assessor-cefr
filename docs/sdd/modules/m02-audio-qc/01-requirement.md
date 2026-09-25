# M02 — Audio QC

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M02 / module |
| SCOPE ROOT | `docs/sdd/modules/m02-audio-qc/` |
| OWNER | Thắng (đề xuất W2–W3) |
| LIFECYCLE | proposed |
| PHASE 01 | DRAFT — chờ người dùng duyệt |
| RESEARCH MODE | Đề xuất `SKIP`; người dùng quyết định trong Phase 01 |
| TARGET | W2 |
| RELATED SCOPES | contract chung; M01 cung cấp audio ref |
| SOURCE BASIS | [Tài liệu nguồn do nhóm tạo](../../../sources/README.md), [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx); SDD hiện hành quyết định phạm vi, contract và approval của module |
| CODE TARGET | `src/aicefr/audio/`, `src/aicefr/qc/` — đề xuất, chưa tạo |

## Requirement (Yêu cầu)

**Mục tiêu:** Chuẩn hóa đầu vào kỹ thuật và trả kết quả QC đo được trước khi chạy ASR.

**Trong phạm vi:** Giải mã format được duyệt; đo thời lượng/silence/clipping và chỉ số có thể tái lập; `PASS/REVIEW/REJECT` cùng reason code/version.

**Ngoài phạm vi W2–W3:** Chẩn đoán phát âm, điểm CEFR, suy diễn chất lượng người nói từ thiết bị.

| ID | Functional Requirement (Yêu cầu chức năng) |
| --- | --- |
| M02-FR-001 | Audio lỗi/không hỗ trợ/quá ngắn được trả `REJECT` hoặc `REVIEW` với reason code; không gọi ASR sau từ chối. |
| M02-FR-002 | Kết quả QC có các giá trị đã đo, đơn vị, config version; raw audio bất biến. |

## Acceptance Criteria (Tiêu chí chấp nhận)

| ID | Bằng chứng phải kiểm tra |
| --- | --- |
| M02-AC-001 | Fixture rỗng/hỏng/quá ngắn cho kết quả xác định, không tạo score hay transcript. |
| M02-AC-002 | Fixture hợp lệ trả `PASS` và metadata; chạy lặp với cùng config cho cùng kết quả phần tất định. |

## W2 scope note (Ranh giới tuần 2)

W2 đo các thuộc tính audio kỹ thuật trước ASR; ngưỡng, format và sample rate sẽ nằm trong config có version sau khi nhóm chọn, không tự đặt số trong tài liệu.

## Điều kiện chung và câu hỏi mở

- Unit test dùng fixture tạo bởi nhóm; smoke/integration chỉ dùng audio có quyền sử dụng. Fixture kiểm thử không là số liệu thực nghiệm; không log audio, transcript hoặc PII.
- ID, enum, schema/API xuyên module phải được cả owner liên quan review; mọi feature code chỉ bắt đầu sau khi Phase 01, 03, 04 và 05 của **module này** được người dùng duyệt theo thứ tự.
- Chủ dự án đã chọn 5 tiêu chí độc thoại làm bản nháp W2; rubric học thuật vẫn cần xác minh. Giữ field `Interaction=null` cùng lý do `insufficient_evidence` cho độc thoại. Dữ liệu/model và lịch 3 tuần xem [roadmap](../../../plan/three-week-roadmap.md).

