# Raw implementation report — W3 pipeline lane

- Prompt: `W3-PROMPT-001`
- Amendments: `W3-PROMPT-001-AMEND-01` (migration regression scope), `W3-PROMPT-001-AMEND-02` (schema version regression expectations)
- Tasks: `W3-TASK-001`, `W3-TASK-002`
- Starting fingerprint: `411c2366ca9d656366523883a3a6f7383506620208b8d0d7ba1495358c20aa84` (`sdd-workspace-v2`)
- Base revision: `7bb327b655c67d8eb5aafc4cd8ec9481fabdff28`
- Code commit: `66d23d49b55c2b7df2c82341e8190675e87065ff`
- Committed source tree fingerprint (`git tree`): `925e1fc0bdcd8917851900b8e73eea85b309a299`
- Branch: `feat/W3-pipeline`

## Thay đổi

Thêm `PipelineCoordinator` xử lý đồng bộ response `QUEUED` qua claim CAS, đọc blob có checksum qua `ResponseService`, xác định audio container từ bytes và đi qua QC/ASR/features/scoring/report. QC `REJECT` không gọi ASR và không tạo report; QC `REVIEW` tạo report `NOT_EVALUATED` và review candidate. Kết quả cần review giữ candidate ở revision response cuối. Report, status và candidate được ghi trong cùng unit of work khi dùng SQLite; lỗi ngoài dự kiến chuyển response thành `FAILED` với reason code ổn định, không ghi exception payload.

Thêm `SQLiteReportRepository` trên connection dùng chung với review, schema v3 và migration v1/v2→v3. Repository tham gia transaction đang mở, cho phép callback cập nhật teacher result rollback đồng thời decision và audit. Student submit đọc lại response sau synchronous enqueue để trả status persisted.

## File đã commit

- `src/aicefr/pipeline/__init__.py`
- `src/aicefr/pipeline/coordinator.py`
- `src/aicefr/report/sqlite.py`
- `src/aicefr/report/service.py`
- `src/aicefr/storage/sqlite.py`
- `src/aicefr/api/student.py`
- `tests/pipeline/test_coordinator.py`
- `tests/report/test_sqlite_report.py`
- `tests/storage/test_report_migration.py`
- `tests/storage/test_sqlite_memory_migration.py`
- `tests/storage/test_sqlite_blob_store.py`
- `docs/sdd/features/w3-local-integration/prompts/W3-PROMPT-001-pipeline.md`

## Kiểm tra

- `PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python -m pytest -q -m 'not smoke' --cov=aicefr.pipeline --cov=aicefr.report --cov=aicefr.storage --cov-branch --cov-report=term-missing --cov-report=json:/tmp/aicefr-w3-pipeline-coverage.json` — exit 0; **199 passed, 10 skipped**. Các skipped đều cần `ridge_resp_v2.json` qua `AICEFR_MODEL_DIR`; không có model được tải.
- `/tmp/aicefr-w3-venv/bin/ruff check src/aicefr/pipeline src/aicefr/report/sqlite.py src/aicefr/report/service.py src/aicefr/storage/sqlite.py src/aicefr/api/student.py tests/pipeline tests/report/test_sqlite_report.py tests/storage/test_report_migration.py tests/storage/test_sqlite_memory_migration.py tests/storage/test_sqlite_blob_store.py` — exit 0, PASS.
- `git diff HEAD --check` — exit 0, PASS.
- Coverage line/branch: `pipeline/coordinator.py` **76.9% / 45.5%** (10/22 branches); `report/sqlite.py` **100% / 100%** (2/2); `report/service.py` **87.9% / 77.8%** (42/54); `storage/sqlite.py` **96.6% / 91.7%** (22/24). Coordinator branch coverage còn thấp ở các nhánh container ít dùng (FLAC/OGG/MP3), repository không có metadata fallback và lỗi persistence/status; đã có kiểm thử QC PASS/REVIEW/REJECT, ASR không gọi trên REVIEW/REJECT, duplicate CAS, privacy log, report restart, migration v1/v2 và rollback callback SQLite thật.

## Giới hạn và giả định

ASR/scorer/features trong pipeline behavior tests là injected doubles; không đo accuracy CEFR và không chạy model thật. Smoke ASR local: `NOT_RUN` do lane này không có quyền/trọng số/audio thật. Mười bài test model-dependent giữ nguyên skip reason có sẵn. Failure path dùng reason code ổn định mặc định `ASR_FAILED`; log chỉ chứa response ID. Formal phase verdict và user acceptance vẫn `PENDING`.

Không dùng nguồn ngoài; không có source citation bổ sung.
