# M06-EVID-DIRECT-20260928 — Direct implementation evidence

## Trạng thái và provenance

- Task: `M06-TASK-001`, `M06-TASK-002`, `M06-TASK-003`.
- Cách thực hiện: chủ dự án yêu cầu Codex triển khai trực tiếp ngày 28/09/2026. Không có Prompt ID/Antigravity handoff và không có claim Phase 05/07/08 hay user acceptance.
- HEAD base: `db34379f96d439ace6d504b60c31bc01cab9a902`; source/docs đang là current uncommitted workspace.
- WORKSPACE FINGERPRINT: d330136d7e842ac36decee5d7836c2985f03168099afe947c4eb663f6374c6f6
- Dữ liệu: chỉ fixture tổng hợp; không có report CEFR thực nghiệm hay dữ liệu cá nhân.

## Diff được quan sát

- `src/aicefr/report/contracts.py`, `src/aicefr/report/service.py`: `EvidenceRef` có source/version/response/time/word checks; evidence sai/thiếu chỉ tạo issue, không tạo comment khẳng định.
- `DiagnosticReport` có đúng một overall score/band nullable, năm hàng coverage canonical và `Interaction` insufficient evidence; không có năm criterion score/band.
- `ReportService.apply_review` yêu cầu `ReviewDecisionVerifier`; report chỉ có `teacher_verified=true` sau decision/audit được M07 repository xác minh.
- `src/aicefr/api/templates.py` trình bày provisional và teacher final riêng; `tests/report/test_report_service.py`, `tests/review/test_review_service.py` và fixture flow API kiểm chứng contract.

## Checks đã chạy

| Check | Kết quả thực tế |
| --- | --- |
| Ruff trên API/report/review/storage/contracts và tests liên quan | exit 0, `All checks passed!` |
| `pytest -p no:cacheprovider -q tests/api tests/report tests/review tests/storage/test_sqlite_memory_migration.py` | exit 0, `28 passed in 2.15s` |
| `python -m compileall -q src tests` | exit 0 |
| `git diff --check` | exit 0; chỉ có cảnh báo line ending Git, không có whitespace error |

Các test cover evidence missing/foreign/stale/out-of-range, comment valid, `NOT_EVALUATED`, one overall + five coverage rows, decision không có verifier bị từ chối và teacher action đã audit cập nhật report. Fixture flow `test_w3_fixture_flow_submits_then_exposes_teacher_verified_report` nối M01 → M06 → M07.

## Giới hạn và verdict

- Không có dữ liệu benchmark/coverage CEFR hoặc real model inference; fixture không phải kết quả đánh giá người học.
- Review M05/M07/M08 về mapping, persistence và nội dung wording còn PENDING.
- Self-review technical đã ghi tại `../reviews/review-log.md`; final verification và user verdict: **PENDING**.
