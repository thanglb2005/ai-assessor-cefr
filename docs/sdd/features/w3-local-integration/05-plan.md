# W3 — Plan & Task Readiness

Version v0.1 · direct user instruction authorizes Luna implementation and Codex review. Standard artifact checkpoints are not retroactively APPROVED.

## Isolation

Integration branch: feat/W3-local-integration. Three independent Git worktrees under /tmp/aicefr-w3-{pipeline,app,speech}, each with its own task branch. Agents commit only allowed files; root inspects diff and cherry-picks locally. No push/deploy. Scope IDs W3-TASK-* are local, not invented Jira keys.

## Lanes and dependencies

1. Pipeline/persistence: coordinator + durable report/review atomicity + M01 fresh status. Own pipeline, report repo/service protocol, storage migrations, student service and focused tests.
2. Local application: login/logout/consent, CLI composition, accessible UI and teacher/audio navigation. Own local package, auth service additions, api WSGI/templates and app tests. Imports agreed public contracts; wait for pipeline/speech at integration.
3. Speech/quality: offline optional adapters, scoring artifact finite/shape validation, exception log privacy, tests, CI and model provenance/error analysis docs. Own asr/features adapter and log fixes, scoring, CI and corresponding tests; no shared contracts.
4. Reuse app agent for browser QA after integration; save prompt first. Any correction uses root-issued stored prompt and narrow allowed files.

## Quality and evidence

Raw reports per lane under evidence/; include base/head, tests/exit, skipped, coverage, file list, source references and limitations. Root owns SDD, AI Prompt Log.xlsx and review records. Agent evidence is input, not approval. Review every human-written change and rerun required checks; update context/roadmap only with actual evidence. Frozen W2 specs remain unchanged. Retention/real-data governance and unavailable actual ASR smoke remain explicitly pending.

