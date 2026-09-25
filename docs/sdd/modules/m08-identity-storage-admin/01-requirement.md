# M08 — Identity, Storage & Admin

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M08 / module |
| SCOPE ROOT | `docs/sdd/modules/m08-identity-storage-admin/` |
| OWNER | Thắng (đề xuất W2–W3) |
| LIFECYCLE | proposed |
| PHASE 01 | DRAFT — chờ người dùng duyệt |
| RESEARCH MODE | Đề xuất `SKIP`; người dùng quyết định trong Phase 01 |
| TARGET | W2–W3 |
| RELATED SCOPES | contract chung; cung cấp cho M01/M07 |
| SOURCE BASIS | [Tài liệu nguồn do nhóm tạo](../../../sources/README.md), [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx); quyết định W2 là bản mới, không kế thừa code/approval cũ |
| CODE TARGET | `src/aicefr/auth/`, `src/aicefr/storage/`, `src/aicefr/infra/` — đề xuất, chưa tạo |

## Requirement (Yêu cầu)

**Mục tiêu:** Bảo vệ tài khoản, consent, bài nộp và audit trong lưu trữ local.

**Trong phạm vi:** Account/role/session, consent, SQLite/BlobStore local, lưu/xuất/xóa tối thiểu, admin tạo tài khoản, audit không chứa PII.

**Ngoài phạm vi W2–W3:** SSO, multi-tenant production, cloud storage, vận hành model registry phức tạp.

| ID | Functional Requirement (Yêu cầu chức năng) |
| --- | --- |
| M08-FR-001 | Không tự đăng ký role teacher/admin; consent có version và trạng thái rút; quyền dữ liệu theo chủ sở hữu. |
| M08-FR-002 | Dữ liệu và audit được lưu nhất quán, xuất/xóa theo request có kiểm tra quyền và reason; log không chứa transcript/PII. |

## Acceptance Criteria (Tiêu chí chấp nhận)

| ID | Bằng chứng phải kiểm tra |
| --- | --- |
| M08-AC-001 | Role student không đọc bài người khác; rút consent chặn nộp mới và quy trình xóa/retention có test. |
| M08-AC-002 | Lưu/đọc response và audit sau restart local; secret không nằm trong Git hoặc tài liệu. |

## W2 scope note (Ranh giới tuần 2)

W2 tạo ranh giới tài khoản/consent/owner và lưu trữ local tối thiểu. Chính sách retention, mã hóa và backup của dữ liệu thật vẫn cần quyết định riêng; demo không được làm bằng chứng tuân thủ dữ liệu thật.

## Điều kiện chung và câu hỏi mở

- Unit test dùng fixture tạo bởi nhóm; smoke/integration chỉ dùng audio có quyền sử dụng. Fixture kiểm thử không là số liệu thực nghiệm; không log audio, transcript hoặc PII.
- ID, enum, schema/API xuyên module phải được cả owner liên quan review; mọi feature code chỉ bắt đầu sau khi Phase 01, 03, 04 và 05 của **module này** được người dùng duyệt theo thứ tự.
- Chủ dự án đã chọn 5 tiêu chí độc thoại làm bản nháp W2; rubric học thuật vẫn cần xác minh. Giữ field `Interaction=null` cùng lý do `insufficient_evidence` cho độc thoại. Dữ liệu/model và lịch 3 tuần xem [roadmap](../../../plan/three-week-roadmap.md).

