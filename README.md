# AI Assessor CEFR

Dự án hỗ trợ đánh giá bài nói tiếng Anh độc thoại A2–B2, phục vụ học tập và giảng viên duyệt. W2 đã có mã nguồn các module; W3 nối luồng sinh viên → QC/ASR/features/scoring → báo cáo → giảng viên duyệt trên ứng dụng local. Overall AI là ước lượng; kết quả giảng viên được lưu riêng. Khi thiếu model, bằng chứng hoặc provenance phù hợp, hệ thống trả trạng thái từ chối với overall `null`.

Chạy với Python 3.11 trở lên:

```bash
python3 -m venv /tmp/aicefr-local-venv
source /tmp/aicefr-local-venv/bin/activate
python -m pip install -e '.[dev]'
python -m aicefr.local --help
python -m aicefr.local init-demo --data-dir /tmp/aicefr-local-data --actor-id fixture-student --role student
python -m aicefr.local init-demo --data-dir /tmp/aicefr-local-data --actor-id fixture-teacher --role teacher
python -m aicefr.local serve --data-dir /tmp/aicefr-local-data --demo
```

Mở `http://127.0.0.1:8000/login`. Mật khẩu được nhập riêng khi tạo từng tài khoản. Chế độ `--demo` dùng tài khoản/audio kiểm thử và QC dành cho trình diễn; cần cấu hình model local để chạy ASR/scoring thật. Xem [hướng dẫn local đầy đủ](docs/local-run.md) về cấu hình, audio kiểm thử, model, kiểm thử và khởi động lại.

- [Quy tắc chung của nhóm](AGENTS.md) · [skill SDD dùng chung](.agents/skills/sdd-antigravity-orchestrator/SKILL.md) · [điểm vào Antigravity](ANTIGRAVITY.md)
- [Bản đồ tài liệu](docs/README.md)
- [Tổng quan 3 tuần](docs/plan/three-week-roadmap.md): [W1](docs/plan/week-01.md) · [W2](docs/plan/week-02.md) · [W3](docs/plan/week-03.md)
- SDD riêng của 8 module và [chỉ mục Prompt Log](docs/sdd/prompt-log.md)
- [Hồ sơ minh chứng theo rubric](docs/evidence/README.md)
- [W3 Status](docs/sdd/features/w3-local-integration/07-status.md) · [Prompt Log](docs/sdd/features/w3-local-integration/prompts/prompt-log.md) · [Evidence](docs/sdd/features/w3-local-integration/evidence/evidence-manifest.md) · [Code Review](docs/sdd/features/w3-local-integration/reviews/review-log.md)
- [Tổng kết W1](docs/reports/week-01/tong-ket-w1.md) và [báo cáo Word](docs/reports/week-01/bao-cao-tuan-01.docx)
- [Rubric đồ án](docs/rubric/Rubric_Do_An_Mon_Hoc_CNPM_sinhvien.docx.pdf)

Trạng thái phê duyệt đọc từ scope/module tương ứng. W3 được triển khai theo chỉ dẫn trực tiếp của Thắng, còn verdict nghiệm thu cuối giữ `PENDING`. Tài liệu gốc, model provenance và hồ sơ kỹ thuật nội bộ của nhóm được quản lý tại [docs/sources/](docs/sources/README.md); kết quả của dự án được ghi theo revision và evidence hiện hành.
