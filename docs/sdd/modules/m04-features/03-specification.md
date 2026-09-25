# M04 — 03 Specification (Đặc tả)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M04 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Sang. **Cơ sở:** [Nguồn đề tài do nhóm tạo](../../../sources/README.md) và [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx). **Mục tiêu W2:** Trích một tập đặc trưng nhỏ, đo được và truy nguồn; báo thiếu dữ liệu minh bạch.

## Boundary và hợp đồng đầu vào/đầu ra

| Artifact/boundary | Trường hoặc invariant bắt buộc | Owner/consumer |
| --- | --- | --- |
| FeatureInput | Transcript status/version, timestamp/quality flags, QC metrics và response ID | M02/M03 → M04 |
| FeatureValue | name, nullable value, unit, source refs, method/config version, `missing_reason` | M04 → M05/M06 |
| FeatureSet | response ID, `feature_version`, input hashes, criterion coverage metadata | M04 → M05 |
| W2 candidate features | speech duration từ QC; word count từ transcript OK; speaking rate chỉ khi duration/timestamps đủ | M04 internal |

## Hành vi có thể kiểm tra

- Mỗi feature có công thức, đơn vị, nguồn và điều kiện hợp lệ ghi trong implementation/test; không dùng metric chỉ vì có trong repo cũ.
- Nếu transcript lỗi hoặc timestamp thiếu, feature phụ thuộc đó là null + missing_reason; không impute 0/mean.
- Không đổi word count/speaking rate thành điểm Range/Fluency/Accuracy/Phonology; đó là tín hiệu hỗ trợ, chưa đại diện toàn construct.
- FeatureSet mang input artifact hash/version để không trộn output từ transcript/QC khác lần.

## Lỗi, thiếu dữ liệu và phục hồi

- Input version/hash không khớp: reject FeatureSet hoặc tính lại có audit.
- Độ dài 0, chia 0, NaN/infinite: value null + reason; không đưa vào M05 như số hợp lệ.
- ASR UNRELIABLE: feature text bị đánh dấu không đủ tin cậy theo policy.

## Quyền, riêng tư và giao diện

- Không chứa nội dung transcript hoặc token có PII trong FeatureSet/log; chỉ giữ số đo/ref được phép.
- Điều kiện Phonology cần evidence audio chuyên biệt; không phạt accent từ từ khóa hoặc WER.
- Phương thức làm tròn/normalization có version để so kết quả.

## Trace Requirement → AC

| Requirement | Acceptance Criteria | Cách quan sát |
| --- | --- | --- |
| M04-FR-001 | M04-AC-001 | Feature đo được có unit/provenance; timing thiếu thì null |
| M04-FR-002 | M04-AC-002 | Không imputation hoặc claim unsupported |

## Quyết định còn mở

- Bộ feature W2 tối thiểu nào được nhóm và giảng viên đồng ý?
- Cách chọn duration: full audio hay voiced duration cho speaking rate?
- Policy khi ASR UNRELIABLE: giữ feature với flag hay null toàn bộ?

**CODEX CHECK RESULT:** DRAFT — đã đối chiếu FR/AC và ranh giới M04; chưa có verdict Phase 01, hợp đồng liên module và dữ liệu W2 cần review. **User verdict Phase 03:** PENDING.
