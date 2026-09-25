# M05 — 03 Specification (Đặc tả)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M05 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

**Owner đề xuất:** Sang. **Cơ sở:** [Nguồn đề tài do nhóm tạo](../../../sources/README.md) và [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx). **Mục tiêu W2:** Định nghĩa scorer có provenance và đường từ chối an toàn; tái kiểm model Ridge do nhóm từng huấn luyện như một ứng viên, chỉ phát band overall ước lượng khi artifact/pipeline/input đủ điều kiện.

## Boundary và hợp đồng đầu vào/đầu ra

| Artifact/boundary | Trường hoặc invariant bắt buộc | Owner/consumer |
| --- | --- | --- |
| ScoreInput | FeatureSet hợp lệ, task/rubric version, model config và evidence coverage; không nhận null như số 0 | M04/M08 → M05 |
| CriterionProfile | năm tiêu chí W1 với coverage/evidence; `score=null` cho từng tiêu chí nếu chưa có nhãn/model riêng đã kiểm định | M05 → M06/M07 |
| InteractionResult | `level=null`, `score_status=insufficient_evidence` cho monologue | M05 → M06 |
| OverallEstimate/ScoreProvenance | nullable overall score/band, model ID/hash, unit `one_response`, feature/ASR/VAD/band-map/calibration/rubric version hoặc reason | M05 → report/evidence |

## Hành vi có thể kiểm tra

- Chỉ dùng 5 tiêu chí của W1 làm **phạm vi nháp**; giữ `Interaction=null` với reason `insufficient_evidence`; overall chỉ từ model đã tái kiểm, không từ một proxy đơn lẻ.
- Model Ridge lịch sử có overall score theo response và năm criterion coverage, chưa phải năm điểm độc lập. Chỉ tái dùng artifact sau khi chủ dự án duyệt và kiểm feature order, ASR/VAD, task/unit, license, hash; nếu thiếu, trả `NOT_EVALUATED` và không tạo band.
- Nếu baseline Ridge được duyệt, overall estimate phải tất định với cùng input/config, thể hiện estimated/provisional, model version và giới hạn corpus. Không gán score từng criterion từ overall hoặc tỷ lệ feature đo được.
- Near-boundary/OOD/low confidence chỉ kích hoạt `REVIEW_REQUIRED` theo ngưỡng có version; không gán xác suất hoặc confidence nếu chưa hiệu chỉnh.

## Lỗi, thiếu dữ liệu và phục hồi

- Model file thiếu/hash sai hoặc parser lỗi: fail closed, không fallback sang band mặc định.
- FeatureSet thiếu/stale/NaN hoặc criterion coverage không đủ: null + reason.
- Model/rubric không phù hợp task/unit/feature pipeline: `NOT_EVALUATED`; metric dev lịch sử chỉ ghi ở tài liệu nguồn, không hiện như kết quả bản dựng mới.

## Quyền, riêng tư và giao diện

- Không nhận model artifact không rõ nguồn hoặc pickle không tin cậy; format và hash cần chốt.
- Không xuất lời khẳng định “chứng chỉ CEFR”/đậu rớt; mọi điểm là ước lượng thử nghiệm nếu chưa validation.
- Log chỉ provenance/status/reason, không log transcript hay đặc điểm nhận dạng.

## Trace Requirement → AC

| Requirement | Acceptance Criteria | Cách quan sát |
| --- | --- | --- |
| M05-FR-001 | M05-AC-001, M05-AC-002 | Model/input hợp lệ mới có estimate; provenance đủ |
| M05-FR-002 | M05-AC-001 | Thiếu/OOD/near boundary dẫn tới reason/review, Interaction null |

## Quyết định còn mở

- Rubric Speaking do giảng viên bộ môn thiết lập/duyệt đã có bản nào cho 5 tiêu chí chưa? Corpus Ridge lịch sử chỉ có overall label, không có năm nhãn criterion.
- Cho phép đánh giá lại artifact Ridge/DeBERTa lịch sử trên pipeline mới, và dữ liệu/weight đang ở đâu để tái lập?
- Nếu artifact chưa qua kiểm tương thích, W2 chấp nhận report `NOT_EVALUATED` thay band hay điều chỉnh thời hạn?
- Phương pháp band mapping/calibration và ngưỡng review nào được phê duyệt?

**CODEX CHECK RESULT:** DRAFT — đã đối chiếu FR/AC và ranh giới M05; chưa có verdict Phase 01, hợp đồng liên module và dữ liệu W2 cần review. **User verdict Phase 03:** PENDING.
