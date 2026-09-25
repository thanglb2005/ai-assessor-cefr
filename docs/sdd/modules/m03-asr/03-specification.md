# M03 — 03 Specification (Đặc tả)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M03 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Sang. **Cơ sở:** [Nguồn đề tài do nhóm tạo](../../../sources/README.md) và [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx). **Mục tiêu W2:** Cung cấp transcript local có provenance và trạng thái bất định; W2 smoke trên audio có quyền sử dụng nếu runtime/model sẵn sàng.

## Boundary và hợp đồng đầu vào/đầu ra

| Artifact/boundary | Trường hoặc invariant bắt buộc | Owner/consumer |
| --- | --- | --- |
| AsrInput | DecodedAudio/QCResult từ M02, response ID, language hint; không nhận URL ngoài | M02 → M03 |
| Transcript | text verbatim, segment/word timestamps nullable, quality flags, `asr_model`, `transcript_version`, source hash | M03 → M04/M06 |
| AsrStatus | `OK/ASR_FAILED/UNRELIABLE/NOT_RUN`; reason codes riêng | M03 → pipeline/M07 |
| AsrEngine port | local adapter riêng; test double chỉ cho test, luôn có marker test | M03 internal |

## Hành vi có thể kiểm tra

- Chỉ chạy khi QC policy cho phép; xử lý bằng model local được cấu hình, lưu exact model identifier/checksum và decode config.
- Giữ filler và thứ tự lời nói trong bản transcript gốc; không thêm từ để làm đẹp câu.
- Word timestamp/confidence chỉ điền khi engine thực cung cấp; segment-only không được khai là word-level.
- Không tự động tải model từ mạng khi chạy smoke mặc định; nếu model chưa có, trả `NOT_RUN`/reason và W2 gate chưa đạt.

## Lỗi, thiếu dữ liệu và phục hồi

- ASR fail/timeout hoặc transcript rỗng khi audio có tiếng: trả status/reason, không tạo transcript `OK`.
- Nghi hallucination/low reliability: `UNRELIABLE`, chặn feature/scoring đòi text đáng tin hoặc gửi review.
- Timestamp âm, đảo thứ tự hoặc vượt duration: reject artifact và giữ diagnostic metadata.

## Quyền, riêng tư và giao diện

- Chỉ xử lý audio được phép; không gửi audio/transcript lên cloud mặc định.
- Log không chứa raw transcript hay audio; lưu artifact dưới M08 với owner/access policy.
- Test double phải hiện rõ `test_only=true` và không xuất hiện ở báo cáo thực nghiệm.

## Trace Requirement → AC

| Requirement | Acceptance Criteria | Cách quan sát |
| --- | --- | --- |
| M03-FR-001 | M03-AC-001, M03-AC-002 | Adapter/version và timestamp nullable đúng nguồn |
| M03-FR-002 | M03-AC-001, M03-AC-002 | Lỗi/không đáng tin không đi vào score |

## Quyết định còn mở

- Máy W2 có CPU/GPU/RAM nào và model local nào đã có hợp lệ?
- Chọn engine/model/version nào sau khi kiểm license và runtime?
- Cần word timestamp W2 hay segment timestamp đủ cho report ban đầu?

**CODEX CHECK RESULT:** DRAFT — đã đối chiếu FR/AC và ranh giới M03; chưa có verdict Phase 01, hợp đồng liên module và dữ liệu W2 cần review. **User verdict Phase 03:** PENDING.
