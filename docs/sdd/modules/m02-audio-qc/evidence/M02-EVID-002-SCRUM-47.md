# M02-EVID-002 — SCRUM-47

- Executor: Codex direct implementation, per Thắng Phase 05 approval on 28/09/2026.
- Base revision: `078d90f8fa1270969520ac21eda6c37d9ccfed41` (SCRUM-46 complete).
- Base tree fingerprint: `adb8a0c4776066c667b50e89041fdc46a266a63e7f03e18945cd23816c9c2361`.
- Prompt: `M02-PROMPT-002-SCRUM-47.md`; Test IDs M02-TEST-007/008. Earlier Test IDs 001–006 rerun.
- Scope: explicit QC policy, PASS-only ASR pipeline gate and synthetic policy/ASR-spy tests.

| Check | Command | Exit | Result |
| --- | --- | --- | --- |
| M02 task tests + branch coverage | `PYTHONPATH=src /tmp/ai-assessor-cefr-m02-venv/bin/python -m pytest -q --cov=aicefr.audio --cov=aicefr.qc --cov-branch --cov-report=json:/tmp/m02-scrum47-coverage.json tests/audio tests/qc` | 0 | 21 passed, 0 skipped; statements 216/228 = 94.74%; branches 84/94 = 89.36% |
| Full non-smoke regression | `PYTHONPATH=src /tmp/ai-assessor-cefr-m02-venv/bin/python -m pytest -q -m 'not smoke'` | 0 | 144 passed, 10 skipped because `ridge_resp_v2.json` is absent from `$AICEFR_MODEL_DIR` |
| Lint | `/tmp/ai-assessor-cefr-m02-venv/bin/ruff check src/aicefr/audio src/aicefr/qc src/aicefr/contracts.py tests/audio tests/qc` | 0 | All checks passed |
| Diff hygiene | `git diff --check` | 0 | No whitespace error |

PASS dispatches once to the injected ASR port; REVIEW returns `awaiting_review=True` with no transcript; REJECT blocks dispatch. No scoring step exists in this boundary, so non-PASS cannot create a score here. Tests use synthesized PCM bytes and spy output only. No product thresholds, raw audio, transcript, model, secret or participant data committed. Sang shared-contract/boundary review remains pending before PR merge. Final code revision and fingerprint follow after commit.
