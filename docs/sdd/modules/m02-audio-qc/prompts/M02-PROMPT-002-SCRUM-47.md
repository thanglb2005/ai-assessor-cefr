# M02-PROMPT-002 — SCRUM-47 / M02-TASK-002

| Field | Value |
| --- | --- |
| Executor | Codex, direct implementation requested by Thắng; Antigravity tool unavailable in this session |
| Issued at | 28/09/2026 |
| Phase 05 verdict | APPROVED by Thắng: “duyệt đi, cứ done task đã rồi tính, gấp” |
| Cross-owner review | Sang (M03/M04) PENDING before PR merge |
| Base revision | 078d90f8fa1270969520ac21eda6c37d9ccfed41 |
| Base tree fingerprint | adb8a0c4776066c667b50e89041fdc46a266a63e7f03e18945cd23816c9c2361 |
| Artifacts | M02 Requirement v0.2; Research v0.1; Specification v0.3; Test Plan v0.2; Plan/Tasks v0.2 |

## Objective and scope

Implement M02-TASK-002 on `feat/SCRUM-47-M02-TASK-002-QC-policy-va-pipeline-boundary-tests`. FR-001/002, AC-001/002, Test IDs M02-TEST-007/008. Evaluate explicit versioned QC metrics and configured min duration, silence and clipping review/reject thresholds. Structural failures remain REJECT. Gate the injected ASR port so only PASS automatically dispatches; REVIEW stays pending owner decision and REJECT is blocked. Do not edit M03 AsrService.

Allowed files: `src/aicefr/qc/policy.py`, `src/aicefr/audio/pipeline.py`, `src/aicefr/audio/__init__.py`, `src/aicefr/qc/__init__.py`, `tests/qc/test_policy.py`, `tests/audio/test_pipeline.py`, this module's SDD prompt/evidence/review/status files. No audio, transcript, model, secret, actual participant data or product QC defaults.

## Required checks

Run Test IDs M02-TEST-007/008 and full non-smoke regression; line ≥90%, branch ≥85% on pure M02 logic across both tasks. Run Ruff and diff check. Record exact command, exit, pass/fail/skip, coverage, code revision and fingerprint. Review actual diff and report pending Sang shared-contract review honestly before recommending PR merge.
