# M02-PROMPT-001 — SCRUM-46 / M02-TASK-001

| Field | Value |
| --- | --- |
| Executor | Codex, direct implementation requested by Thắng; Antigravity tool is not available in this session |
| Issued at | 28/09/2026 |
| Phase 05 verdict | APPROVED by Thắng on 28/09/2026: “duyệt đi, cứ done task đã rồi tính, gấp” |
| Cross-owner review | Sang (M03/M04) PENDING; disclose before PR merge |
| Base revision | 55d89524bce7b62d04835d73c723696976f773be |
| Base workspace fingerprint | 7cabc5bb6d1baeea109de9d4608749bb5f13ca605c220da4c37b67722732733c |
| Artifacts | M02 Requirement v0.2; Research v0.1; Specification v0.3; Test Plan v0.2; Plan/Tasks v0.2 |

## Objective and scope

Implement M02-TASK-001 on `feat/SCRUM-46-M02-TASK-001-Audio-decoder-QC-va-unit-tests` in this worktree. FR-001/002, AC-001/002, Test IDs M02-TEST-001–006. Decode authorized bytes for WAV PCM, FLAC, OGG/Vorbis, MP3 with SoundFile 0.14.0; downmix stereo by arithmetic mean, reject >2 channels; resample with SoXR 1.1.0 HQ to 1-D float32 mono 16 kHz. Compute raw SHA-256, duration/silence/clipped ratios and explicit versioned QCConfig. Resource limits are required config values; no production thresholds/defaults. Decode in process with bounded bytes/rate/channels/frames, without hard timeout. Return safe reason codes for invalid input and controlled errors.

Allowed files: `pyproject.toml`, M02 additions only in `src/aicefr/contracts.py`, `src/aicefr/audio/**`, `src/aicefr/qc/measurements.py`, `tests/audio/test_decoder.py`, `tests/qc/test_measurements.py`, M02 assertions in `tests/test_contracts.py`, this module's SDD prompt/evidence/review/status files. Do not edit M03/M04 code, model/assets, audio, transcripts, secrets or actual participant data.

## Required checks and report

Run Test IDs M02-TEST-001–006, full affected pytest suite and branch coverage on pure M02 logic (line ≥90%, branch ≥85%) using commands in 04-test-plan.md. Run `ruff` if configured. Record each command, timestamp, exit code, pass/fail/skip, line/branch coverage, base/head revision and final fingerprint in module `evidence/`. Review actual diff for contract compatibility, privacy, error handling and unintended scope. Do not mark Sang review complete; it remains pending before PR merge.
