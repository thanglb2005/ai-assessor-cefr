# W3 local browser QA — FIX-01

**Date:** 02/10/2026 Asia/Ho_Chi_Minh. **Worktree:** `/tmp/aicefr-w3-app-review`, branch `feat/W3-app-review`, tested source HEAD `b6063dd` plus app correction commit `a750639`. **Result:** PASS.

Re-run from the worktree root (Chromium is expected under `/tmp/aicefr-w3-browsers`):

```bash
PLAYWRIGHT_BROWSERS_PATH=/tmp/aicefr-w3-browsers \
AICEFR_MODEL_DIR=/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src/aicefr/scoring/models \
PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python scripts/qa/w3_app_browser.py \
  --evidence-dir docs/sdd/features/w3-local-integration/evidence
```

The harness provisions random fixture passwords through the CLI's stdin interface, launches the app subprocess on `127.0.0.1`, and creates a synthetic two-second WAV with 70% silence in a temporary directory. It uses the pinned Ridge artifact by path; it does not copy the model or persist generated audio. The server is stopped in `finally`; only screenshot PNGs and summary/hash evidence remain in the repository.

The real Chromium journey used student and teacher contexts. It covered login, current consent, upload, review-required status and report, teacher queue/claim/detail/audio (WAV MIME and bytes hash checked), teacher B1 override and refreshed student report with separate unchanged AI null result, consent withdrawal and rejected second submission, and logout/session revocation. A student role denial returned 403; a foreign student's report returned 404; stale consent submission returned 403; a revoked session returned 403. One response remained after withdrawal. Desktop was 1280x800 and mobile was 390x844; all 11 DOM/viewport checks passed. Form controls were keyboard-focused and verified with `:focus-visible` in Chromium.

Observed HTTP statuses: 200, 303, 403, 404. Browser console errors: 0; failed requests: 0; external requests attempted: 0. The denied/stale/revoked cases were made through Playwright's API request context so expected 403/404 documents did not create browser console errors. Request bodies and raw audio were compared/used in memory only and were not logged.

The generated QC REVIEW fixture intentionally bypasses ASR/VAD model execution: this browser QA is **not** an ASR/VAD inference measurement and makes no WER or CEFR accuracy claim.

| Screenshot | SHA-256 |
| --- | --- |
| `browser-qa-desktop-student-report.png` | `5c34409b7ad872eee257da8624e0e87e544ddb6a7d05ab23497bd5a39a1a2411` |
| `browser-qa-desktop-teacher-review.png` | `6b305a3a5cc0c9a0c1e291d42d0b75eb2e8c57925650244a03dfe3acba02e07c` |
| `browser-qa-mobile-student-upload.png` | `6fbf017044d5a18fbec3d629b9359f5eaeb1e10c3c9ed00917c2c3ac4038a49d` |
| `browser-qa-mobile-teacher-detail.png` | `e87650491f2e2889cee9731d76e8205002c18169c453dcf64670f579a658d795` |
