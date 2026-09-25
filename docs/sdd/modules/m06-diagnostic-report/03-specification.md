# M06 — 03 Specification (Đặc tả)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M06 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Nguyên. **Cơ sở:** [Nguồn đề tài do nhóm tạo](../../../sources/README.md) và [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx). **Mục tiêu W2:** Tạo báo cáo cho một bài nói với dẫn chứng truy được và nhãn kết quả chưa duyệt; không tạo nhận xét khi không có evidence.

## Boundary và hợp đồng đầu vào/đầu ra

| Artifact/boundary | Trường hoặc invariant bắt buộc | Owner/consumer |
| --- | --- | --- |
| ReportInput | Response/QC/Transcript/FeatureSet/Assessment refs có cùng response ID và version; ReviewDecision nullable | M01–M05/M07 → M06 |
| EvidenceRef | evidence ID, source artifact/version, mốc thời gian/word ref nullable, criterion liên quan | M03/M04 → M06 |
| DiagnosticReport | response ID, status, overall estimate nullable, năm criterion coverage/evidence (không score/band riêng), Interaction null/reason, comments/evidence refs, limitations, generated_at, versions | M06 → M01 UI |
| VerificationState | `teacher_verified=false` trước action M07; true chỉ khi có review audit ref thật | M07/M08 → M06 |

## Hành vi có thể kiểm tra

- Chỉ phát comment/priority khi EvidenceRef tồn tại, thuộc cùng response và phù hợp criterion; text template có version, không dùng LLM tự do W2.
- Nếu M05 `NOT_EVALUATED`, báo cáo hiển thị “chưa đủ điều kiện ước lượng” kèm reason, vẫn có thể hiển thị QC/ASR diagnostic được phép. Khi M05 hợp lệ, chỉ hiển thị overall score/band và coverage/evidence năm tiêu chí; không hiển thị năm điểm lặp.
- Evidence time ref không vượt audio duration; liên kết nguồn phiên bản chính xác, không tạo timestamp từ lời nhận xét.
- Tách estimated AI result khỏi teacher final result; chưa có M07 action thì giữ provisional và `teacher_verified=false`.

## Lỗi, thiếu dữ liệu và phục hồi

- EvidenceRef mồ côi/stale hoặc khác response: bỏ comment liên quan và ghi thiếu evidence, không hiển thị nhận xét khẳng định.
- Transcript/timestamp thiếu: bỏ link tương ứng; report không crash, reason rõ.
- Report input conflict version: từ chối tạo bản “hoàn tất” và yêu cầu tái tổng hợp.

## Quyền, riêng tư và giao diện

- M06 không tự quyết định quyền xem; M01/M08 kiểm owner/role ở boundary truy xuất, report chỉ chứa ID giả danh.
- Text report không đưa raw transcript/audio/PII vào log; UI nhấn rõ kết quả low-stakes/provisional.
- Evidence kỹ thuật của sản phẩm ở đây khác `docs/evidence/` hồ sơ theo rubric.

## Trace Requirement → AC

| Requirement | Acceptance Criteria | Cách quan sát |
| --- | --- | --- |
| M06-FR-001 | M06-AC-001, M06-AC-002 | Comment có evidence ref hợp lệ và đúng source version |
| M06-FR-002 | M06-AC-002, M06-AC-003 | AI/provisional khác final; chỉ overall score/band + coverage, teacher_verified mặc định false |

## Quyết định còn mở

- Danh sách comment template W2 nào được giảng viên xem trước?
- Có giới hạn tối đa priority W2 không, và dựa trên quy tắc nào?
- Vị trí/nội dung câu cảnh báo kết quả chưa duyệt trong UI?

**CODEX CHECK RESULT:** DRAFT — đã đối chiếu FR/AC và ranh giới M06; chưa có verdict Phase 01, hợp đồng liên module và dữ liệu W2 cần review. **User verdict Phase 03:** PENDING.
