# M07-EVID-DIRECT-20260928 — Direct implementation evidence

## Trạng thái và provenance

- Task: `M07-TASK-001`, `M07-TASK-002` và integration/QA W3 bằng fixture.
- Cách thực hiện: chủ dự án yêu cầu Codex triển khai trực tiếp ngày 28/09/2026. Không có Prompt ID/Antigravity handoff và không có claim Phase 05/07/08 hay user acceptance.
- HEAD base: `db34379f96d439ace6d504b60c31bc01cab9a902`; source/docs đang là current uncommitted workspace.
- WORKSPACE FINGERPRINT: d330136d7e842ac36decee5d7836c2985f03168099afe947c4eb663f6374c6f6
- Dữ liệu: chỉ pseudonymous fixture; audit không mang audio, transcript, blob path hay token.

## Diff được quan sát

- `contract-reason-map.md`: `CONTRACT_DRAFT` cho reason routing, state, audit, M06 verification và impact M05/M06/M08.
- `src/aicefr/review/routing.py`, `service.py`, `sqlite.py`: reason-to-candidate, teacher-only queue/claim/decision, candidate + response revision checks, append-only audit và durable SQLite decision verification.
- `src/aicefr/api/review.py`, `templates.py`, `wsgi.py`: teacher queue/API/form routes; cookie mutation dùng same-origin check.
- `src/aicefr/contracts.py`, `src/aicefr/storage/sqlite.py`: typed review contracts và v2 migration cho candidate/decision tables.

## Checks đã chạy

| Check | Kết quả thực tế |
| --- | --- |
| Ruff trên API/report/review/storage/contracts và tests liên quan | exit 0, `All checks passed!` |
| `pytest -p no:cacheprovider -q tests/api tests/report tests/review tests/storage/test_sqlite_memory_migration.py` | exit 0, `28 passed in 2.15s` |
| `python -m compileall -q src tests` | exit 0 |
| `git diff --check` | exit 0; chỉ có cảnh báo line ending Git, không có whitespace error |

M07-TEST-001/002/003/004/005 được ánh xạ trong `tests/review/test_review_service.py` và WSGI test. Những test này kiểm reason route, teacher role, stale revision, durable review adapter, audit-backed report update và rollback callback fixture.

## UI/browser QA và cross-owner review

WSGI form/API được fixture test. Preflight browser ngày 28/09/2026 trả `playwright-unavailable`; browser automation/ảnh là **NOT_RUN**. Review từ owner M05 (reason), M06 (presentation) và M08 (schema/persistence) chưa có; trạng thái **PENDING**.

## Giới hạn và verdict

- SQLite adapter dùng M08 metadata schema nhưng M08 owner cần review migration v2 trước khi merge.
- Integration callback nguyên tử trong fixture/M07 metadata transaction; persistent M06 repository transaction cần được thiết kế cùng owner khi có storage report thật.
- Self-review technical đã ghi tại `reviews/review-log.md`; final verification và user verdict: **PENDING**.
