# M05 — Review Records

**Hiện trạng:** Phase 07 attempt A1 **APPROVED** 26/09/2026; attempt A2 (M05-TASK-004) **APPROVED** 03/10/2026 (Sang).

| Review ID | Prompt ID / Task ID | Base/Head revision | Diff/evidence đã kiểm tra | Finding và resolution | User verdict |
| --- | --- | --- | --- | --- | --- |
| 07-M05-A1 | M05-TASK-002, 001 (SCRUM-27, 28); Claude implement theo yêu cầu chủ dự án (không qua prompt Antigravity) | base `main` `ecb835f` → correction PR `[Phase 07]` | toàn bộ `src/aicefr/scoring/*, phần M05 của contracts.py, tests/scoring/*`; evidence module; chạy lại test/lint | FINDING-07-A1-01, FINDING-07-A1-03, FINDING-07-A1-06 — xem dưới | APPROVED 26/09/2026 (Sang) |
| 07-M05-A2 | M05-TASK-004 (SCRUM-29); Claude implement theo yêu cầu chủ dự án | base `main` `2b428ce` → PR #25 → `ae72d57` | `tests/scoring/test_integration_features.py`, Test Plan v0.2.1; chạy lại test/lint | Không có finding; khác Test Plan v0.2.1 — xem dưới | APPROVED 03/10/2026 (Sang) |

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
STATUS: ACCEPTED_RISK — chủ dự án chấp nhận để làm follow-up (26/09/2026)
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

## Khác Test Plan — chủ dự án đã chấp nhận (26/09/2026)

- Không có khác biệt so với Test Plan. Contract thêm `Assessment.out_of_range` (phần M05) để trả chi tiết OOD theo Spec bước 6.

Codex lưu Phase 07 review record tại đây sau khi kiểm tra actual diff, test và evidence. Chỉ người dùng ghi verdict phê duyệt.

## Review Record 07-M05-A2

```text
REVIEW ID: 07-M05-A2
TASK/PROMPT ID: M05-TASK-004 (SCRUM-29); Claude implement theo yêu cầu chủ dự án (không qua prompt Antigravity)
BASE/HEAD/FINGERPRINT: base main 2b428ce → PR #25 (merge 7b32672) → main ae72d57 (ae72d57b03de0ae9333e8b549484d026feb3177c); fingerprint sdd-workspace-v2 8835acf872d8c0abd3cc94e897723bc7a9c05fe3956400ee0b6bf577d7ab8af7
REVIEWED SCOPE/FILES: tests/scoring/test_integration_features.py; Test Plan M05 v0.2.1 (dòng 022);
  status/plan/tasks/evidence M05; đọc lại diff 2b428ce..ae72d57 phần M03–M05
CHECKLIST RESULT: scope/traceability PASS (chỉ tests/scoring + docs M05, không đổi src/); design PASS;
  functionality PASS (ART-REAL: chỉ log_uniq lệch → NOT_EVALUATED + OUT_OF_DISTRIBUTION; CI: hợp đồng
  tên/thứ tự/provenance, VAD lệch → VAD_VERSION_MISMATCH); simplicity PASS; duplication PASS (dùng lại
  fixture M04 và write_fake); naming PASS; style PASS (ruff); security/license PASS (ngưỡng đọc từ artifact,
  không ghi số suy ra từ S&I vào test hay Test Plan); tests PASS
FINDINGS: không có BLOCKER/MAJOR/MINOR. Khác Test Plan: v0.2.1 thêm hai biến thể ART-FAKE cho M05-TEST-022
CHECKS RERUN: `env -u AICEFR_MODEL_DIR pytest -q -m "not smoke"` → 192 passed, 11 skipped;
  `AICEFR_MODEL_DIR=… pytest -q -m "not smoke" --cov=aicefr --cov-branch` → 203 passed; `aicefr.scoring` 100 %;
  `ruff check .` sạch; CI run 37113044170 trên ae72d57, Python 3.11: 192 passed, 11 skipped
REVIEWER: Claude — cùng tác nhân đã implement, nên verdict do chủ dự án quyết; PR #25 không có lượt approve
  của thành viên khác trên GitHub
RESULT: PASS
EVIDENCE: evidence/evidence-manifest.md (M05-EV-003, M05-EV-P08-A2)
```

**Khác Test Plan — chủ dự án đã chấp nhận (03/10/2026):** Test Plan v0.2.1 thêm hai biến thể ART-FAKE chạy trên CI cho M05-TEST-022 (hợp đồng tên/thứ tự/provenance; VAD lệch) và đọc `accepted_low` từ artifact thay vì ghi số. Không đổi FR/AC.
