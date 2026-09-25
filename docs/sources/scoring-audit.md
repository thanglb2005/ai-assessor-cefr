# Kiểm tra bằng chứng chấm điểm của phiên bản trước

**Ngày đọc:** 25/09/2026. Đây là khảo sát read-only theo yêu cầu chủ dự án để thiết kế lại M05. Repo và kết quả trước đều là công việc của nhóm; nội dung dưới đây **không phải kết quả chạy/đánh giá của repo mới**.

| Hạng mục | Đã thấy trực tiếp | Kết luận cho M05 mới |
| --- | --- | --- |
| Ridge overall scorer | `scorer.py`, `tools/train_scorer.py`, `tests/test_scorer.py` và `ridge_resp_v2.json` trong repo trước. Model JSON SHA-256 `7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a`. | Ứng dụng cũ **đã có** đường dự đoán điểm/band tổng thể cho **một response**, OOD refusal và test. Có thể học lại contract/invariant, viết code mới; chưa chuyển model/artifact vào repo mới. |
| Training/provenance Ridge | Script dùng P3/P4 của Speak & Improve, `GroupKFold` theo speaker; artifact ghi `train_n=876`, `cv_pcc=0.6966`, `cv_rmse=0.5262`, `calibration_version=chua-hieu-chuan`. | Các số là **metadata lịch sử** trên corpus khác population mục tiêu; chưa tự chạy lại vì workspace dữ liệu huấn luyện không nằm trong repo mới. Không ghi là độ chính xác với sinh viên Việt Nam hoặc M05 mới. |
| Năm tiêu chí | `RidgeScorer.score()` xuất một `overall_0_6`/band và năm `CriterionCoverage` (mức tính được của feature), không xuất năm score độc lập. Decision log cũ `QD-04` cũng ghi corpus chỉ có nhãn tổng thể. | Báo cáo W2 không được gọi coverage/proxy là “điểm Range/Accuracy/Fluency/Coherence/Phonology”. Rubric chấm từng tiêu chí và dữ liệu nhãn tương ứng vẫn cần xác minh. |
| DeBERTa transcript model | [Báo cáo gốc của Thắng](prior-project-reports/deberta_cefr_finetune_thang.md) SHA-256 `27b17e3519f5a648d9acff354bf1887493904a00bdbdee6b80d255d5f94c0a46`; manifest và bốn weight `model.safetensors` đã xác nhận có tại kho riêng ngoài Git. Manifest SHA-256 `1179a6b641ef95566a2bf206ea135059a5ef4e962e4a27c6805d91d5c812407e`. | Report nêu **dev overall** PCC `0.8273`, RMSE `0.5118` trên bốn phần P1/P3/P4/P5; model **chưa tích hợp vào app cũ**, chưa đánh giá trên test độc lập/đối tượng Việt Nam. Đây là kết quả fine-tune lịch sử, không là metric của bản dựng mới. |
| Quyết định phạm vi | `QD-04` trong [decision log cũ](../../../aiassessor-cefr/docs/plan/QUYET_DINH.md) ghi chủ dự án chọn 5 tiêu chí và bỏ hẳn `Interaction`; báo cáo W1 mới cũng dùng 5 tiêu chí. | Bản nháp W2 theo 5 tiêu chí. Chủ dự án quyết định ngày 25/09/2026: output mới giữ field `Interaction=null` với reason `insufficient_evidence` để giải thích thiếu bằng chứng; đây là thay đổi so với QD-04 cũ. |

## Gaps trước khi dùng lại artifact cho bản dựng mới

1. Xác nhận quyền/truy cập corpus, đường dẫn dữ liệu và protocol tái chạy; hash model/manifest, feature order, ASR/VAD/config và `unit_of_inference` phải khớp pipeline mới.
2. Xác nhận rubric Speaking của giảng viên, tiêu chí nào có nhãn thật, band thresholds và calibration. Model hồi quy **điểm tổng thể của corpus** không tự là năm điểm tiêu chí CEFR.
3. Nếu chủ dự án muốn dùng Ridge artifact đã huấn luyện: ghi rõ đây là model do nhóm tạo ở phiên bản trước, xin duyệt việc đưa artifact vào bản dựng mới, kiểm tra license/dữ liệu và chạy test integration mới. Code inference vẫn viết mới.
4. Nếu muốn dùng DeBERTa: cần tích hợp mới, kiểm resources/weight license, test inference và đánh giá thích hợp; không thể lấy bảng dev làm bằng chứng app đang chấm qua DeBERTa.

**Kết luận kiểm tra:** phần chấm **overall thử nghiệm** ở phiên bản trước là có thật; phần “đã chấm hoàn thiện năm tiêu chí CEFR cho population mục tiêu” chưa được chứng minh bởi artifact đã xem. M05 W2 cần kiểm chứng/thiết kế lại, không khởi đầu từ giả định “chưa có model” và cũng không tự đánh dấu model mới đã đạt.
