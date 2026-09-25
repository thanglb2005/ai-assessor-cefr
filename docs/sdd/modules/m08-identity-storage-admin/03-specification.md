# M08 — 03 Specification (Đặc tả)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M08 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Thắng. **Cơ sở:** [Nguồn đề tài do nhóm tạo](../../../sources/README.md) và [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx). **Mục tiêu W2:** Cung cấp account/role/consent, owner check và storage local tối thiểu cho luồng W2; dữ liệu thật chờ data governance được duyệt.

## Boundary và hợp đồng đầu vào/đầu ra

| Artifact/boundary | Trường hoặc invariant bắt buộc | Owner/consumer |
| --- | --- | --- |
| Actor/Session | actor ID giả danh, role `student/teacher/admin`, session expiry; không tin role client | M08 → M01/M07 |
| ConsentRecord | participant ID giả danh, consent version, trạng thái active/withdrawn, thời điểm; quyền theo actor | M08 → M01 |
| BlobStore/ResponseRepo | audio/artifact refs không chứa PII, owner, checksum, status/revision, atomic save/read | M08 → M01–M07 |
| AuditEvent | actor pseudonym, action, object ID, timestamp, reason, before/after ref; append-only | M08 → M07/admin |

## Hành vi có thể kiểm tra

- Không tự đăng ký teacher/admin từ request; admin có quyền tạo account qua đường được duyệt, mật khẩu không lưu plaintext.
- Consent active đúng version là điều kiện nộp; rút consent chặn nộp mới ngay, xử lý dữ liệu tồn tại theo retention/deletion policy đã duyệt.
- Owner check ở mọi read/write response/report/blob; raw audio và identity map tách khỏi source/Git; config path không hard-code máy cá nhân.
- SQLite/BlobStore local giữ checksum/version; audit action quan trọng không được mất khi restart; W2 chỉ dùng account/data thử có quyền.

## Lỗi, thiếu dữ liệu và phục hồi

- Session hết hạn/sai role trả lỗi quyền trước truy dữ liệu.
- DB/blob write fail: rollback hoặc ghi trạng thái recovery, không tạo Response trỏ blob không tồn tại.
- Rút consent/xóa dữ liệu thật chưa có chính sách: không tuyên bố đã xử lý hoàn chỉnh; đánh dấu pending owner decision.

## Quyền, riêng tư và giao diện

- Không log password, token, audio, transcript hoặc PII; `.env`, DB, blobs, identity map ngoài Git.
- Mã hóa at rest, backup/key recovery và retention là quyết định triển khai cho dữ liệu thật, không suy từ SQLite mặc định.
- Export/delete phải kiểm quyền và có audit; scope W2 chỉ chuẩn bị contract/test, không vận hành trên dữ liệu thật khi chưa duyệt.

## Trace Requirement → AC

| Requirement | Acceptance Criteria | Cách quan sát |
| --- | --- | --- |
| M08-FR-001 | M08-AC-001 | Role/consent/owner chặn truy cập trái quyền |
| M08-FR-002 | M08-AC-002 | Persistence/audit sau restart, secret ngoài Git |

## Quyết định còn mở

- Cơ chế login/session demo W2 và quản trị account nào được duyệt?
- Nơi lưu dữ liệu thật, encryption/key/backup/retention có người chịu trách nhiệm và approval chưa?
- Thời hạn/session expiry và chính sách password cụ thể?
- Xuất/xóa dữ liệu là W3 bắt buộc hay làm sau khi data plan được duyệt?

**CODEX CHECK RESULT:** DRAFT — đã đối chiếu FR/AC và ranh giới M08; chưa có verdict Phase 01, hợp đồng liên module và dữ liệu W2 cần review. **User verdict Phase 03:** PENDING.
