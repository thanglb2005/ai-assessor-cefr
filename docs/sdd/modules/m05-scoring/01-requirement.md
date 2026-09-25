# M05 — Scoring & Band Mapping

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M05 / module |
| SCOPE ROOT | `docs/sdd/modules/m05-scoring/` |
| OWNER | Sang (đề xuất W2–W3) |
| LIFECYCLE | proposed |
| PHASE 01 | DRAFT — chờ người dùng duyệt |
| RESEARCH MODE | Đề xuất `RUN`; người dùng quyết định trong Phase 01 |
| TARGET | W2–W3 |
| RELATED SCOPES | M04 FeatureSet, rubric/construct được xác nhận |
| SOURCE BASIS | [Tài liệu nguồn do nhóm tạo](../../../sources/README.md), [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx); SDD hiện hành quyết định phạm vi, contract và approval của module |
| CODE TARGET | `src/aicefr/scoring/` — đề xuất, chưa tạo |

## Requirement (Yêu cầu)

**Mục tiêu:** Tạo ước lượng điểm/band từ baseline được kiểm định, có version; từ chối khi thiếu bằng chứng hoặc model/rubric hợp lệ.

**Trong phạm vi:** Baseline có model/config version; score/band mapping được mô tả; cửa sổ cho bài dài nếu được chốt; OOD/low confidence/refusal.

**Ngoài phạm vi W2–W3:** Fine-tune foundation model; tuyên bố metric trên population chưa đo; score Interaction từ độc thoại.

| ID | Functional Requirement (Yêu cầu chức năng) |
| --- | --- |
| M05-FR-001 | Scorer chỉ phát điểm/band khi FeatureSet thỏa invariant; phải có model version và criterion coverage. |
| M05-FR-002 | OOD, thiếu feature hoặc near boundary theo ngưỡng được duyệt trả `REVIEW_REQUIRED`/null hoặc score tạm theo contract, không bịa kết luận. |

## Acceptance Criteria (Tiêu chí chấp nhận)

| ID | Bằng chứng phải kiểm tra |
| --- | --- |
| M05-AC-001 | Fixture thiếu evidence không nhận score; `Interaction` luôn `insufficient_evidence` trong task độc thoại. |
| M05-AC-002 | Nếu artifact/config hợp lệ, cùng input tạo một overall estimate tái lập cùng năm coverage; output không có score/band riêng từng tiêu chí. Nếu chưa đủ điều kiện thì `NOT_EVALUATED`. Metric chỉ ghi khi có manifest/split/evidence hợp lệ. |

## W2 scope note (Ranh giới tuần 2)

W2 xây contract, đường từ chối và provenance dựa trên [model và đường chấm overall do nhóm đã kiểm chứng](../../../sources/scoring-audit.md). `ridge_resp_v2` là ứng viên cho unit of inference một response; trước khi tích hợp cần kiểm hash, feature order, ASR/VAD, inference unit và quyền dữ liệu. Rubric Speaking/nhãn riêng cho năm tiêu chí hiện chưa có trong nguồn đã khảo sát; sản phẩm chỉ hiển thị overall score/band và coverage từng tiêu chí theo quyết định chủ dự án. Metric báo cáo phải gắn với dataset, protocol và revision hiện hành.

## Điều kiện chung và câu hỏi mở

- Unit test dùng fixture tạo bởi nhóm; smoke/integration chỉ dùng audio có quyền sử dụng. Fixture kiểm thử không là số liệu thực nghiệm; không log audio, transcript hoặc PII.
- ID, enum, schema/API xuyên module phải được cả owner liên quan review; mọi feature code chỉ bắt đầu sau khi Phase 01, 03, 04 và 05 của **module này** được người dùng duyệt theo thứ tự.
- Chủ dự án đã chọn 5 tiêu chí độc thoại làm bản nháp W2; rubric học thuật vẫn cần xác minh. Giữ field `Interaction=null` cùng lý do `insufficient_evidence` cho độc thoại. Dữ liệu/model và lịch 3 tuần xem [roadmap](../../../plan/three-week-roadmap.md).

