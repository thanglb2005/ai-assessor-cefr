# W3 — Test Plan

Version v0.1. UT REQUIRED: YES — pipeline/state/auth/storage/adapter behavior.

| Test ID | AC | Scenarios |
| --- | --- | --- |
| W3-TEST-001 | AC-001 | Generated valid audio through real QC and injected engine/extractor/scorer; report availability and lifecycle |
| W3-TEST-002 | AC-001 | QC corrupt/reject/review; spies prove no ASR on non-PASS; no fabricated score |
| W3-TEST-003 | AC-001/004 | ASR/model/VAD failure, missing features, mismatch/OOD; safe reasons/null overall; privacy logs |
| W3-TEST-004 | AC-002 | Restart restores reports/review; same-connection decision/report rollback; optimistic revision/duplicate dispatch |
| W3-TEST-005 | AC-003 | Login/logout/consent, student owner/foreign denial, teacher permissions/audio, input/CSRF boundaries |
| W3-TEST-006 | AC-004 | Lazy/offline ASR/VAD adapters with mocked imports; actual local smoke only with allowed model/audio |
| W3-TEST-007 | AC-003 | Playwright generated-fixture browser journey: login→consent→upload→report→teacher override; desktop/mobile; screenshot/console/network evidence |
| W3-TEST-008 | AC-005 | Full regression, Ruff, Markdown links, forbidden-file guard, compile/package and CI config |

## Commands

Use /tmp/aicefr-w3-venv/bin/python and /tmp/aicefr-w3-venv/bin/ruff. Base env installed existing .[dev]; Playwright/openpyxl are QA/log utilities only. Default tests deterministic/offline, no large model. Regression: python -m pytest -q -m 'not smoke'. Coverage: python -m pytest -q -m 'not smoke' --cov=aicefr --cov-branch --cov-report=term-missing --cov-report=json:/tmp/aicefr-w3-coverage.json. Ruff: ruff check src tests scripts. Guards: python scripts/ci/check_md_links.py; python scripts/ci/check_forbidden_files.py. Diff: git diff --check.

Measure line+branch on changed critical code and analyze uncovered paths; M02/M08 retain ≥90% line/≥85% branch approved policy. Do not invent a global threshold or exclusions. Optional actual ASR smoke records NOT_RUN if prerequisites absent, not PASS from mocks. Final rerun after corrections on final source revision; USER VERDICT PENDING.
