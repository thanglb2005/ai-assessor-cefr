# M05 — 02 Research (khảo sát rubric và scorer)

> **DRAFT v0.1 · 25/09/2026.** Phase 01 còn PENDING; `RESEARCH MODE: RUN` mới là đề xuất. Không khóa rubric, band mapping hoặc model từ nội dung file này.

## Câu hỏi nghiên cứu W2

1. Chưa có rubric Speaking được giảng viên duyệt hay nhãn riêng năm tiêu chí trong nguồn đã kiểm tra, theo xác nhận chủ dự án. Khi nào cần xây và duyệt rubric đó; phần overall từ nhãn corpus được mô tả ra sao?
2. Dữ liệu nhãn và model Ridge/DeBERTa trong hồ sơ kỹ thuật nội bộ đáp ứng điều kiện provenance, quyền sử dụng và tương thích của dự án đến mức nào?
3. Nếu chưa đủ, report W2 nên hiển thị `NOT_EVALUATED` đến mức nào để vẫn có giá trị chẩn đoán mà không bịa CEFR band?

## Nguồn đã xem

| Nguồn | Fact có thể dùng | Giới hạn |
| --- | --- | --- |
| [Báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx) | Bản kế hoạch 3 tuần nêu 5 tiêu chí cho bài độc thoại | Chưa có sign-off học thuật riêng cho rubric hoặc band mapping |
| [CEFR Companion Volume 2020, Appendix 3](https://rm.coe.int/cefr-companion-volume-with-new-descriptors-2020/16809ea0d4) | Bảng qualitative features mở rộng có Range, Accuracy, Fluency, Interaction, Coherence, Phonology | Descriptors không tự biến thành thuật toán điểm; `Interaction` cần task có tương tác |
| [Đề cương gốc của nhóm](../../../sources/README.md) | Có kế hoạch dài hạn gồm 6 tiêu chí, human rating và validation | Phạm vi 10 tuần và các claim chưa duyệt không tự áp dụng cho kế hoạch ba tuần |
| [scikit-learn model persistence](https://scikit-learn.org/stable/model_persistence.html) | Lựa chọn lưu model có rủi ro tương thích và an toàn tùy định dạng | Chưa chọn thư viện/format; cần manifest/hash/schema cho artifact thực |
| [Kiểm tra scorer/model của nhóm](../../../sources/scoring-audit.md) | Ridge v2 đã được dùng cho overall; bốn weight DeBERTa/manifest nằm trong kho model riêng. Implementation đã khảo sát có năm `CriterionScore` cùng nhận một overall; `confidence` là coverage | Model là ứng viên cần duyệt quyền, kiểm tương thích và đánh giá trên pipeline hiện hành |

## Adaptation Map

| Hạng mục | Quyết định bản nháp | Lý do |
| --- | --- | --- |
| Đơn vị suy luận `one response` | PROPOSED | Khớp luồng nộp một bài W2; model huấn luyện theo whole exam không dùng trực tiếp |
| Ridge v2 do nhóm tạo | Ứng viên baseline overall W2, chưa tích hợp vào pipeline hiện hành | Model đã được kiểm chứng cho một response; kiểm hash, feature/ASR/VAD/unit/quyền trước khi dùng |
| Refusal path `NOT_EVALUATED` | ADOPT như điều kiện an toàn W2 | Thể hiện đúng khoảng trống dữ liệu/approval |
| 5 tiêu chí độc thoại | PROPOSED theo lựa chọn của chủ dự án cho bản nháp W2 | Chủ dự án chọn giữ field `Interaction=null` với reason `insufficient_evidence` ngày 25/09/2026; vẫn cần review học thuật cho 5 tiêu chí |
| DeBERTa weight do nhóm tạo | OPEN — nhánh nghiên cứu riêng | Có weight và dev report; chưa thuộc pipeline hiện hành, cần tài nguyên cùng test/inference riêng |
| Band mapping/calibration | Band threshold có trong Ridge v2; độ phù hợp với pipeline hiện hành đang OPEN | Giữ nguồn và version của threshold; chưa tuyên bố xác suất hay độ chính xác ở population mục tiêu |
| Năm dòng tiêu chí trong output | DECIDED — chỉ coverage/evidence, không score/band | Chủ dự án chọn ngày 25/09/2026; implementation đã khảo sát lặp overall vào năm dòng và chưa có năm nhãn/model riêng |

## Evidence cần trước khi phát điểm

- Với Ridge v2: ghi nguồn và SHA-256; kiểm task/response unit, quyền dùng corpus, feature order, ASR/VAD/config, band threshold, speaker split và test trên pipeline hiện hành. Rubric chuyên môn/nhãn riêng cần trước khi công bố năm điểm tiêu chí độc lập, không phải trước khi thiết kế overall baseline. Với DeBERTa: quyền truy cập weight, resource, inference adapter và đánh giá ngoài dev nếu claim rộng hơn.
- Nếu thiếu điều kiện trọng yếu, M05-TASK-002/003 giữ `BLOCKED` hoặc `NOT_RUN`; M06 báo tình trạng thiếu bằng chứng. Metric của dự án phải gắn với dataset, protocol và revision hiện hành. Implementation đã khảo sát có năm field `score_0_6` cùng nhận một overall; sản phẩm chỉ hiển thị overall và coverage.

**CODEX CHECK RESULT:** phát hiện xung đột giữa đề cương 6 tiêu chí dài hạn và bản nháp W2 5 tiêu chí; đã tách scope. Rubric/nhãn riêng năm tiêu chí được ghi `CHƯA CÓ`; quyền và tương thích artifact trong pipeline hiện hành vẫn `OPEN`. **User decision Research mode và Phase 03:** PENDING.
