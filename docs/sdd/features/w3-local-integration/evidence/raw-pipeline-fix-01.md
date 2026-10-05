# Raw correction report — W3 pipeline FIX-01

- Prompt: `W3-PROMPT-001-FIX-01`
- Tasks: `W3-TASK-001`, `W3-TASK-002`
- Base code revision: `66d23d49b55c2b7df2c82341e8190675e87065ff`
- Base HEAD: `1aaa7aaa5b037b13dc0618baa848b4bfe02539dd`
- Source correction commit: `5056d05dfb767e8756ddf47de5c7e096800d5ba9`
- Source commit tree fingerprint: `3b19f07ae79a5b028b538f0fcfab6b595e62f834`
- Branch: `feat/W3-pipeline`
- User verdict: `PENDING`

## Đã sửa

`PipelineCoordinator` nay nhận type hints rõ cho `ResponseService`, `ReportService`, `ReviewService`, ASR port, `FeatureExtractor` và `RidgeScorer`. Coordinator gọi trực tiếp transaction/CAS thuộc SQLite metadata service, không dùng `getattr` hay fallback unit-of-work không rõ ownership. CAS đối chiếu revision, trạng thái, owner, task và toàn bộ `BlobRef` trước khi claim.

Report, final response status và review candidate cùng transaction SQLite. Lỗi ghi report/candidate rollback final writes, rồi response được chuyển `FAILED` với `PIPELINE_ENQUEUE_FAILED`; nếu revision thay đổi đồng thời, recovery đọc lại và chỉ retry khi response vẫn `RUNNING`. Lỗi recovery không còn bị nuốt. QC `REVIEW` rỗng reasons dùng `QC_MEASUREMENT_MISSING`. ASR refusal reasons được giữ trước model refusal, score/band bị xóa khi ASR chưa `OK`, và status/candidate giữ reason gốc.

Report ghi provenance QC, ASR engine/model, transcript và features. Evidence refs/comment requests được tạo từ word timestamps hợp lệ và feature values hữu hạn thật; M06 xác minh feature ID/value với `FeatureSet`. Evidence ngoại lai, version cũ, timestamp không hợp lệ, feature thiếu hoặc value khác bị loại; test-only transcript không sinh evidence.

Integration tests dùng SQLite `ResponseService`, report repository, review repository/service thật với audio tự tạo. Bao phủ commit/restart, rollback report/candidate/teacher callback, stale/duplicate/forged claims, race khi recover failure, refusal reason preservation, near-boundary queue, missing transcript, QC empty-reason fallback, corrupt/whitelist container và generated WAV/FLAC/OGG/MP3.

## Files trong source commit

- `src/aicefr/pipeline/coordinator.py`
- `src/aicefr/report/service.py`
- `src/aicefr/storage/sqlite.py`
- `tests/pipeline/test_coordinator.py`

## Kiểm tra cuối

- `AICEFR_MODEL_DIR=/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src/aicefr/scoring/models PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python -m pytest -q -m 'not smoke' --cov=aicefr.pipeline --cov=aicefr.report --cov=aicefr.storage --cov-branch --cov-report=term-missing --cov-report=json:/tmp/aicefr-w3-pipeline-fix01-coverage.json` — exit 0, **225 passed**.
- `/tmp/aicefr-w3-venv/bin/ruff check src/aicefr/pipeline src/aicefr/report/sqlite.py src/aicefr/report/service.py src/aicefr/storage/sqlite.py src/aicefr/api/student.py tests/pipeline tests/report/test_sqlite_report.py tests/storage/test_report_migration.py tests/storage/test_sqlite_memory_migration.py tests/storage/test_sqlite_blob_store.py` — exit 0, PASS.
- `git diff --check` — exit 0, PASS.
- Final coverage: pipeline coordinator **99.2% line, 31/32 branches (96.9%)**; SQLite report repo **100% line/branch**; `storage/sqlite.py` **96.2% line, 23/26 branches (88.5%)**. M08 storage exceeds the 90% line/85% branch policy. `report/service.py` is **87.6% line, 48/60 branches (80%)**; its remaining uncovered paths include comment/evidence validation error variants and teacher-result shape guards.

## Giới hạn

Pipeline integration sử dụng ASR/scorer doubles để kiểm tra service orchestration offline. Không chạy ASR model thật và không đo CEFR accuracy. Model artifact local được dùng cho regression suite hiện có; không tải model/network. Không có nguồn ngoài cần trích dẫn. Prompt metadata, AI workbook, status và worktree khác vẫn thuộc root, không nằm trong các commit của lane này.
