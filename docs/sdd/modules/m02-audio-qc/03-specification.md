# M02 — 03 Specification (Đặc tả)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M02 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Thắng. **Cơ sở:** [Nguồn đề tài do nhóm tạo](../../../sources/README.md) và [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx). **Mục tiêu W2:** Giải mã audio được phép, đo chất lượng kỹ thuật có version và chặn đầu vào không dùng được trước ASR.

## Boundary và hợp đồng đầu vào/đầu ra

| Artifact/boundary | Trường hoặc invariant bắt buộc | Owner/consumer |
| --- | --- | --- |
| AudioInput | `audio_ref`, content hash, declared format, task/response ID; không mang tên người học | M01/M08 → M02 |
| DecodedAudio | sample rate, channels, duration, số mẫu; không ghi đè raw blob | M02 internal → M03 |
| QCResult | `PASS/REVIEW/REJECT`, measured fields + unit, reason codes, `qc_config_version` | M02 → M03/M01 |
| QCConfig | format whitelist và ngưỡng thời lượng/silence/clipping có version; số cụ thể OPEN | M08 config → M02 |

## Hành vi có thể kiểm tra

- Kiểm tra file thực, giới hạn byte và decoder trước khi đo; đối chiếu declared format với decoded format.
- Đo thời lượng, tỉ lệ silence/clipping trên bản decode; các đơn vị và thuật toán được ghi trong config/version.
- `REJECT` không gọi M03; `REVIEW` được chuyển tiếp hay dừng phải có policy và reason rõ; raw audio vẫn bất biến.
- Không dùng QC để suy diễn trình độ, phát âm, accent hoặc điểm CEFR.

## Lỗi, thiếu dữ liệu và phục hồi

- File rỗng, hỏng, không hỗ trợ hoặc không giải mã được trả `REJECT` với reason không chứa raw data.
- Giá trị đo không xác định/null được gắn missing reason; không biến thành 0.
- Decoder timeout/resource limit: trả failure có thể xử lý, không giữ tiến trình treo.

## Quyền, riêng tư và giao diện

- Đọc blob qua M08, không nhận path tùy ý từ HTTP.
- Log chỉ chứa response ID, status, reason và version; không ghi âm thanh/transcript.
- Config QC được review và version; không thay ngưỡng ngầm làm thay đổi kết quả.

## Trace Requirement → AC

| Requirement | Acceptance Criteria | Cách quan sát |
| --- | --- | --- |
| M02-FR-001 | M02-AC-001 | Lỗi audio có reason, không ASR/score |
| M02-FR-002 | M02-AC-002 | Audio hợp lệ có metadata/config và kết quả lặp |

## Quyết định còn mở

- Danh sách định dạng, giới hạn byte/duration và bộ decoder nào được duyệt?
- Ngưỡng QC và cách xử lý `REVIEW` trước ASR?
- Có cần resample về sample rate cố định không, và thư viện nào được phép?

**CODEX CHECK RESULT:** DRAFT — đã đối chiếu FR/AC và ranh giới M02; chưa có verdict Phase 01, hợp đồng liên module và dữ liệu W2 cần review. **User verdict Phase 03:** PENDING.
