# W3-PROMPT-001-FIX-01 — Bundled review correction

PROMPT ID: W3-PROMPT-001-FIX-01
TASK IDS: W3-TASK-001, W3-TASK-002
SCOPE ROOT: docs/sdd/features/w3-local-integration/
REPO ROOT: /tmp/aicefr-w3-pipeline
BRANCH: feat/W3-pipeline
BASE CODE: 66d23d49b55c2b7df2c82341e8190675e87065ff
BASE HEAD: 1aaa7aaa5b037b13dc0618baa848b4bfe02539dd
AUTHORIZATION: chỉ dẫn trực tiếp của Thắng; gpt-6-luna implement, Codex review; user verdict PENDING.

Giữ prompt gốc và AMEND-01/02, allowed files; source/tests correction commit riêng rồi evidence. Verify BASE HEAD; baseline workbook/prompt metadata dirty để nguyên. Không sửa root hoặc lane khác; không cài shared venv. Không dùng fingerprint trước implementation như fingerprint cuối.

MAJOR-01: Transaction orchestration chưa được kiểm chứng với SQLite thật. Thêm tests coordinator với SQLite ResponseService + SQLiteReportRepository + SQLiteReviewRepository/ReviewService thực, audio kiểm thử được tạo. Chứng minh report/status/candidate cùng commit; candidate insertion/report persistence lỗi rollback tất cả final writes, FAILED có reason phù hợp, không report mồ côi/queue thiếu; duplicate/stale claims không chạy ASR lại; restart giữ report/queue; decision/report callback lỗi rollback toàn bộ teacher result/audit. Existing repository tests không thay coordinator integration tests. Giữ atomic unit of work hiện có và sửa bug nếu tests phát hiện.

MAJOR-02: reason mặc định ASR_FAILED khiến lỗi blob/extractor/report/database bị gắn ASR. Dùng reason có nghĩa cho boundary (existing PIPELINE_ENQUEUE_FAILED cho unexpected pipeline failure), giữ ASR/QC refusal reasons trong report/status/candidate. Khi ASR thất bại mà artifact thiếu, scorer ưu tiên MODEL_VERSION_MISSING hiện làm mất ASR reason; coordinator phải giữ refusal gốc và null overall, không bịa features/score. QC REVIEW reasons tuple có thể rỗng; fail closed với QC_MEASUREMENT_MISSING thay index crash. Failure recovery không silently swallow sai revision để bỏ RUNNING không có báo cáo; test rollback/current revision và safe logs, không log exception payload.

MAJOR-03: Constructor public không có type hints; protocol _Responses unused và blobs:object. Gắn port Protocol/service types thật cho responses/reports/reviews/asr/extractor/scorer, tránh getattr unit-of-work phụ thuộc object không rõ. Port transaction optional có thể giữ cho fixture, nhưng loại unused protocol và làm explicit SQLite orchestration responsibility. Không thêm framework/dependency.

Report cần source versions và evidence thật nếu có theo Specification. Khi transcript words hoặc finite FeatureValues tồn tại, tạo EvidenceRef dùng response/source version/timestamps/value thật và validation M06. Không invent comments/evidence cho refusal/test-only runtime. Có test foreign/stale refs không xuất hiện trong report.

Coverage hiện coordinator 76.9% line / 45.5% branch bỏ nhiều critical paths. Bổ sung scenarios container sniff corrupt/FLAC/OGG/MP3 nếu codec có sẵn; non-QUEUED, stale claim, missing transcript, scorer refusal/near-boundary, exceptions và rollback. M02/M08 giữ policy >=90% line >=85% branch trên packages đã duyệt; đo pipeline riêng và nêu uncovered thật, không test mirror chỉ để số. Chạy full regression với AICEFR_MODEL_DIR=/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src/aicefr/scoring/models và PYTHONPATH=src. Ruff/diff guard. Evidence raw-pipeline-fix-01.md dẫn commit, commands và coverage. Return source/evidence SHA.
