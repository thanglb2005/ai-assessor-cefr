# M04 — Features

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M04 / module |
| SCOPE ROOT | `docs/sdd/modules/m04-features/` |
| OWNER | Sang (đề xuất W2–W3) |
| LIFECYCLE | proposed |
| PHASE 01 | DRAFT — chờ người dùng duyệt |
| RESEARCH MODE | Đề xuất `SKIP`; người dùng quyết định trong Phase 01 |
| TARGET | W2 |
| RELATED SCOPES | M02 QC, M03 transcript/timestamp |
| SOURCE BASIS | [Tài liệu nguồn do nhóm tạo](../../../sources/README.md), [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx); SDD hiện hành quyết định phạm vi, contract và approval của module |
| CODE TARGET | `src/aicefr/features/` — đề xuất, chưa tạo |

## Requirement (Yêu cầu)

**Mục tiêu:** Tính các đặc trưng bài nói có định nghĩa, version và lý do khi thiếu dữ liệu.

**Trong phạm vi:** FeatureSet có tên/giá trị/đơn vị/nguồn; fluency/lexical/timing trong phạm vi dữ liệu hỗ trợ; coverage từng criterion.

**Ngoài phạm vi W2–W3:** Tự chấm CEFR; gán đặc trưng không đo được từ transcript kém tin cậy.

| ID | Functional Requirement (Yêu cầu chức năng) |
| --- | --- |
| M04-FR-001 | Mỗi feature có `feature_version`, input provenance và `missing_reason` khi không tính được. |
| M04-FR-002 | Dữ liệu thiếu hoặc ASR bất định không được âm thầm thay bằng 0 hay trung bình. |

## Acceptance Criteria (Tiêu chí chấp nhận)

| ID | Bằng chứng phải kiểm tra |
| --- | --- |
| M04-AC-001 | Fixture có transcript/timestamp cho feature tất định; thiếu timestamps trả null + reason cho feature cần timing. |
| M04-AC-002 | FeatureSet không chứa PII và chỉ số unsupported không bị báo là đã đo. |

## W2 scope note (Ranh giới tuần 2)

W2 ưu tiên đặc trưng đo được từ audio/transcript/timestamp sẵn có; mỗi giá trị phải mang nguồn và đơn vị. Không suy Phonology hoặc Accuracy chỉ từ một proxy kỹ thuật.

## Điều kiện chung và câu hỏi mở

- Unit test dùng fixture tạo bởi nhóm; smoke/integration chỉ dùng audio có quyền sử dụng. Fixture kiểm thử không là số liệu thực nghiệm; không log audio, transcript hoặc PII.
- ID, enum, schema/API xuyên module phải được cả owner liên quan review; mọi feature code chỉ bắt đầu sau khi Phase 01, 03, 04 và 05 của **module này** được người dùng duyệt theo thứ tự.
- Chủ dự án đã chọn 5 tiêu chí độc thoại làm bản nháp W2; rubric học thuật vẫn cần xác minh. Giữ field `Interaction=null` cùng lý do `insufficient_evidence` cho độc thoại. Dữ liệu/model và lịch 3 tuần xem [roadmap](../../../plan/three-week-roadmap.md).

