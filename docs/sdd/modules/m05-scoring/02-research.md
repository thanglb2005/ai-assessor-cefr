# M05 — 02 Research (khảo sát rubric và scorer)

> **DRAFT v0.1 · 25/09/2026.** Phase 01 còn PENDING; `RESEARCH MODE: RUN` mới là đề xuất. Không khóa rubric, band mapping hoặc model từ nội dung file này.

## Câu hỏi nghiên cứu W2

1. Rubric Speaking của giảng viên có bản đã duyệt cho 5 tiêu chí độc thoại chưa? Đơn vị đánh giá là một response hay hồ sơ nhiều bài?
2. Dữ liệu nhãn, model Ridge/DeBERTa đã tạo ở phiên bản trước có thể tái kiểm/tích hợp hợp lệ vào bản dựng mới đến mức nào?
3. Nếu chưa đủ, report W2 nên hiển thị `NOT_EVALUATED` đến mức nào để vẫn có giá trị chẩn đoán mà không bịa CEFR band?

## Nguồn đã xem

| Nguồn | Fact có thể dùng | Giới hạn |
| --- | --- | --- |
| [Báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx) | Bản kế hoạch 3 tuần nêu 5 tiêu chí cho bài độc thoại | Chưa có sign-off học thuật riêng cho rubric hoặc band mapping |
| [CEFR Companion Volume 2020, Appendix 3](https://rm.coe.int/cefr-companion-volume-with-new-descriptors-2020/16809ea0d4) | Bảng qualitative features mở rộng có Range, Accuracy, Fluency, Interaction, Coherence, Phonology | Descriptors không tự biến thành thuật toán điểm; `Interaction` cần task có tương tác |
| [Đề cương gốc của nhóm](../../../sources/README.md) | Có kế hoạch dài hạn gồm 6 tiêu chí, human rating và validation | Scope 10 tuần/claim chưa duyệt không tự áp dụng cho bản dựng 3 tuần |
| [scikit-learn model persistence](https://scikit-learn.org/stable/model_persistence.html) | Lựa chọn lưu model có rủi ro tương thích và an toàn tùy định dạng | Chưa chọn thư viện/format; cần manifest/hash/schema cho artifact thực |
| [Kiểm tra scorer/model lịch sử](../../../sources/scoring-audit.md) | Ridge overall scorer và model JSON đã tồn tại; bốn weight DeBERTa/manifest ở kho riêng; năm tiêu chí chỉ có coverage trong app cũ | Không chuyển code/metric vào repo mới; model cũ là ứng viên cần duyệt quyền, tương thích và đánh giá |

## Adaptation Map

| Hạng mục | Quyết định bản nháp | Lý do |
| --- | --- | --- |
| Đơn vị suy luận `one response` | PROPOSED | Khớp luồng nộp một bài W2; model huấn luyện theo whole exam không dùng trực tiếp |
| Ridge artifact do nhóm tạo | OPEN — ứng viên tái kiểm, không tự mang sang | Có overall score theo một response, nhưng cần xác minh feature/ASR/VAD/unit/license và đánh giá mới |
| Refusal path `NOT_EVALUATED` | ADOPT như điều kiện an toàn W2 | Thể hiện đúng khoảng trống dữ liệu/approval |
| 5 tiêu chí độc thoại | PROPOSED theo lựa chọn của chủ dự án cho bản nháp W2 | Chủ dự án chọn giữ field `Interaction=null` với reason `insufficient_evidence` ngày 25/09/2026; vẫn cần review học thuật cho 5 tiêu chí |
| DeBERTa weight do nhóm tạo | OPEN — nhánh nghiên cứu riêng | Có weight và dev report lịch sử, chưa tích hợp app; cần tài nguyên và test/inference mới |
| Band mapping/probability/calibration | OPEN | Phải có rubric, nhãn và protocol kiểm định phù hợp |

## Evidence cần trước khi phát điểm

- Với Ridge lịch sử: rubric version và người duyệt; task/response unit; quyền dùng corpus; feature order, ASR/VAD/config, script/manifest/hash, speaker split và test trên pipeline mới. Với DeBERTa: quyền truy cập weight, resource, inference adapter và đánh giá ngoài dev nếu claim rộng hơn.
- Nếu thiếu điều kiện trọng yếu, M05-TASK-002/003 giữ `BLOCKED` hoặc `NOT_RUN`; M06 báo tình trạng thiếu bằng chứng. Không lấy metric trong report/docstring cũ làm metric repo mới. Scorer cũ chỉ có overall score, nên không suy năm điểm criterion từ coverage.

**CODEX CHECK RESULT:** phát hiện xung đột giữa đề cương 6 tiêu chí dài hạn và bản nháp W2 5 tiêu chí; đã tách scope. Quyền/tương thích của artifact và rubric tiêu chí vẫn `OPEN`. **User decision Research mode và Phase 03:** PENDING.
