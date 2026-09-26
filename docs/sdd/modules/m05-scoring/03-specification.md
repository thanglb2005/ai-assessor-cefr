# M05 — 03 Specification (Đặc tả)

> **v0.2 · 26/09/2026 · APPROVED Phase 03 ngày 26/09/2026.** Dựa trên [Requirement v0.2 APPROVED](01-requirement.md) và [Research v0.2](02-research.md). Chưa cấp quyền phát prompt triển khai.

**Owner:** Sang. **Mục tiêu W2:** Ước lượng **một** overall score/band từ `ridge_resp_v2` khi đầu vào đủ điều kiện; năm tiêu chí chỉ mang coverage; mọi trường hợp còn lại từ chối có lý do.

## Boundary và hợp đồng

| Artifact | Trường / invariant | Owner → consumer |
| --- | --- | --- |
| ModelConfig | `model_name="ridge_resp_v2"`; `model_sha256` ghim = `7cdeb2a0…b521a` (M05-R-001); `boundary_margin = 0.5` — đọc từ artifact (M05-O-001) | cấu hình dự án → M05 |
| ScoreInput | `FeatureSet` từ M04 (18 giá trị theo `feature_order`, `feature_version`, `vad_*`, `asr_model`, reasons); `Transcript.status`, `reasons` từ M03 | M03/M04 → M05 |
| Assessment | `status` (dưới); `overall_score: float \| null` ∈ [1,0 ; 6,0]; `overall_band: A2 \| B1 \| B2 \| null`; `criteria: list[CriterionCoverage]` (5 dòng); `interaction`; `reasons`; provenance | M05 → M06/M07 |
| CriterionCoverage | `criterion ∈ {range, accuracy, fluency, coherence, phonology}`; `coverage ∈ [0,1] \| null`; `features: list[str]`; `reasons` — **không có score/band** | M05 → M06 |
| Interaction | `level=null`, `score_status="insufficient_evidence"` — luôn luôn cho bài độc thoại | M05 → M06 |
| Provenance | `model_version`, `model_sha256`, `feature_version`, `band_map_version`, `calibration_version`, `trained_with`, `unit_of_inference`, `scored_at` — tất cả đọc từ artifact trừ `scored_at` | M05 → M06/M08 |

### AssessmentStatus

| Status | Khi nào | `overall_*` |
| --- | --- | --- |
| `ESTIMATED` | Mọi kiểm tra đạt, không near-boundary | có score + band |
| `REVIEW_REQUIRED` | Có score nhưng near-boundary (`SCORE_NEAR_BOUNDARY`) | có score + band, chờ giảng viên |
| `NOT_EVALUATED` | Artifact không hợp lệ, provenance lệch, thiếu đặc trưng, OOD, hoặc transcript không `OK` | `null` |

Mọi status đều là ước lượng thử nghiệm; `teacher_verified=false` cho đến khi M07 xác nhận.

## Thứ tự kiểm (fail-closed, dừng ở bước đầu tiên thất bại)

| Bước | Kiểm | Thất bại → reason |
| --- | --- | --- |
| 1 | Nạp JSON (không pickle); SHA-256 = `model_sha256` ghim | `MODEL_ARTIFACT_INVALID` (**mã mới**) — file thiếu: `MODEL_VERSION_MISSING` |
| 2 | `unit_of_inference` chứa "một bài nói" (REF-05) | `MODEL_ARTIFACT_INVALID` |
| 3 | `Transcript.status == OK` | giữ reason của M03 |
| 4 | Provenance (M05-FR-003), so bằng `==`: `FeatureSet.asr_model == trained_with.asr_model`; `vad_name`, `vad_threshold`, `vad_min_silence_ms` khớp `trained_with`; danh sách tên FeatureSet == `feature_order`; `feature_version` khớp | `ASR_VERSION_MISMATCH`, `VAD_VERSION_MISMATCH`, `FEATURE_VERSION_MISMATCH` (gộp mọi mục lệch) → `NOT_EVALUATED` (M05-O-003) |
| 5 | Không đặc trưng nào `null` | `FEATURE_NOT_COMPUTABLE` |
| 6 | OOD (REF-02) với `ood_tolerance` từ artifact | `OUT_OF_DISTRIBUTION` + chi tiết từng đặc trưng |
| 7 | Tính `z`, `raw`, clip [1,0 ; 6,0]; band theo `band_thresholds` | — |
| 8 | `|score − t| ≤ boundary_margin` với `t ∈ {2,75 ; 3,75}` | `SCORE_NEAR_BOUNDARY` → `REVIEW_REQUIRED` |

## Coverage năm tiêu chí (REF-06)

| Tiêu chí | Đặc trưng liên quan (chỉ những tên có trong `feature_order`) |
| --- | --- |
| range | `log_uniq`, `ttr`, `mean_word_len` |
| accuracy | `asr_conf_mean`, `asr_conf_geo` |
| fluency | `words_per_sec`, `vad_articulation_rate`, `vad_mean_pause`, `vad_pause_per_min`, `vad_long_pause_ratio` |
| coherence | `n_words`, `vad_mean_seg_len`, `total_dur` |
| phonology | `asr_conf_mean`, `vad_silence_ratio` |

`coverage = số đặc trưng liên quan khác null / số đặc trưng liên quan`, làm tròn 2 chữ số. `coverage < 1` → `FEATURE_NOT_COMPUTABLE` trên dòng đó. Status `NOT_EVALUATED` → `coverage=null` + reason của Assessment. Bảng gán lấy từ hồ sơ tham chiếu, đã bỏ `filler_ratio` (Research F-05); là **giải thích**, không phải thang đo đã được thẩm định học thuật.

## Tính tất định

Cùng FeatureSet + cùng artifact → cùng `status`, `overall_score`, `overall_band`, `criteria`, `reasons` (so sánh bỏ qua `scored_at`). Artifact nạp một lần khi khởi tạo; không đọc lại giữa chừng.

## Bảo mật, riêng tư, accessibility

- Chỉ nạp artifact JSON có hash ghim; không pickle, không tải model qua mạng.
- Không có câu chữ "chứng chỉ CEFR", đậu/rớt; M06 hiển thị "ước lượng thử nghiệm" cùng `calibration_version`.
- Log chỉ ghi `response_id`, status, reason, `model_version`; không log FeatureSet chi tiết kèm định danh người học.
- Accessibility: N/A — M05 không có giao diện (M06 chịu trách nhiệm hiển thị).

## Reason code dùng (đề nghị Thắng đưa vào contract chung)

Đã có trong hồ sơ tham chiếu: `FEATURE_NOT_COMPUTABLE`, `OUT_OF_DISTRIBUTION`, `SCORE_NEAR_BOUNDARY`, `MODEL_VERSION_MISSING`, `ASR_VERSION_MISMATCH`, `VAD_VERSION_MISMATCH`. **Mới:** `FEATURE_VERSION_MISMATCH` (chung với M04), `MODEL_ARTIFACT_INVALID`.

## Trace Requirement → AC

| Requirement | AC | Quan sát |
| --- | --- | --- |
| M05-FR-001 | M05-AC-001, M05-AC-002 | Bước 1–7; provenance đủ; 5 dòng coverage, không score riêng |
| M05-FR-002 | M05-AC-001 | Bước 5, 6, 8; `Interaction` luôn `insufficient_evidence` |
| M05-FR-003 | M05-AC-003 | Bước 4: ba fixture lệch riêng `asr_model`, `vad_name`, `feature_order` |

## Giả định, phụ thuộc, câu hỏi mở

| Loại | Nội dung |
| --- | --- |
| Phụ thuộc | M03 `asr_model` identifier chuẩn (M03 Spec); M04 FeatureSet 18 giá trị |
| Phụ thuộc | Hai reason code mới cần Thắng duyệt vào contract chung |
| Giả định | Artifact `ridge_resp_v2.json` đặt trong repo dự án hay kho model riêng — quyết ở Phase 05 (vị trí file), hash ghim không đổi |
| Quyết định | **M05-O-001** — giữ `boundary_margin = 0,5`; mọi bài ước lượng B1 sang giảng viên; M06 cần nói rõ điều này |
| Quyết định | **M05-O-002** — W2 không chia cửa sổ; bài vượt khoảng chấp nhận (≈ 77,8 s) → `OUT_OF_DISTRIBUTION` kèm chi tiết; M01/M02 hiển thị giới hạn (phối hợp Nguyên/Thắng) |
| Quyết định | **M05-O-003** — provenance lệch → `NOT_EVALUATED`, không có số |

**CODEX CHECK RESULT:** FR/AC trace đủ; success/invalid/boundary/failure có; security/privacy có, accessibility N/A có lý do. **User verdict Phase 03:** APPROVED 26/09/2026 (Sang), theo khuyến nghị cho cả ba quyết định.

## Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
| --- | --- | --- |
| v0.1 | 25/09/2026 | Bản nháp đầu |
| v0.2 | 26/09/2026 | **APPROVED** Phase 03. Theo Requirement v0.2: thứ tự kiểm fail-closed, AssessmentStatus, coverage bỏ `filler_ratio`, hash ghim; ba quyết định M05-O-001..003 |
