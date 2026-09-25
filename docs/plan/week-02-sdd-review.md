# Tự rà soát hồ sơ SDD W2 — 25/09/2026

**Phạm vi:** rà soát tài liệu đã soạn để bàn giao cho Antigravity; chưa rà soát mã nguồn của dự án vì `src/` và `tests/` chưa có. Đây là kiểm tra của Codex, không thay phê duyệt của chủ dự án tại các checkpoint SDD.

## Kết quả kiểm tra

| Mục | Kết quả tại thời điểm rà soát |
| --- | --- |
| Cấu trúc | 8/8 module M01–M08 có Requirement, Specification, Test Plan, Plan, Tasks, Status, Prompt Log, Evidence Manifest và Review Log; M03/M05 có Research nháp. |
| Truy vết | 42 ca test dự kiến và 20 task nháp; FR/AC đều được dẫn trong Specification, Test Plan và Tasks; mọi Test ID được dẫn trong Tasks. Đây là kiểm tra liên kết, không phải test đã chạy. |
| Tài liệu và nguồn | Liên kết Markdown nội bộ tồn tại; checksum của 2 DOCX đề cương và báo cáo fine-tune lịch sử khớp danh mục nguồn. Bốn hình nhúng báo cáo W1 và hai biến thể class diagram được giữ riêng, không coi là cùng một bản. |
| AI Prompt Log | File XLSX mở được và CRC hợp lệ; công thức sheet Tổng hợp dẫn cả ba sheet Thắng, Sang, Nguyên. Ba dòng mẫu `abc` đã được xóa; 4 prompt Codex hiện được ghi ở sheet Thắng, cache tổng hợp là 4. Chưa có prompt Antigravity phát hành. |
| Rule/skill nhóm | Đã thêm `AGENTS.md` làm quy tắc chung, `ANTIGRAVITY.md` làm điểm vào và đóng gói đúng một bản `sdd-antigravity-orchestrator` trong repo; đây là chuẩn bàn giao W2, không phải bằng chứng file rule W1. |
| Git | Đã khởi tạo Git cho repo dự án ngày 25/09/2026 và thêm `.gitignore` cho secret, DB, audio, model weights, cache. Mốc khởi tạo này được ghi riêng với tiến độ W1. |
| Trạng thái SDD | Cả 8 module vẫn ở Phase 01 DRAFT/PENDING; Research M03/M05 chỉ là đề xuất `RUN`. Chưa có approval Phase 03–05, implementation, raw report, test result hay nghiệm thu. |

Kiểm tra sau khi đóng gói rule/skill: 20 file skill khớp checksum bản cá nhân; 31 test của script skill chạy đạt; 312 liên kết Markdown nội bộ không bị đứt; XLSX qua kiểm tra ZIP CRC và công thức tổng hợp vẫn dẫn cả ba sheet. Các kiểm tra này xác minh bộ tài liệu/skill; test ứng dụng được theo dõi riêng trong từng module.

## Phát hiện và cách xử lý

1. M06 từng có tên dễ nhầm với thư mục hồ sơ rubric. Đã đổi thành `m06-diagnostic-report`; `docs/evidence/` tiếp tục dành cho minh chứng nộp đồ án.
2. Hồ sơ quyết định QD-04 ghi phạm vi độc thoại với năm tiêu chí có evidence; chủ dự án quyết định giữ `Interaction=null` và reason `insufficient_evidence`. M05 và roadmap đã được cập nhật theo quyết định này.
3. Nhóm có Ridge scorer cho điểm tổng thể một response và model DeBERTa đã fine-tune trong kho model riêng. [Khảo sát nền tảng kỹ thuật nội bộ](../sources/code-survey.md) ghi nhận 442 test chạy đạt và năm `CriterionScore` cùng nhận một overall; chưa có năm model/nhãn riêng để kiểm định năm điểm độc lập. M05 xem model có provenance này là ứng viên baseline có điều kiện và yêu cầu test riêng trên revision hiện hành.
4. Một số Plan còn ghi Git chưa khởi tạo và bảng trace dùng ID viết tắt. Đã cập nhật trạng thái Git và viết đủ ID để kiểm tra tự động.
5. Rà soát cấu trúc tài liệu: kết quả khảo sát kỹ thuật được tập trung tại `docs/sources/code-survey.md`; bản text rubric một dòng đã bỏ vì PDF gốc có thể tìm kiếm. Các hình nhúng W1, hai biến thể class diagram, workbook Prompt Log, hồ sơ theo rubric và log/evidence từng module được giữ vì có vai trò riêng.

## Việc còn mở trước khi phát prompt triển khai

- Chủ dự án xác nhận hiện chưa có rubric Speaking được giảng viên duyệt và nhãn riêng năm tiêu chí trong nguồn đã kiểm tra. Chủ dự án đã chọn chỉ hiển thị overall score/band và coverage của năm tiêu chí; overall Ridge v2 có thể được tích hợp sau khi xác minh quyền, artifact hash, feature order, ASR/VAD, inference unit và test trên pipeline hiện hành. Band mapping/ngưỡng review cần ghi version và giới hạn rõ.
- Chọn ASR engine/model local, máy và audio smoke có quyền sử dụng; nếu thiếu, M03 smoke giữ `NOT_RUN`.
- Chủ dự án duyệt Requirement → Research mode → Specification → Test Plan → Plan/Tasks theo từng module trước khi phát prompt Antigravity. Owner Thắng/Sang/Nguyên trong W2–W3 vẫn là phân công đề xuất, chờ ba người xác nhận.
- Link Jira, file AI rules gốc có nguồn gốc W1, commit/đường dẫn W1 và xác nhận GVHD chưa có trong thư mục dự án. Rule/skill chung W2 đã sẵn trong repo; không ghi ngược thành chứng cứ W1. Giờ công W1 là giả định lập kế hoạch, không là timesheet.

**Kết luận:** W1 đóng tiến độ theo xác nhận người dùng, nhưng hồ sơ chứng minh độc lập vẫn PARTIAL. Nhóm có thể nhận owner và review SDD W2 với một rule/skill chung; chưa đủ điều kiện phát prompt implement, ghi `READY`, `DONE`, điểm CEFR thật hoặc test PASS cho dự án.
