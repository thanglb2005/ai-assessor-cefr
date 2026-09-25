# Tự rà soát hồ sơ SDD W2 — 25/09/2026

**Phạm vi:** rà soát tài liệu đã soạn để bàn giao cho Antigravity; chưa rà soát mã nguồn của bản dựng mới vì `src/` và `tests/` chưa có. Đây là kiểm tra của Codex, không thay phê duyệt của chủ dự án tại các checkpoint SDD.

## Kết quả kiểm tra

| Mục | Kết quả tại thời điểm rà soát |
| --- | --- |
| Cấu trúc | 8/8 module M01–M08 có Requirement, Specification, Test Plan, Plan, Tasks, Status, Prompt Log, Evidence Manifest và Review Log; M03/M05 có Research nháp. |
| Truy vết | 42 ca test dự kiến và 20 task nháp; FR/AC đều được dẫn trong Specification, Test Plan và Tasks; mọi Test ID được dẫn trong Tasks. Đây là kiểm tra liên kết, không phải test đã chạy. |
| Tài liệu và nguồn | Liên kết Markdown nội bộ tồn tại; checksum của 2 DOCX đề cương và báo cáo fine-tune lịch sử khớp danh mục nguồn. Bốn hình nhúng báo cáo W1 và hai biến thể class diagram được giữ riêng, không coi là cùng một bản. |
| AI Prompt Log | File XLSX mở được và CRC hợp lệ; công thức sheet Tổng hợp dẫn cả ba sheet Thắng, Sang, Nguyên. Ba dòng mẫu `abc` đã được xóa; bản ghi hiện tại ở sheet Thắng. Chưa có prompt Antigravity phát hành. |
| Git | Đã khởi tạo Git ở thư mục dự án mới ngày 25/09/2026 và thêm `.gitignore` cho secret, DB, audio, model weights, cache. Git mới không chứng minh có commit W1. |
| Trạng thái SDD | Cả 8 module vẫn ở Phase 01 DRAFT/PENDING; Research M03/M05 chỉ là đề xuất `RUN`. Chưa có approval Phase 03–05, implementation, raw report, test result hay nghiệm thu. |

## Phát hiện và cách xử lý

1. M06 từng có tên dễ nhầm với thư mục hồ sơ rubric. Đã đổi thành `m06-diagnostic-report`; `docs/evidence/` tiếp tục dành cho minh chứng nộp đồ án.
2. QD-04 của phiên bản trước bỏ `Interaction` khỏi output; chủ dự án quyết định cho bản mới giữ `Interaction=null` và reason `insufficient_evidence` khi chỉ có bài nói độc thoại. Đã cập nhật M05 và roadmap theo quyết định này.
3. Ứng dụng tham chiếu có Ridge scorer cho điểm tổng thể một response và model DeBERTa đã fine-tune ở kho riêng; [442 test của bản tham chiếu đã chạy đạt](../sources/reference-validation.md), không thay test repo mới. Bản tham chiếu mới kiểm tra có năm `CriterionScore`, song code gán cùng overall vào cả năm; chưa có năm model/nhãn riêng để kiểm định năm điểm độc lập. Đã sửa M05 để đánh giá artifact cũ như ứng viên có điều kiện, không phủ nhận kết quả lịch sử hoặc nhận metric đó là kết quả repo mới.
4. Một số Plan còn ghi Git chưa khởi tạo và bảng trace dùng ID viết tắt. Đã cập nhật trạng thái Git và viết đủ ID để kiểm tra tự động.

## Việc còn mở trước khi phát prompt triển khai

- Chủ dự án xác nhận hiện chưa có rubric Speaking được giảng viên duyệt và nhãn riêng năm tiêu chí trong nguồn đã kiểm tra. Chủ dự án đã chọn chỉ hiển thị overall score/band và coverage của năm tiêu chí; overall Ridge v2 có thể được tích hợp mới sau khi xác minh quyền, artifact hash, feature order, ASR/VAD, inference unit và test trên pipeline mới. Band mapping/ngưỡng review cần ghi version và giới hạn rõ.
- Chọn ASR engine/model local, máy và audio smoke có quyền sử dụng; nếu thiếu, M03 smoke giữ `NOT_RUN`.
- Chủ dự án duyệt Requirement → Research mode → Specification → Test Plan → Plan/Tasks theo từng module trước khi phát prompt Antigravity. Owner Thắng/Sang/Nguyên trong W2–W3 vẫn là phân công đề xuất, chờ ba người xác nhận.
- Link Jira, AI rules, commit/đường dẫn W1 và xác nhận GVHD chưa có trong thư mục mới. Giờ công W1 là giả định lập kế hoạch, không là timesheet.

**Kết luận:** tài liệu W2 đủ để chủ dự án review và quyết định scope từng module; chưa đủ điều kiện ghi `READY`, `DONE`, điểm CEFR thật hoặc test PASS cho bản dựng mới.
