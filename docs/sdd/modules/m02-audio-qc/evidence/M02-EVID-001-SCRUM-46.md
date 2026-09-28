# M02-EVID-001 — SCRUM-46

- Executor: Codex direct implementation, per Thắng Phase 05 approval on 28/09/2026.
- Base revision: `55d89524bce7b62d04835d73c723696976f773be`.
- Prompt: `M02-PROMPT-001-SCRUM-46.md`; Test IDs M02-TEST-001–006.
- Scope: SoundFile/SoXR decoder, explicit QCConfig, shared M02 contracts, synthetic tests.
- Runtime: Python 3.12.3; SoundFile 0.14.0 with libsndfile 1.2.2, SoXR 1.1.0.

| Check | Command | Exit | Result |
| --- | --- | --- | --- |
| Module tests + branch coverage | `/tmp/ai-assessor-cefr-m02-venv/bin/python -m pytest -q --cov=aicefr.audio --cov=aicefr.qc --cov-branch --cov-report=json:/tmp/m02-scrum46-coverage.json tests/audio tests/qc` | 0 | 14 passed, 0 skipped; statements 153/165 = 92.73%; branches 58/68 = 85.29% |
| Full non-smoke regression | `/tmp/ai-assessor-cefr-m02-venv/bin/python -m pytest -q -m 'not smoke'` | 0 | 137 passed, 10 skipped because `ridge_resp_v2.json` is absent from `$AICEFR_MODEL_DIR` |
| Lint | `/tmp/ai-assessor-cefr-m02-venv/bin/ruff check src/aicefr/audio src/aicefr/qc src/aicefr/contracts.py tests/audio tests/qc` | 0 | All checks passed |
| Diff hygiene | `git diff --check` | 0 | No whitespace error |

Test bytes are synthesized at runtime; no audio payload, transcript, model, secret or participant data committed. WAV PCM, FLAC, OGG/Vorbis and MP3 encoder/decoder paths were exercised; each assertion passed. Decoder executes in process within configured byte/rate/channel/frame caps; hard wall-clock timeout remains outside approved W2 scope. Product QC thresholds were not set. Sang shared-contract review remains pending before PR merge.

Code revision: `a6da59ab3868d2ffe6584b597d4153a964bfe2e1`. Source fingerprint (`git ls-tree -r HEAD` over M02 source, shared contract, dependency and task tests, then SHA-256): `d9963b0b9a449eb009014d9d5c41bc84847025f0463a6a93e352afa2c409a936`. Coverage JSON was written to `/tmp` and its exact totals are reproduced above. Final verification on this code revision uses the checks above; this evidence-only commit does not change code.
