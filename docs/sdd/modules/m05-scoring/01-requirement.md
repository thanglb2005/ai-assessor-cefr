# M05 — Scoring & Band Mapping

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M05 / module |
| SCOPE ROOT | `docs/sdd/modules/m05-scoring/` |
| OWNER | Sang (đề xuất W2–W3) |
| LIFECYCLE | proposed |
| PHASE 01 | **APPROVED** v0.2 — người dùng (Sang) duyệt ngày 26/09/2026 |
| RESEARCH MODE | **`RUN`** — theo đề xuất trong v0.2; người dùng duyệt Phase 01 không đổi đề xuất |
| TARGET | W2–W3 |
| RELATED SCOPES | M04 FeatureSet (`feature_order`, `vad_name`); M03 transcript (`asr_model`); rubric/construct được xác nhận |
| SOURCE BASIS | [Tài liệu nguồn do nhóm tạo](../../../sources/README.md), [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx), [kiểm tra scorer/model](../../../sources/scoring-audit.md); SDD hiện hành quyết định phạm vi, contract và approval của module |
| CODE TARGET | `src/aicefr/scoring/` — đề xuất, chưa tạo |

## Requirement (Yêu cầu)

**Mục tiêu:** Tạo ước lượng điểm/band từ baseline được kiểm định, có version; từ chối khi thiếu bằng chứng hoặc model/rubric hợp lệ.

**Trong phạm vi:** Baseline có model/config version; score/band mapping được mô tả; cửa sổ cho bài dài nếu được chốt; OOD/low confidence/refusal; kiểm provenance đầu vào khớp artifact.

**Ngoài phạm vi W2–W3:** Fine-tune foundation model; tuyên bố metric trên population chưa đo; score Interaction từ độc thoại.

| ID | Functional Requirement (Yêu cầu chức năng) |
| --- | --- |
| M05-FR-001 | Scorer chỉ phát điểm/band khi FeatureSet thỏa invariant; phải có model version và criterion coverage. |
| M05-FR-002 | OOD, thiếu feature hoặc near boundary theo ngưỡng được duyệt trả `REVIEW_REQUIRED`/null hoặc score tạm theo contract, không bịa kết luận. |
| M05-FR-003 | Trước khi phát band, kiểm provenance đầu vào khớp `trained_with` của artifact (`asr_model`, `vad_name`) và `feature_order`. Lệch bất kỳ mục nào thì không phát band tự động; trả `NOT_EVALUATED` hoặc `REVIEW_REQUIRED` kèm reason. |

## Acceptance Criteria (Tiêu chí chấp nhận)

| ID | Bằng chứng phải kiểm tra |
| --- | --- |
| M05-AC-001 | Fixture thiếu evidence không nhận score; `Interaction` luôn `insufficient_evidence` trong task độc thoại. |
| M05-AC-002 | Nếu artifact/config hợp lệ, cùng input tạo một overall estimate tái lập cùng năm coverage; output không có score/band riêng từng tiêu chí. Nếu chưa đủ điều kiện thì `NOT_EVALUATED`. Metric chỉ ghi khi có manifest/split/evidence hợp lệ. |
| M05-AC-003 | Ba test lệch riêng biệt — `asr_model`, `vad_name`, `feature_order` — đều không cho band tự động và mang reason tương ứng. |

## Kết quả kiểm tra của owner trong review Phase 01 (26/09/2026)

| ID | Phát hiện | Căn cứ đo được | Xử lý |
| --- | --- | --- | --- |
| M05-R-001 | **Artifact Ridge khớp hash.** `ridge_resp_v1.json`, `ridge_resp_v2.json`, `ridge_v3.json` trong hồ sơ kỹ thuật nội bộ trên máy Sang khớp đúng SHA-256 ghi trong [scoring-audit](../../../sources/scoring-audit.md). | `ridge_resp_v2.json` = `7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a`, đo bằng `shasum -a 256` ngày 26/09/2026. | Điều kiện "kiểm hash" của W2 scope note có thể đạt với artifact này. |
| M05-R-002 | **Đầu vào của Ridge v2 ràng buộc M03 và M04.** Artifact ghi `trained_with.asr_model = "whisper-small"`, `trained_with.vad_name = "silero"` và `feature_order` 18 phần tử. | Đọc trực tiếp từ `ridge_resp_v2.json`. | Đã đưa vào M03-D-001, M04-D-001, M04-D-002 và M05-FR-003. |
| M05-R-003 | **Output năm dòng coverage đã có tiền lệ.** Bản mới nhất của hồ sơ kỹ thuật nội bộ đã thay `CriterionScore` (lặp overall vào năm dòng) bằng lớp chỉ mang `coverage`, trùng quyết định ngày 25/09/2026. | [scoring-audit](../../../sources/scoring-audit.md) mô tả bản chụp trước thay đổi này; `contracts.py` hiện có SHA-256 khác giá trị đã ghi vì tệp đã thay đổi. | Tham chiếu shape này khi soạn Specification. |

## Quyết định còn mở

| ID | Vấn đề | Số liệu | Nơi quyết định |
| --- | --- | --- | --- |
| M05-O-001 | Ngưỡng near-boundary của Ridge v2 quá rộng. | `band_thresholds` A2/B1 = 2,75, B1/B2 = 3,75; `boundary_margin` = 0,5 → vùng review là [2,25 ; 3,25] ∪ [3,25 ; 4,25] = [2,25 ; 4,25], bao trọn bậc B1 [2,75 ; 3,75]. Mọi bài được ước lượng B1 đều bị chuyển review. | Research (`RUN`) → Specification. Không dùng ngưỡng này làm mặc định trước khi quyết định. |

## W2 scope note (Ranh giới tuần 2)

W2 xây contract, đường từ chối và provenance dựa trên [model và đường chấm overall do nhóm đã kiểm chứng](../../../sources/scoring-audit.md). `ridge_resp_v2` là ứng viên cho unit of inference một response; trước khi tích hợp cần kiểm hash (đã đạt theo M05-R-001), feature order, ASR/VAD, inference unit và quyền dữ liệu. Rubric Speaking/nhãn riêng cho năm tiêu chí hiện chưa có trong nguồn đã khảo sát; sản phẩm chỉ hiển thị overall score/band và coverage từng tiêu chí theo quyết định chủ dự án. Metric báo cáo phải gắn với dataset, protocol và revision hiện hành.

## Điều kiện chung và câu hỏi mở

- Unit test dùng fixture tạo bởi nhóm; smoke/integration chỉ dùng audio có quyền sử dụng. Fixture kiểm thử không là số liệu thực nghiệm; không log audio, transcript hoặc PII.
- ID, enum, schema/API xuyên module phải được cả owner liên quan review; mọi feature code chỉ bắt đầu sau khi Phase 01, 03, 04 và 05 của **module này** được người dùng duyệt theo thứ tự.
- Chủ dự án đã chọn 5 tiêu chí độc thoại làm bản nháp W2; rubric học thuật vẫn cần xác minh. Giữ field `Interaction=null` cùng lý do `insufficient_evidence` cho độc thoại. Dữ liệu/model và lịch 3 tuần xem [roadmap](../../../plan/three-week-roadmap.md).
- **Ghi chú gửi owner `docs/sources/` (không sửa trong M05):** [scoring-audit](../../../sources/scoring-audit.md) ghi SHA-256 của `scorer.py` là chuỗi 49 ký tự, không phải SHA-256 hợp lệ (64 ký tự); `pipeline.py` và `contracts.py` đã thay đổi so với giá trị đã ghi. Đề nghị cập nhật khi tài liệu nguồn được rà lại.

## Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
| --- | --- | --- |
| v0.1 | 25/09/2026 | Bản nháp đầu |
| v0.2 | 26/09/2026 | **APPROVED** Phase 01 ngày 26/09/2026. Owner review: thêm M05-FR-003, M05-AC-003; kết quả kiểm tra M05-R-001..003; quyết định còn mở M05-O-001 |
