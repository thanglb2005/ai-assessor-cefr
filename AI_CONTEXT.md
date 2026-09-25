# AI Assessor CEFR — context cấp dự án

**Trạng thái:** W1 (14–18/09/2026) đã hoàn thành theo xác nhận của chủ dự án; SDD của các module đang chờ duyệt để triển khai W2–W3.

Mục tiêu dự kiến là một hệ thống hỗ trợ đánh giá bài nói tiếng Anh độc thoại A2–B2 cho sinh viên đại học Việt Nam, phục vụ học tập và giảng viên duyệt. Mọi band/điểm là ước lượng; không cấp chứng chỉ hay tự quyết định đậu/rớt. Chủ dự án đã chọn 5 tiêu chí trong báo cáo tuần 1 làm bản nháp W2. Output W2 chỉ hiển thị overall score/band và coverage của từng tiêu chí; `Interaction=null` với lý do thiếu bằng chứng từ độc thoại. Rubric Speaking có phê duyệt học thuật vẫn chưa có trong nguồn đã kiểm tra.

- Quy tắc chung: [`AGENTS.md`](AGENTS.md); skill dùng chung: [`.agents/skills/sdd-antigravity-orchestrator/SKILL.md`](.agents/skills/sdd-antigravity-orchestrator/SKILL.md).
- Bản đồ tài liệu: [`docs/README.md`](docs/README.md); [nguồn đề tài do nhóm tạo](docs/sources/README.md).
- Tổng quan ba tuần: [`docs/plan/three-week-roadmap.md`](docs/plan/three-week-roadmap.md); file từng tuần nằm trong docs/plan/week-01.md, week-02.md, week-03.md.
- Chỉ mục prompt/evidence theo module: [`docs/sdd/prompt-log.md`](docs/sdd/prompt-log.md).
- Hồ sơ minh chứng theo rubric: [`docs/evidence/README.md`](docs/evidence/README.md).
- Nguồn yêu cầu/tiến độ cho từng module: `docs/sdd/modules/<module>/01-requirement.md` và `07-status.md`.
- Tổng kết W1 và giả định giờ công: docs/reports/week-01/tong-ket-w1.md.
- Báo cáo tuần 1 bản gốc: `docs/reports/week-01/bao-cao-tuan-01.docx`.
- Rubric đánh giá đồ án: `docs/rubric/`.

`ai-assessor-cefr` là dự án chính thức do nhóm phát triển từ đầu theo SDD. `docs/sources/` lưu đề cương, model provenance và hồ sơ kỹ thuật nội bộ do nhóm tạo trong quá trình hình thành đề tài; mỗi nguồn quan trọng có checksum hoặc đường dẫn xuất xứ. SDD W2 hiện ở Phase 01 DRAFT; mã nguồn và test của các module chưa được triển khai. Kết quả 442 test trong hồ sơ kỹ thuật nội bộ ghi nhận phạm vi kiểm thử của nền tảng đã nghiên cứu, còn kết quả của dự án sẽ được đo trên revision hiện hành và lưu trong evidence của từng module.
