# M08 — Identity, Storage & Admin

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M08 / module |
| SCOPE ROOT | docs/sdd/modules/m08-identity-storage-admin/ |
| OWNER | Thắng |
| LIFECYCLE | proposed |
| PHASE 01 | APPROVED v0.2 — 28/09/2026 |
| RESEARCH MODE | RUN — người dùng chọn tại Phase 01 |
| TARGET | W2 core; export/xóa dữ liệu thật phụ thuộc W3 policy |
| RELATED SCOPES | M01 nhận auth/consent/owner/storage contracts; M07 dùng teacher role/audit ở W3 |
| SOURCE BASIS | docs/sources/README.md, báo cáo W1; SDD đã duyệt của consumer quyết định contract liên module |
| CODE TARGET | src/aicefr/auth/, src/aicefr/storage/, src/aicefr/infra/ |

## Requirement (Yêu cầu)

Mục tiêu: Bảo vệ account, consent, response ownership và audit trong local storage.

Trong phạm vi W2: Account/role/session service, consent versioning, owner checks, SQLite metadata, local BlobStore, audit và restart-safe persistence. W2 chỉ dùng fixture/tài khoản giả danh do nhóm tạo; không dùng dữ liệu người học thật.

Ngoài phạm vi W2: SSO, multi-tenant production, cloud storage, mã hóa/backup/key recovery cho dữ liệu thật, retention policy và thao tác export/xóa dữ liệu thật. Các mục này cần data-governance approval riêng trước W3.

| ID | Functional Requirement (Yêu cầu chức năng) |
| --- | --- |
| M08-FR-001 | Không cho client tự đăng ký role teacher/admin; consent có version và trạng thái active/withdrawn; mọi truy cập response/blob phải kiểm tra owner. Rút consent chặn submit mới. |
| M08-FR-002 | Response/blob metadata và audit được lưu nhất quán, kiểm tra checksum sau restart; log không chứa password, token, audio, transcript hoặc PII. Không chạy export/xóa dữ liệu thật trong W2. |

## Acceptance Criteria (Tiêu chí chấp nhận)

| ID | Bằng chứng phải kiểm tra |
| --- | --- |
| M08-AC-001 | Student không đọc response/blob của actor khác; consent withdrawn chặn submit mới; dữ liệu fixture hiện có không bị xóa ngầm. |
| M08-AC-002 | Response/blob và audit đọc lại đúng checksum/status sau restart local; secret không nằm trong Git hoặc tài liệu. |

## W2 data boundary

Thắng đã duyệt Phase 01: W2 chỉ dùng fixture và account giả danh; không xử lý dữ liệu thật. Rút consent chặn bài nộp mới nhưng không xóa dữ liệu đang lưu. Export/xóa dữ liệu thật, retention, encryption và backup chỉ được đặc tả sau khi policy/approver được xác định ở W3.

## Điều kiện chung

- Không ghi PII, password, session token, audio hoặc transcript vào log.
- DB, blob files, identity map và secrets nằm ngoài Git/repo; đường dẫn lấy từ cấu hình.
- Contract/schema dùng chung cần owner M01/M07 review trước Phase 05.
- Feature code chỉ bắt đầu sau khi Phase 01, 03, 04, 05 của module được người dùng duyệt tuần tự.

## Phase 01 record

PHASE RECORD ID: M08-01-A1
PHASE: 01 — Requirement
SUBJECT: 01-requirement.md v0.2
CODEX CHECK RESULT: PASS — FR/AC testable; data boundary W2/W3 đã tách; không suy diễn approval cho dữ liệu thật.
CODEX RECOMMENDATION: RECOMMEND APPROVAL
USER VERDICT: APPROVED theo đề xuất
VERIFIED/APPROVED BY: User (Thắng)
USER VERDICT AT: 28/09/2026
RESEARCH MODE: RUN — auth/session, local persistence, atomic blob/audit behavior
DECISION: W2 chỉ dùng fixture/account giả danh; retention và export/xóa thật chờ policy W3.
NEXT ACTION: Phase 02 — Research, sau đó Phase 03 — Specification
