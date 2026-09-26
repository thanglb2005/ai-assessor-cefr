# M04 — 03 Specification (Đặc tả)

> **v0.2 · 26/09/2026 · chờ Phase 03 verdict.** Dựa trên [Requirement v0.2 APPROVED](01-requirement.md). `RESEARCH MODE: SKIP` (M04-D-003) — không có `02-research.md`; nguồn công thức ghi trực tiếp ở bảng Reference bên dưới. Chưa cấp quyền phát prompt triển khai.

**Owner:** Sang. **Mục tiêu W2:** FeatureSet đủ 18 đặc trưng theo `feature_order` của `ridge_resp_v2`, gồm 10 đặc trưng `vad_*` do M04 tự chạy Silero VAD; mỗi giá trị có đơn vị, nguồn và `missing_reason` khi không tính được.

## Reference (thay cho Research đã SKIP)

| REF-ID | Nguồn trong hồ sơ kỹ thuật nội bộ | Giá trị | Quyết định |
| --- | --- | --- | --- |
| M04-REF-01 | `features/extract.py` (`FEATURE_VERSION="v3"`) | Công thức 18 đặc trưng trùng `feature_version="v3"` của Ridge v2 | **ADOPT** công thức; code dự án viết mới theo Spec |
| M04-REF-02 | `asr/vad.py` `SileroVad` | `threshold=0.5`, `min_silence_duration_ms=150` = `trained_with` | **ADOPT** |
| M04-REF-03 | `asr/vad.py` `default_vad()` | Âm thầm rơi về `EnergyVad` khi Silero lỗi | **REJECT** — vi phạm M04-FR-004 |
| M04-REF-04 | `extract.py` `vad_features` khi không có segment | Trả `0.0` cho cả 10 đặc trưng | **REJECT** — vi phạm M04-FR-002; dùng `null` |
| M04-REF-05 | `extract.py` `filler_ratio` | Extractor sinh 19 đặc trưng; Ridge v2 bỏ `filler_ratio` (hằng 0 khi huấn luyện) | **REJECT** khỏi FeatureSet (M04-FR-003) |

## Boundary và hợp đồng

| Artifact | Trường / invariant | Owner → consumer |
| --- | --- | --- |
| FeatureInput | `Transcript` (status, words, `asr_model`, reasons) từ M03; `DecodedAudio` (16 kHz mono, xem M03-O-002) và `duration_s` từ M02; `feature_order`, `feature_version`, `trained_with.vad_name` đọc từ artifact M05 | M02/M03/M05 → M04 |
| FeatureValue | `name`; `value: float \| null`; `unit`; `missing_reason: ReasonCode \| null` | M04 → M05/M06 |
| FeatureSet | `response_id`; `values` theo **đúng thứ tự `feature_order`**; `feature_version`; `vad_name`, `vad_version`, `vad_threshold`, `vad_min_silence_ms`; `asr_model` (chép từ Transcript); `transcript_ref`, `audio_sha256`; `reasons` | M04 → M05 |
| VadSegments | `list[(start_s, end_s)]`, nội bộ M04; M06 được đọc nếu cần evidence ngừng | M04 → M06 |

## Chuẩn hóa token

`tok = text.strip().strip('.,?!;:"').lower()`; bỏ token rỗng sau chuẩn hóa. `n` = số token còn lại, `uniq` = số token khác nhau. Filler (`um`, `uh`, …) **được đếm** như token thường — giống feature v3.

## Catalogue 18 đặc trưng (thứ tự = `feature_order`)

`D` = `duration_s` (độ dài toàn bài từ M02). `S` = tổng độ dài segment VAD. `P` = danh sách ngừng: khoảng giữa hai segment liên tiếp, cộng khoảng đuôi `D − end(segment cuối)`, chỉ giữ khoảng `> 0,30 s`.

| # | Tên | Công thức | Đơn vị | Khoảng huấn luyện | Nguồn |
| --- | --- | --- | --- | --- | --- |
| 1 | `n_words` | `n` | từ | 35,5 – 151 | transcript |
| 2 | `words_per_sec` | `n / D` | từ/s | 0,80 – 2,66 | transcript + M02 |
| 3 | `total_dur` | `D` | s | 26,66 – 60,74 | M02 |
| 4 | `mean_word_len` | tổng số ký tự token / `n` | ký tự | 3,70 – 5,12 | transcript |
| 5 | `ttr` | `uniq / n` | tỷ lệ | 0,45 – 0,83 | transcript |
| 6 | `log_uniq` | `ln(uniq + 1)` | — | 3,33 – 4,46 | transcript |
| 7 | `asr_conf_mean` | trung bình `prob` của các word có `prob ≠ null` | [0,1] | 0,69 – 0,95 | transcript |
| 8 | `asr_conf_geo` | `exp(mean(ln(max(prob, 1e-4))))` trên cùng tập | [0,1] | 0,59 – 0,94 | transcript |
| 9 | `vad_silence_ratio` | `1 − S / D` | tỷ lệ | 0,04 – 0,54 | VAD |
| 10 | `vad_mean_pause` | `mean(P)`; `0` nếu `P` rỗng | s | 0,33 – 1,85 | VAD |
| 11 | `vad_pause_per_min` | `len(P) / (D / 60)` | lần/phút | 1,0 – 25,1 | VAD |
| 12 | `vad_long_pause_ratio` | tỷ lệ phần tử `P` `> 1,00 s`; `0` nếu `P` rỗng | tỷ lệ | 0 – 0,60 | VAD |
| 13 | `vad_pause_sd` | độ lệch chuẩn tổng thể của `P` nếu `len(P) > 1`, ngược lại `0` | s | 0 – 2,22 | VAD |
| 14 | `vad_mean_seg_len` | trung bình độ dài segment | s | 1,12 – 19,18 | VAD |
| 15 | `vad_n_seg_per_min` | số segment / `(D / 60)` | lần/phút | 3,0 – 33,8 | VAD |
| 16 | `vad_articulation_rate` | `n / S` | từ/s nói | 1,20 – 3,15 | VAD + transcript |
| 17 | `vad_onset_delay` | `start` của segment đầu | s | 0,30 – 5,53 | VAD |
| 18 | `vad_speech_sec` | `S` | s | 18,55 – 57,30 | VAD |

Khoảng huấn luyện (`feature_lo`/`feature_hi` của Ridge v2) chỉ để tham khảo khi viết fixture; kiểm OOD thuộc M05. `P` rỗng cho `0` ở #10, #12, #13 là **giá trị đo thật** (không có lần ngừng nào), không phải imputation — khác trường hợp không có segment (bảng dưới).

## VAD (M04-FR-004)

- Silero từ gói `silero-vad` 6.2.1 (license MIT, trọng số đi kèm gói, không tải mạng lúc chạy). Tham số cố định: `threshold=0.5`, `min_silence_duration_ms=150`, `sampling_rate=16000`, trả giây.
- Tham số VAD đọc so với `trained_with` (`vad_name`, `vad_threshold`, `vad_min_silence_ms`); lệch bất kỳ mục nào → `VAD_VERSION_MISMATCH` trên FeatureSet.
- Silero không nạp được → **không** rơi về VAD khác; 10 đặc trưng `vad_*` và #16 = `null` + `FEATURE_NOT_COMPUTABLE`.

## Dữ liệu thiếu (M04-FR-002)

| Điều kiện | Đặc trưng bị `null` | `missing_reason` |
| --- | --- | --- |
| Transcript `status ≠ OK` (M03-FR-002) | #1, 2, 4–8, 16 | `FEATURE_NOT_COMPUTABLE` |
| `n < 10` | #4, 5, 6 | `TOO_FEW_WORDS` |
| Không word nào có `prob` | #7, 8 | `FEATURE_NOT_COMPUTABLE` |
| VAD không ra segment nào, hoặc Silero lỗi | #9–18 | `FEATURE_NOT_COMPUTABLE` |
| `D ≤ 0` | toàn bộ 18 | `FEATURE_NOT_COMPUTABLE` |
| Kết quả là NaN/±∞ | đặc trưng đó | `FEATURE_NOT_COMPUTABLE` |

Mọi đặc trưng `null` vẫn có mặt trong `values` với tên đúng vị trí (M04-AC-003). Không bao giờ thay bằng 0 hay trung bình.

## Kiểm nhất quán

- Tên và thứ tự đọc từ `feature_order` của artifact M05 lúc chạy (M04-FR-003); tên không có công thức trong catalogue → dừng với lỗi cấu hình, không bỏ qua.
- `feature_version` của M04 (`v3`) phải bằng `feature_version` của artifact; lệch → reason `FEATURE_VERSION_MISMATCH` (**mã mới**, đề nghị Thắng thêm vào contract chung).
- Giá trị lưu float64, **không làm tròn** trong FeatureSet; làm tròn chỉ ở tầng hiển thị M06.

## Bảo mật, riêng tư, accessibility

- FeatureSet chỉ chứa số đo và ref; không chứa token, `text` hay audio.
- Log chỉ ghi `response_id`, tên đặc trưng bị null và reason.
- Accessibility: N/A — M04 không có giao diện.

## Trace Requirement → AC

| Requirement | AC | Quan sát |
| --- | --- | --- |
| M04-FR-001 | M04-AC-001 | Mỗi FeatureValue có unit; thiếu → null + reason |
| M04-FR-002 | M04-AC-001, M04-AC-002 | Bảng dữ liệu thiếu; không 0/mean; REF-04 bị loại |
| M04-FR-003 | M04-AC-003 | 18 tên đúng thứ tự `feature_order`; không có `filler_ratio` |
| M04-FR-004 | M04-AC-004 | `vad_name="silero"` + tham số khớp; VAD khác → `VAD_VERSION_MISMATCH` |

## Giả định, phụ thuộc, câu hỏi mở

| Loại | Nội dung |
| --- | --- |
| Phụ thuộc | DecodedAudio 16 kHz mono từ M02 (chung với **M03-O-002**; Thắng review consumer thứ hai) |
| Phụ thuộc | Reason code mới `FEATURE_VERSION_MISMATCH`; các mã còn lại đã có trong hồ sơ tham chiếu |
| Rủi ro → Test Plan | Engine local có thể chép filler mà CTM huấn luyện không có → `n_words`/`ttr` lệch nhẹ (M03 Research I-02) |
| OPEN riêng M04 | Không có |

**CODEX CHECK RESULT:** FR/AC trace đủ; công thức, đơn vị, missing policy cho cả 18 đặc trưng; security/privacy có, accessibility N/A có lý do. Không có OPEN riêng; phụ thuộc M03-O-002. **User verdict Phase 03:** PENDING.

## Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
| --- | --- | --- |
| v0.1 | 25/09/2026 | Bản nháp đầu (3 đặc trưng) |
| v0.2 | 26/09/2026 | Theo Requirement v0.2: catalogue 18 đặc trưng, VAD Silero, bảng dữ liệu thiếu, loại fallback EnergyVad và giá trị 0 giả |
