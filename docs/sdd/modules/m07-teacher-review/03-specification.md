# M07 — 03 Specification (Đặc tả)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M07 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Nguyên. **Cơ sở:** [Nguồn đề tài do nhóm tạo](../../../sources/README.md) và [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx). **Mục tiêu W2:** W2 chốt contract review reason/state/audit với M05/M06/M08; triển khai hàng đợi và hành động giảng viên ở W3.

## Boundary và hợp đồng đầu vào/đầu ra

| Artifact/boundary | Trường hoặc invariant bắt buộc | Owner/consumer |
| --- | --- | --- |
| ReviewCandidate | response ID, reason codes từ QC/ASR/scoring, source versions, status | M02/M03/M05 → M07 |
| ReviewState | `PENDING/IN_REVIEW/APPROVED/OVERRIDDEN/REJECTED`, revision để chống ghi đè | M07/M08 → M06 |
| ReviewDecision | teacher pseudonym, action, old/new result, reason, timestamp, audit ID | M07 → M08/M06 |
| W2 interface pack | schema/reason map và wireframe không chứa dữ liệu thật; chưa có review action runtime | M07 → M06/M08 |

## Hành vi có thể kiểm tra

- W2 chỉ soạn hợp đồng: reason code nào tạo candidate và state nào báo cáo M06 hiển thị; không đánh dấu review đã hoạt động.
- W3 route bài lỗi/không chắc chắn vào queue có owner teacher; chỉ teacher được duyệt/sửa với reason.
- `teacher_verified=true` chỉ sau action thật lưu audit, không suy từ confidence hay test double.
- Update dùng revision/lock để tránh hai teacher sửa đè im lặng.

## Lỗi, thiếu dữ liệu và phục hồi

- Không có quyền hoặc stale revision: từ chối action, giữ lịch sử.
- Thiếu reason khi override: từ chối, không đổi teacher final result.
- Audit write lỗi: rollback decision/state, không hiển thị verified.

## Quyền, riêng tư và giao diện

- Role teacher do M08 kiểm; student chỉ được xem report của mình qua M01.
- Audit không chứa transcript/audio/PII; reviewer pseudonym có thể truy trách nhiệm nội bộ theo quyền.
- Queue UI có trạng thái loading/empty/error và không lộ bài của owner khác.

## Trace Requirement → AC

| Requirement | Acceptance Criteria | Cách quan sát |
| --- | --- | --- |
| M07-FR-001 | M07-AC-001 | Reason→queue, lock/stale revision |
| M07-FR-002 | M07-AC-002 | Role check và audit action thật |

## Quyết định còn mở

- Teacher nào có quyền duyệt bài của lớp nào?
- Có yêu cầu hai giảng viên đồng duyệt/giải quyết bất đồng trong MVP 3 tuần không?
- Reason code nào đẩy bài vào review W2/W3?

**CODEX CHECK RESULT:** DRAFT — đã đối chiếu FR/AC và ranh giới M07; chưa có verdict Phase 01, hợp đồng liên module và dữ liệu W2 cần review. **User verdict Phase 03:** PENDING.
