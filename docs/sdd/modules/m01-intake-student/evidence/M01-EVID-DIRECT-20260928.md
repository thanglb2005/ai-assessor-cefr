# M01-EVID-DIRECT-20260928 — Direct implementation evidence

## Trạng thái và provenance

- Task: `M01-TASK-001`, `M01-TASK-002`, `M01-TASK-003`.
- Cách thực hiện: chủ dự án yêu cầu Codex triển khai trực tiếp ngày 28/09/2026. Không có Prompt ID/Antigravity handoff và không có claim Phase 05/07/08 hay user acceptance.
- HEAD base: `db34379f96d439ace6d504b60c31bc01cab9a902`; source/docs đang là current uncommitted workspace.
- WORKSPACE FINGERPRINT: d330136d7e842ac36decee5d7836c2985f03168099afe947c4eb663f6374c6f6
- Dữ liệu: chỉ fixture tổng hợp; không ghi audio, transcript, token, PII hay secret.

## Diff được quan sát

- `src/aicefr/api/student.py`: session-only student boundary, task-version gate, consent-backed submit port, file policy, status/report owner boundary và `COMPLETED` fail-closed nếu report M06 chưa có.
- `src/aicefr/api/wsgi.py`, `src/aicefr/api/templates.py`: form upload, status/report HTML và WSGI routes có body cap, owner boundary, CSRF origin check cho cookie mutation.
- `src/aicefr/contracts.py`, `src/aicefr/storage/service.py`, `src/aicefr/storage/sqlite.py`: typed response lifecycle, stable reason, optimistic transition và migration v2.
- `tests/api/test_student.py`, `tests/storage/test_sqlite_memory_migration.py`: M01 test mapping và fixture integration W2–W3.

## Checks đã chạy

| Check | Kết quả thực tế |
| --- | --- |
| Ruff trên API/report/review/storage/contracts và tests liên quan | exit 0, `All checks passed!` |
| `pytest -p no:cacheprovider -q tests/api tests/report tests/review tests/storage/test_sqlite_memory_migration.py` | exit 0, `28 passed in 2.15s` |
| `python -m compileall -q src tests` | exit 0 |
| `git diff --check` | exit 0; chỉ có cảnh báo line ending Git, không có whitespace error |

M01-TEST-001/002/003/004/005 được ánh xạ trong `tests/api/test_student.py`; có thêm test task đóng để xác nhận không ghi Response/blob. Storage test chạy ngoài sandbox cho kết quả `9 passed, 1 skipped`; skip là case symlink vì Windows host không có quyền tạo symlink (`WinError 1314`), không được tính là pass cho M01.

## UI/browser QA

WSGI/UI route được kiểm bằng fixture trong `tests/api/test_student.py`. Preflight browser ngày 28/09/2026 trả `playwright-unavailable`; vì vậy browser automation và ảnh trình duyệt là **NOT_RUN**, không có ảnh/evidence giả.

## Giới hạn và verdict

- `AllowlistedTaskAccess` là gate cấu hình cho vertical slice; task catalogue/ownership sản phẩm cần owner chốt.
- Không có M02–M05 pipeline với audio thật, không có đo lường CEFR và không claim E2E production.
- Self-review technical đã ghi tại `../reviews/review-log.md`; final verification và user verdict: **PENDING**.
