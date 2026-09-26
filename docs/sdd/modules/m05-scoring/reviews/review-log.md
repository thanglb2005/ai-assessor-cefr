# M05 — Review Records

**Hiện trạng:** Phase 07 attempt A1 xong, chờ user verdict.

| Review ID | Prompt ID / Task ID | Base/Head revision | Diff/evidence đã kiểm tra | Finding và resolution | User verdict |
| --- | --- | --- | --- | --- | --- |
| 07-M05-A1 | M05-TASK-002, 001 (SCRUM-27, 28); Claude implement theo yêu cầu chủ dự án (không qua prompt Antigravity) | base `main` `ecb835f` → correction PR `[Phase 07]` | toàn bộ `src/aicefr/scoring/*, phần M05 của contracts.py, tests/scoring/*`; evidence module; chạy lại test/lint | FINDING-07-A1-01, FINDING-07-A1-03, FINDING-07-A1-06 — xem dưới | PENDING |

## Review Record 07-M05-A1

```text
REVIEW ID: 07-M05-A1
TASK/PROMPT ID: M05-TASK-002, 001 (SCRUM-27, 28)
BASE/HEAD/FINGERPRINT: base main ecb835f (PR #7 e92c1cf, PR #8 ecb835f); không có fingerprint sdd-workspace-v2
  vì chủ dự án cho Claude implement trực tiếp, không phát prompt Antigravity — diff kiểm được qua Git
REVIEWED SCOPE/FILES: src/aicefr/scoring/*, phần M05 của contracts.py, tests/scoring/*
CHECKLIST RESULT: scope/traceability PASS; design PASS; functionality PASS sau correction (còn MINOR follow-up);
  simplicity PASS; responsibility/coupling PASS; duplication/dead code PASS; naming PASS;
  comments/docs MINOR (README, FINDING-05); style PASS (ruff); error/security PASS (log không lộ transcript/vector,
  artifact chỉ JSON có hash ghim); tests PASS (hành vi, biên, regression) sau FINDING-01
FINDINGS: FINDING-07-A1-01 MAJOR RESOLVED, FINDING-07-A1-03 MINOR OPEN, FINDING-07-A1-06 NIT RESOLVED
CHECKS RERUN BY CODEX: `pytest -q -m "not smoke"` → 123 passed, 10 skipped;
  `AICEFR_MODEL_DIR=… python -m pytest -q -m "not smoke" --cov=aicefr --cov-branch` → 133 passed, 99 %;
  `ruff check src tests`, `ruff format --check src tests` sạch
RESULT: PASS — không còn BLOCKER/MAJOR mở; MINOR còn mở là follow-up ngoài phạm vi task
EVIDENCE: evidence/evidence-manifest.md; PR sửa `[Phase 07] fix …`
```

## Findings

```text
FINDING ID: FINDING-07-A1-01
SEVERITY: MAJOR
CATEGORY: Test
LOCATION: pyproject.toml [tool.pytest.ini_options]
OBSERVED EVIDENCE: Chạy `pytest` trơn: 4 lỗi thu thập, `ModuleNotFoundError: No module named 'tests'` (test import `tests.features.fixtures`, `tests.asr.fixtures`); chỉ `python -m pytest` chạy được.
RISK/FAILED AC: Người khác trong nhóm (hoặc Antigravity) chạy `pytest` sẽ thấy lỗi dù code đúng.
REQUIRED CHANGE: Thêm `pythonpath = ["."]`.
STATUS: RESOLVED
RESOLUTION EVIDENCE: `pytest -q -m "not smoke"`: 123 passed, 10 skipped.
```
```text
FINDING ID: FINDING-07-A1-03
SEVERITY: MINOR
CATEGORY: Functionality
LOCATION: asr/service.py (QC REJECT) → scoring/scorer.py bước 3
OBSERVED EVIDENCE: QC `REJECT` → Transcript `NOT_RUN`, reasons rỗng → Assessment `NOT_EVALUATED` không kèm reason nào.
RISK/FAILED AC: M06 không có lý do để hiển thị. Spec M03 chưa định reason cho nhánh này; mã lỗi QC thuộc M02.
REQUIRED CHANGE: Follow-up: owner M02 (Thắng) công bố reason code QC trong contract, M03 chép sang Transcript.
STATUS: OPEN — follow-up, không chặn nghiệm thu
RESOLUTION EVIDENCE: —
```
```text
FINDING ID: FINDING-07-A1-06
SEVERITY: NIT
CATEGORY: Clean Code
LOCATION: src/aicefr/scoring/scorer.py `_evaluate`
OBSERVED EVIDENCE: `assert` trên đường chạy thật (bị bỏ khi chạy `python -O`).
RISK/FAILED AC: —
REQUIRED CHANGE: Thay bằng nhánh rõ ràng.
STATUS: RESOLVED
RESOLUTION EVIDENCE: Test scorer vẫn pass.
```

## Khác Test Plan — cần chủ dự án chấp nhận khi ghi verdict

- Không có khác biệt so với Test Plan. Contract thêm `Assessment.out_of_range` (phần M05) để trả chi tiết OOD theo Spec bước 6.

Codex lưu Phase 07 review record tại đây sau khi kiểm tra actual diff, test và evidence. Chỉ người dùng ghi verdict phê duyệt.
