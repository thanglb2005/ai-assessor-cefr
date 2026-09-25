# AI Assessor CEFR — context cấp dự án

**Trạng thái:** W1 (14–18/09/2026) đã hoàn thành theo xác nhận của người dùng; phạm vi/SDD của repo mới đang chờ duyệt cho W2–W3.

Mục tiêu dự kiến là một hệ thống hỗ trợ đánh giá bài nói tiếng Anh độc thoại A2–B2 cho sinh viên đại học Việt Nam, phục vụ học tập và giảng viên duyệt. Mọi band/điểm là ước lượng; không cấp chứng chỉ hay tự quyết định đậu/rớt. Phạm vi 5 tiêu chí trong báo cáo tuần 1 là **giả định lập kế hoạch đang chờ xác nhận**. `Interaction` không được chấm từ độc thoại.

- Bản đồ tài liệu: [`docs/README.md`](docs/README.md); [nguồn đề tài do nhóm tạo](docs/sources/README.md).
- Tổng quan ba tuần: [`docs/plan/three-week-roadmap.md`](docs/plan/three-week-roadmap.md); file từng tuần nằm trong docs/plan/week-01.md, week-02.md, week-03.md.
- Chỉ mục prompt/evidence theo module: [`docs/sdd/prompt-log.md`](docs/sdd/prompt-log.md).
- Hồ sơ minh chứng theo rubric: [`docs/evidence/README.md`](docs/evidence/README.md).
- Nguồn yêu cầu/tiến độ cho từng module: `docs/sdd/modules/<module>/01-requirement.md` và `07-status.md`.
- Tổng kết W1 và giả định giờ công: docs/reports/week-01/tong-ket-w1.md.
- Báo cáo tuần 1 bản gốc: `docs/reports/week-01/bao-cao-tuan-01.docx`.
- Rubric đánh giá đồ án: `docs/rubric/`.

Repo `../aiassessor-cefr` là phiên bản trước do chính chủ dự án phát triển; repo mới viết lại mã nguồn, không clone implementation. Hai đề cương gốc của nhóm đã được lưu tại `docs/sources/` có checksum. Metric, approval và test result của bản trước không tự chuyển thành bằng chứng của bản dựng mới. SDD W2 hiện là bản nháp Phase 01; chưa có mã nguồn, Git baseline, prompt triển khai hoặc lệnh test ổn định cho repo mới.
