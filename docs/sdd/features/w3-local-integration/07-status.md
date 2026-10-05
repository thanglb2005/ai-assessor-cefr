# W3 — Status

SCOPE ID/TYPE/ROOT: W3 / feature / docs/sdd/features/w3-local-integration/
Current phase: 07/08 technical review và verification đã hoàn tất; package 09 đã chuẩn bị, user verdict PENDING.
Operating mode: Standard artifacts + direct user override cho Luna implementation và Codex review.
Base source revision: 2b428ceea9e4459f3235d4ce67f10bab31585ebf
W3 source revision measured by final regression: ffb325cc5ba8127f8c76a137a53e15a3dc0599b0
Last evidence HEAD before final documentation: 6ae8b4060f0fa189d7f9a18dbe63c41c214c412e
Latest upstream main checked: 8032e55d911745e9cd4267f6a9c5dcae8d24b440 (13 commits ahead of W3 base)
Integration branch: feat/W3-local-integration
Specification/Test Plan/Plan versions: v0.1; Tasks cập nhật implementation thực tế.
User-modified files on entry: none.
Research: RUN — source/contracts và API chính thức của local adapters đã đối chiếu.
Implementation authority: latest user request trong 01-requirement; permits writing Luna subagents, local branch/commits, setup/tests và corrections.
Phase 01/03/04/05/07/08/09 formal verdicts: PENDING; không ghi APPROVED thay Thắng.
Current tasks: W3-TASK-001–008 IMPLEMENTED. Regression evidence PASS at measured W3 revision above; full tests have not been rerun after syncing latest main. Task acceptance PENDING.
CODEX CHECK RESULT: PASS at measured W3 revision; current merge-head regression pending.
CODEX RECOMMENDATION: RECOMMEND APPROVAL after merge-head CI passes.
USER VERDICT: PENDING
WORKSPACE FINGERPRINT: ac30965ba60e1e27d1c57a1504e971c2caf07a4e83facaf5151feb66824f3e3c

Fingerprint dùng `sdd-workspace-v2` cho snapshot hồ sơ cuối trước commit, HEAD `6ae8b40`; metadata files là Status và Final Verification, không thêm exclusions. Đây là snapshot trước commit docs, không phải fingerprint của HEAD sau commit. [Final Verification](08-final-verification.md) ghi source/test/script/workflow subtree IDs để kiểm chứng source không đổi sau các commit evidence/docs.

Baseline: 189 passed/10 skipped không có model path; 199 passed/0 skipped với pinned Ridge. Final regression: **265 passed/0 skipped/0 failed** với artifact; **254 passed/11 skipped/0 failed** không có artifact path. M02: 94.74% line/89.36% branch; M08: 97.27% line/88.71% branch, đạt policy 90/85. Global 91.58% line/78.67% branch là số đo, không tạo global gate mới.

Browser: Codex rerun Chromium desktop/mobile, 11 DOM/viewport checks PASS, không console error/failed/external request; có ảnh và hashes. Real smoke: local WAV qua factory→QC→Whisper→Silero→Ridge→SQLite report COMPLETED/ESTIMATED, 151 grounded comments/0 invalid evidence; restart/session/logout PASS. MP3 adapter sample có native decoder warnings; giữ limitation tại evidence, không nhận là clean MP3 run. WER/CEFR accuracy/calibration chưa đo.

Prompt/evidence/review: [Prompt Log](prompts/prompt-log.md), [Evidence Manifest](evidence/evidence-manifest.md), [Review](reviews/review-01.md), [Final Verification](08-final-verification.md), [Acceptance](09-acceptance.md).
Data boundary: fixture accounts/generated browser audio; actual local smoke dùng audio được Thắng xác nhận có quyền. Không commit raw audio/model/session/database; không push/deploy. Remote CI NOT_RUN; real learner governance và học thuật nằm ngoài scope local integration.
05/10 sync review: `origin/main` merged locally. Three-way merge found one conflict in `docs/evidence/tc2-3-ai-usage/README.md`, resolved by retaining both the Sang W1–W3 log and W3 prompt/review links. `src/aicefr/asr/service.py` merged without conflict; main's QC-reason propagation is preserved alongside W3's safe exception logging. Main's corresponding ASR/scoring tests are included. No full regression rerun at the merged head in this environment.
Next action: push and create the PR when GitHub authentication is restored; review its CI result before user acceptance.
Last updated: 05/10/2026 Asia/Ho_Chi_Minh.
