# M04 — Features

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M04 / module |
| SCOPE ROOT | `docs/sdd/modules/m04-features/` |
| OWNER | Sang (đề xuất W2–W3) |
| LIFECYCLE | proposed |
| PHASE 01 | DRAFT v0.2 — owner review 26/09/2026, chờ người dùng duyệt |
| RESEARCH MODE | Đề xuất `SKIP`; người dùng quyết định trong Phase 01 |
| TARGET | W2 |
| RELATED SCOPES | M02 QC và **DecodedAudio cho VAD**; M03 transcript/timestamp; **M05 — `feature_order` của model scoring quyết định bộ đặc trưng** (xem M04-FR-003) |
| SOURCE BASIS | [Tài liệu nguồn do nhóm tạo](../../../sources/README.md), [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx), [kiểm tra scorer/model](../../../sources/scoring-audit.md); SDD hiện hành quyết định phạm vi, contract và approval của module |
| CODE TARGET | `src/aicefr/features/` — đề xuất, chưa tạo |

## Requirement (Yêu cầu)

**Mục tiêu:** Tính các đặc trưng bài nói có định nghĩa, version và lý do khi thiếu dữ liệu, đủ để model scoring của M05 sử dụng.

**Trong phạm vi:** FeatureSet có tên/giá trị/đơn vị/nguồn; fluency/lexical/timing trong phạm vi dữ liệu hỗ trợ; bước VAD (voice activity detection) để tính đặc trưng thời gian nói/ngừng; coverage từng criterion.

**Ngoài phạm vi W2–W3:** Tự chấm CEFR; gán đặc trưng không đo được từ transcript kém tin cậy.

| ID | Functional Requirement (Yêu cầu chức năng) |
| --- | --- |
| M04-FR-001 | Mỗi feature có `feature_version`, input provenance và `missing_reason` khi không tính được. |
| M04-FR-002 | Dữ liệu thiếu hoặc ASR bất định không được âm thầm thay bằng 0 hay trung bình. |
| M04-FR-003 | FeatureSet chứa đúng tập tên đặc trưng theo `feature_order` của model scoring mà M05 dùng. Với `ridge_resp_v2` là 18 đặc trưng. Tên và thứ tự đọc từ artifact, không chép tay thành danh sách thứ hai trong code. |
| M04-FR-004 | M04 sở hữu bước VAD để tính các đặc trưng `vad_*`; FeatureSet ghi `vad_name`/version và giá trị này phải khớp `trained_with.vad_name` của model scoring. |

## Acceptance Criteria (Tiêu chí chấp nhận)

| ID | Bằng chứng phải kiểm tra |
| --- | --- |
| M04-AC-001 | Fixture có transcript/timestamp cho feature tất định; thiếu timestamps trả null + reason cho feature cần timing. |
| M04-AC-002 | FeatureSet không chứa PII và chỉ số unsupported không bị báo là đã đo. |
| M04-AC-003 | Với fixture hợp lệ, FeatureSet có đủ 18 tên theo đúng `feature_order` của `ridge_resp_v2`. Đặc trưng không tính được vẫn có mặt với value null + `missing_reason`, không bị bỏ tên. |
| M04-AC-004 | `vad_name` ghi trong FeatureSet khớp `trained_with.vad_name`; test với VAD khác cho ra reason lệch phiên bản. |

## Quyết định của owner trong review Phase 01 (26/09/2026)

| ID | Quyết định | Căn cứ |
| --- | --- | --- |
| M04-D-001 | Bộ đặc trưng W2 là **18 đặc trưng** theo `feature_order` của `ridge_resp_v2`, thay cho bản nháp 3 đặc trưng. | Bản nháp đề xuất speech duration, word count và speaking rate. Ridge v2 đòi đủ 18 đặc trưng; thiếu một thì model không chấm được bài nào và M05 luôn trả `NOT_EVALUATED`. Danh sách đo từ artifact ngày 26/09/2026: `n_words`, `words_per_sec`, `total_dur`, `mean_word_len`, `ttr`, `log_uniq`, `asr_conf_mean`, `asr_conf_geo`, `vad_silence_ratio`, `vad_mean_pause`, `vad_pause_per_min`, `vad_long_pause_ratio`, `vad_pause_sd`, `vad_mean_seg_len`, `vad_n_seg_per_min`, `vad_articulation_rate`, `vad_onset_delay`, `vad_speech_sec`. |
| M04-D-002 | **VAD thuộc M04**, dùng Silero (`trained_with.vad_name = "silero"`). | 10/18 đặc trưng là `vad_*`, nhưng bản nháp không giao VAD cho module nào. Đặt tại M04 giữ toàn bộ chuỗi đặc trưng trong một owner. Môi trường của hồ sơ kỹ thuật nội bộ dùng gói `silero-vad` 6.2.1, trọng số đi kèm gói nên không tải qua mạng lúc chạy; license cần ghi trong Specification. |
| M04-D-003 | Giữ đề xuất Research `SKIP`. | Bộ đặc trưng và VAD đã được xác định bởi artifact M05; câu hỏi còn lại là công thức và cách xử lý thiếu dữ liệu, thuộc Specification. |

## W2 scope note (Ranh giới tuần 2)

W2 tính đủ 18 đặc trưng mà model scoring đòi; mỗi giá trị mang nguồn và đơn vị, đặc trưng không tính được mang null + reason. Không suy Phonology hoặc Accuracy chỉ từ một proxy kỹ thuật: 18 đặc trưng là đầu vào của một model ước lượng overall, không phải điểm từng tiêu chí.

## Điều kiện chung và câu hỏi mở

- Unit test dùng fixture tạo bởi nhóm; smoke/integration chỉ dùng audio có quyền sử dụng. Fixture kiểm thử không là số liệu thực nghiệm; không log audio, transcript hoặc PII.
- ID, enum, schema/API xuyên module phải được cả owner liên quan review; mọi feature code chỉ bắt đầu sau khi Phase 01, 03, 04 và 05 của **module này** được người dùng duyệt theo thứ tự.
- Chủ dự án đã chọn 5 tiêu chí độc thoại làm bản nháp W2; rubric học thuật vẫn cần xác minh. Giữ field `Interaction=null` cùng lý do `insufficient_evidence` cho độc thoại. Dữ liệu/model và lịch 3 tuần xem [roadmap](../../../plan/three-week-roadmap.md).
- **Tác động liên module — cần Thắng review:** M04-D-002 làm M04 trở thành consumer thứ hai của `DecodedAudio` từ M02 (sau M03), vì VAD chạy trên waveform. Không thêm hay đổi field của M02, chỉ thêm consumer.
- **Artifact phía sau đã stale:** [03-specification.md](03-specification.md) còn ghi "W2 candidate features" gồm 3 đặc trưng; Test Plan và Tasks theo sau. Sửa ở Phase 03 sau khi Requirement v0.2 được duyệt.

## Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
| --- | --- | --- |
| v0.1 | 25/09/2026 | Bản nháp đầu |
| v0.2 | 26/09/2026 | Owner review: thêm M04-FR-003/004, M04-AC-003/004; quyết định M04-D-001 (18 đặc trưng), M04-D-002 (VAD thuộc M04), M04-D-003 |
