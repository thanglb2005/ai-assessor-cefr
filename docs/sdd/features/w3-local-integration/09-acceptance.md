# W3 — Acceptance package

PHASE RECORD ID: W3-09-ACCEPTANCE-A01
SCOPE ID/TYPE/ROOT: W3 / feature / docs/sdd/features/w3-local-integration/
SUBJECT: local integration, W3-TASK-001–008
BASE / PRODUCT SOURCE REVISION: 2b428ce → ffb325cc5ba8127f8c76a137a53e15a3dc0599b0
FINGERPRINT: dẫn tới snapshot và subtree IDs trong Final Verification
CODEX CHECK RESULT: PASS — technical evidence
CODEX RECOMMENDATION: RECOMMEND APPROVAL cho phạm vi W3 local integration
USER VERDICT: PENDING
VERIFIED/APPROVED BY: chưa có user verdict
USER VERDICT AT: chưa có

Thắng đã trực tiếp giao implementation/review/delegation như [Requirement](01-requirement.md); quyền đó không được diễn giải thành các verdict lịch sử APPROVED. Formal Phase 01/03/04/05/07/08/09 và task acceptance vẫn PENDING. Package này chuẩn bị cho review, không nghiệm thu thay user hoặc nghiệm thu M01–M08 toàn bộ.

| AC | Hành vi được kiểm chứng | Evidence |
| --- | --- | --- |
| AC-001 | Auth/consent submission→QC/ASR/features/scoring/report; refusal/failure giữ reasons, null overall; non-PASS QC không ASR | tests/pipeline; 265-pass regression; actual WAV COMPLETE/ESTIMATED, grounded report |
| AC-002 | Report/status/session/review tồn tại qua reopen; candidate/decision/report/audit rollback cùng transaction; teacher result riêng | tests/pipeline/test_coordinator.py, tests/report/test_sqlite_report.py, factory integration; browser override; actual restart/logout |
| AC-003 | Local CLI/UI, student ownership, current consent/withdraw/logout; teacher claim/report/authorized audio/override; mobile document | HTTP/factory tests; independent desktop/mobile Chromium journey và 4 ảnh |
| AC-004 | Offline lazy ASR/VAD, bytes/hash provenance, missing prerequisites refuse; actual model smoke | adapter mock boundaries; pinned external Whisper/Ridge; real WAV/Silero log |
| AC-005 | CI config/README/local guide; exact prompt files + Excel; review/final logs theo revision | Ruff/guards/build/compile PASS; AI log audit; Prompt Log; final manifest |

Evidence cuối và commands: [Final Verification](08-final-verification.md). Review/corrections: [Review](reviews/review-01.md). Hướng dẫn thử sản phẩm: [Local run guide](../../../local-run.md).

Giới hạn cần đọc trước verdict: model/calibration/WER/CEFR accuracy chưa đo; local fixture demo không được xem là vận hành dữ liệu người học thật. MP3 sample có native decoder warnings, đã giữ log. Uncovered branches và phạm vi scan secrets được ghi trong Final Verification; chưa được user xác nhận risk acceptance. Remote CI/deploy chưa chạy. Không push/deploy từ lượt này.

Next action: Thắng xem evidence và ghi verdict cho scope W3. Không có mandatory code finding hoặc required technical check đang mở.
