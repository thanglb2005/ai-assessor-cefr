# M02 — 05 Plan & Task Readiness

> **W2 v0.2 · 28/09/2026 · APPROVED by Thắng for implementation.** Phase 01, 03, 04 and 05 are approved. Sang review is still pending and must be disclosed before PR merge.

**Owner:** Thắng. **Module source scope:** `src/aicefr/audio/`, `src/aicefr/qc/`, M02 additions to `src/aicefr/contracts.py`, dependency pins in `pyproject.toml`, and listed tests only.

## Architecture and task order

1. **M02-TASK-001 / SCRUM-46:** decoder + PCM normalization + measurements. Add pinned SoundFile/SoXR, decode the approved formats from bounded authorized bytes, downmix mono/stereo, resample to float32 mono 16 kHz, and calculate deterministic measurements using explicit QCConfig.
2. **M02-TASK-002 / SCRUM-47:** QC policy + pipeline boundary. Consume Task 001 output; evaluate versioned policy config; only PASS dispatches to the injected ASR port. REVIEW stays pending owner review; REJECT never dispatches. Do not change `src/aicefr/asr/service.py` in this M02 scope.

Task 002 depends on Task 001. Overall proposed integration order across the four branches is SCRUM-46 → SCRUM-47 → SCRUM-48 → SCRUM-49, to serialize edits to `contracts.py` and `pyproject.toml`. Within M02, Task 002 depends on Task 001. Since both tasks touch shared integration points, finish/review Task 001 first, then rebase Task 002 to the latest `main` after SCRUM-46 merges before requesting its PR merge.

## Shared-contract review — pending after user-directed implementation

Sang (M03/M04 owner) still needs to review the additive `QCMeasurement`/`QCResult.measurements` fields, M02 reason codes, 16 kHz PCM invariant, and PASS-only dispatch boundary. M03 currently accepts REVIEW and drops QC metadata; M02 keeps that behavior out of automatic dispatch through its own pipeline boundary. Record owner feedback in the review log; do not edit M03 code as part of these Jira scopes.

## File scope by task

| Jira | Allowed files |
| --- | --- |
| SCRUM-46 / M02-TASK-001 | `pyproject.toml`; `src/aicefr/contracts.py` (M02 types only); `src/aicefr/audio/**`; `src/aicefr/qc/measurements.py`; `tests/audio/test_decoder.py`; `tests/qc/test_measurements.py`; M02 assertions in `tests/test_contracts.py` |
| SCRUM-47 / M02-TASK-002 | `src/aicefr/qc/policy.py`; `src/aicefr/audio/pipeline.py`; `tests/qc/test_policy.py`; `tests/audio/test_pipeline.py`; M02 assertions in `tests/test_contracts.py` only if approved contract implementation requires them |

Do not alter M03/M04 implementation or tests, unrelated contracts, model/assets, user audio, transcript, secrets, or generated data. No admin UI, HTTP routes, subprocess worker or hard timeout in W2.

## Required checks and evidence

- Commands approved in Phase 04: `python3 -m pytest -q -m "not smoke" tests/audio tests/qc`; coverage with `--cov=aicefr.audio --cov=aicefr.qc --cov-branch --cov-report=term-missing`; run `python3 -m pytest -q tests/test_contracts.py` for shared types.
- Gate: line ≥ 90% and branch ≥ 85% on pure M02 Python logic; all Test IDs mapped to assertions. No real-audio smoke test is in scope; use only generated fixtures.
- Record command, timestamp, exit code, pass/fail/skip, coverage, revision and workspace fingerprint in module `evidence/`. Run `ruff` only if configured and record exact result. Phase 07 review and Phase 08 verification must use final revision.
- Initial observed branch base was `55d8952`; verify the branch head and capture a fresh fingerprint before implementation. Issue one prompt per Jira task under Thắng’s explicit Phase 05 approval of 28/09/2026; disclose pending Sang review in each report and seek it before PR merge.

## Risks and Definition of Ready

- Native decoder/resampler run in process with bounded bytes/rate/channels/frames but no hard wall-clock timeout or process isolation; exceptions become safe REJECTs. This W2 limitation is approved and must remain explicit in code/review.
- Do not introduce production silence/clipping thresholds without calibration; test-only values must be passed explicitly in versioned QCConfig.
- **Phase 05 READY only when:** M03/M04 review is recorded; task file lists, dependencies, test commands and coverage match this plan; user approves this exact plan/task revision. Until then tasks are `DRAFT / NOT_STARTED`.

**CODEX CHECK RESULT:** READY FOR IMPLEMENTATION by explicit user verdict; Sang cross-module review is still PENDING.
