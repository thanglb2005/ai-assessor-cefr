# M03 — Review Records

**Hiện trạng:** Phase 07 attempt A1 **APPROVED** 26/09/2026 (Sang).

| Review ID | Prompt ID / Task ID | Base/Head revision | Diff/evidence đã kiểm tra | Finding và resolution | User verdict |
| --- | --- | --- | --- | --- | --- |
| 07-M03-A1 | M03-TASK-003, 004, 001 (SCRUM-18, 19, 20); Claude implement theo yêu cầu chủ dự án (không qua prompt Antigravity) | base `main` `ecb835f` → correction PR `[Phase 07]` | toàn bộ `src/aicefr/asr/*, tests/asr/*`; evidence module; chạy lại test/lint | FINDING-07-A1-01, FINDING-07-A1-02, FINDING-07-A1-03, FINDING-07-A1-07 — xem dưới | APPROVED 26/09/2026 (Sang) |

## Review Record 07-M03-A1

```text
REVIEW ID: 07-M03-A1
TASK/PROMPT ID: M03-TASK-003, 004, 001 (SCRUM-18, 19, 20)
BASE/HEAD/FINGERPRINT: base main ecb835f (PR #7 e92c1cf, PR #8 ecb835f); không có fingerprint sdd-workspace-v2
  vì chủ dự án cho Claude implement trực tiếp, không phát prompt Antigravity — diff kiểm được qua Git
REVIEWED SCOPE/FILES: src/aicefr/asr/*, tests/asr/*
CHECKLIST RESULT: scope/traceability PASS; design PASS; functionality PASS sau correction (còn MINOR follow-up);
  simplicity PASS; responsibility/coupling PASS; duplication/dead code PASS; naming PASS;
  comments/docs MINOR (README, FINDING-05); style PASS (ruff); error/security PASS (log không lộ transcript/vector,
  artifact chỉ JSON có hash ghim); tests PASS (hành vi, biên, regression) sau FINDING-01
FINDINGS: FINDING-07-A1-01 MAJOR RESOLVED, FINDING-07-A1-02 MINOR RESOLVED, FINDING-07-A1-03 MINOR RESOLVED 03/10/2026 (SCRUM-50), FINDING-07-A1-07 NIT RESOLVED
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
FINDING ID: FINDING-07-A1-02
SEVERITY: MINOR
CATEGORY: Functionality
LOCATION: src/aicefr/asr/identity.py `asr_version_reasons`
OBSERVED EVIDENCE: Weight không có trong bảng ánh xạ + `trained_asr_model=None` → `asr_model=None`, reasons rỗng. Spec M03: weight không có trong bảng → null + `ASR_VERSION_MISMATCH`.
RISK/FAILED AC: Lệch M03-FR-003 ở trường hợp biên.
REQUIRED CHANGE: `asr_model is None` luôn trả `ASR_VERSION_MISMATCH`.
STATUS: RESOLVED
RESOLUTION EVIDENCE: Test `test_unmapped_weight_is_mismatch_even_without_trained_model`.
```
```text
FINDING ID: FINDING-07-A1-03
SEVERITY: MINOR
CATEGORY: Functionality
LOCATION: asr/service.py (QC REJECT) → scoring/scorer.py bước 3
OBSERVED EVIDENCE: QC `REJECT` → Transcript `NOT_RUN`, reasons rỗng → Assessment `NOT_EVALUATED` không kèm reason nào.
RISK/FAILED AC: M06 không có lý do để hiển thị. Spec M03 chưa định reason cho nhánh này; mã lỗi QC thuộc M02.
REQUIRED CHANGE: Follow-up: owner M02 (Thắng) công bố reason code QC trong contract, M03 chép sang Transcript.
STATUS: RESOLVED 03/10/2026 — ban đầu ACCEPTED_RISK (26/09/2026); M02 đã công bố mã `QC_*` trong contract, M03 chép `QCResult.reasons` sang Transcript (SCRUM-50)
RESOLUTION EVIDENCE: M03-EV-003 (`asr/service.py`, M03-TEST-005 mở rộng); chờ owner review lại trong PR
```
```text
FINDING ID: FINDING-07-A1-07
SEVERITY: NIT
CATEGORY: Clean Code
LOCATION: src/aicefr/asr/hallucination.py `_token_share`
OBSERVED EVIDENCE: `max(set(tokens), key=tokens.count)` là O(n²).
RISK/FAILED AC: —
REQUIRED CHANGE: Dùng `Counter.most_common`.
STATUS: RESOLVED
RESOLUTION EVIDENCE: M03-TEST-009 vẫn pass.
```

## Khác Test Plan — chủ dự án đã chấp nhận (26/09/2026)

- D1: luật "cụm 3–10 từ lặp ≥ 3 lần" hiện thực là lặp **liền nhau** (lặp rời rạc sẽ gắn cờ nhầm lời nói bình thường).

Codex lưu Phase 07 review record tại đây sau khi kiểm tra actual diff, test và evidence. Chỉ người dùng ghi verdict phê duyệt.
