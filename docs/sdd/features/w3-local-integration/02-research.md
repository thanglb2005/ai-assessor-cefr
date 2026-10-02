# W3 — Research

Version v0.1 · 02/10/2026. Baseline code: 2b428ceea9e4459f3235d4ce67f10bab31585ebf.

## Findings từ repo

- M01 StudentService có PipelineStarter port; chưa có coordinator/entrypoint. StudentTeacherApp là WSGI, không cần thêm FastAPI.
- M08 SQLiteStore schema v2 có account/session/consent/response/audit và M07 queue/decision. M06 hiện chỉ có MemoryReportRepository; cần report repository trên cùng connection để review callback rollback cùng decision/audit.
- M02 yêu cầu QCConfig tường minh và chỉ dispatch PASS; REVIEW/REJECT không gọi ASR.
- AsrService và FeatureExtractor nhận injected engines; adapter local chưa có. RidgeScorer phải giữ pinned SHA-256.
- Artifact nội bộ do nhóm tạo tại ../ai-assessor-cefr-thamchie/src/aicefr/scoring/models/ridge_resp_v2.json có SHA-256 7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a (đã đo). Trained provenance: whisper-small, silero, threshold 0.5, min_silence_ms 150, feature v3, 18 features. Không đưa artifact vào Git.
- Baseline kiểm ngày 02/10: 189 PASS, 10 SKIPPED do thiếu AICEFR_MODEL_DIR; Ruff src/tests PASS. Đây không phải metric CEFR hay user study.

## Quyết định triển khai theo chỉ dẫn trực tiếp

Dùng stdlib WSGI/SQLite và existing service contracts; không thêm production framework. Các adapter lazy-load optional extras đã khai báo; local_files_only và cấu hình provenance phải kiểm bằng tài liệu chính thức. Agent speech bổ sung nguồn primary trong raw report; Codex xác minh trước kết luận. Playwright/openpyxl chỉ dùng trong virtualenv kiểm thử /tmp.

## Rủi ro

SQLite single-process demo phải chạy server tuần tự; report/review cùng connection cần transaction-aware put, không mở nested BEGIN. Không claim real ASR smoke từ mocked engines. Product/data-governance decisions ngoài scope giữ pending.
