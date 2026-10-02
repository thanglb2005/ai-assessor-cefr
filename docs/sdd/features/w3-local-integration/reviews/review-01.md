# W3 — Implementation Review, cycle 01

PHASE RECORD ID: W3-07-A01 (initial) → W3-07-A02 (correction re-review)
Reviewer: Codex lead. Date: 02/10/2026.
Base: 2b428ce; initial integration 80c6707; final product source ffb325cc5ba8127f8c76a137a53e15a3dc0599b0.
Fingerprint: [Final Verification](../08-final-verification.md), snapshot trước final docs commit và stable product subtree IDs.
CODEX CHECK RESULT: PASS
CODEX RECOMMENDATION: RECOMMEND APPROVAL
USER VERDICT: PENDING

Codex đọc actual source/test/CI/harness changes và affected contracts, đối chiếu raw reports, tự chạy final regression/coverage, actual browser và real runtime smoke. Không dùng raw agent report làm final acceptance. Initial 236-pass run tại 80c6707 là intermediate; final evidence là 265-pass run sau đủ corrections.

| Finding | Severity | Vấn đề ban đầu và correction đã re-review | Trạng thái cuối |
| --- | --- | --- | --- |
| W3-RV-001 | MAJOR | ASR yêu cầu file preprocessor_config không tồn tại trong pin M03; af5dc8a sửa required set về đúng 4 files | RESOLVED — pin tests và actual local model load PASS |
| W3-RV-002 | MAJOR | Nhãn small chưa gắn bytes/hash; af5dc8a kiểm SHA256 cả 4 files, không canonical alias cho weights khác | RESOLVED — hash mismatch/cache tests và actual hashes/decode PASS |
| W3-RV-003 | MAJOR | Missing-Silero test phụ thuộc package có cài hay không; af5dc8a mock import/version boundary | RESOLVED — final suite có Silero thật cài đặt vẫn PASS, không skip test |
| W3-RV-004 | MAJOR | Chưa chứng minh shared SQLite rollback cho report/candidate/decision; 5056d05 bổ sung actual-service integration/failure tests | RESOLVED — final tests cover rollback, restart, stale/forged/duplicate CAS |
| W3-RV-005 | MAJOR | Unexpected failure bị gắn ASR_FAILED và scorer refusal che ASR reason; 5056d05 giữ reasons/null overall, controlled pipeline failure và recovery CAS | RESOLVED — refusal/failure/race/QC fallback tests PASS |
| W3-RV-006 | MAJOR | Coordinator ports/type hints/transaction ownership chưa rõ; 5056d05 explicit typed dependencies và same-connection unit of work | RESOLVED — actual source/transaction boundaries review + integration PASS |
| W3-RV-007 | MAJOR | Logout cần delete_session nhưng repo chính chưa có; a750639 bổ sung digest-only idempotent delete ở memory/SQLite | RESOLVED — memory/SQLite auth tests, browser revoked token và real reopen/logout PASS |
| W3-RV-008 | MAJOR | HTTP submit có thể dùng old consent sau config version tăng; a750639 enforce configured current consent trước persistence/enqueue | RESOLVED — stale/missing/withdrawn tests và browser withdrawal PASS |
| W3-RV-009 | MAJOR | Factory/browser chưa kiểm trên integrated services; a750639 thêm real SQLite factory tests và reusable actual Chromium harness | RESOLVED — Codex rerun 265 tests + desktop/mobile browser + actual pipeline PASS |
| W3-RV-010 | MINOR | Teacher detail nhúng full HTML document; thiếu viewport/demo note ở vài pages; a750639 sửa valid-document templates/local styles/fixture notes | RESOLVED — 11 DOM/viewport checks và Codex xem đủ 4 ảnh |

Correction source commits của agents: speech `af5dc8a1e72f01be45e66ef39e1d56afa3058a2f`, pipeline `5056d05dfb767e8756ddf47de5c7e096800d5ba9`, app `a7506393c9d023b2c695b48822d807f2ddd0e04c`. Root integration lần lượt tại `98e70da`, `d1f10ae`, `ffb325c`; raw evidence giữ commit/worktree/history từng lane. Prompt/amendment/correction/QA notes đều [lưu trước dispatch](../prompts/prompt-log.md).

## Clean Code và test review

Typed coordinator/ports, lazy adapters và factory giữ domain boundaries; optional packages/weights không download trong runtime; default inference không fake. Shared transaction ownership, CAS/revision và rollback được review cùng tests dùng SQLite services thật. Test mocks ở external import/engine boundaries, failure assertions kiểm trạng thái/report/reasons/audit; generated audio giữ offline determinism. Không training/band-map/contract cleanup ngoài scope. ASR/VAD exception handling không ghi input/exception text/stacktrace có thể chứa dữ liệu riêng; artifact finite/shape/hash checks fail closed. Auth/session/current consent, owner/teacher routes, path confinement và authorized audio được kiểm bằng tests/browser.

Templates có labels/viewport/focus/44px targets, fixture warnings và single-document HTML; Codex nhìn actual desktop/mobile screenshots. CI install không có fallback che failure; local required checks pass, chưa claim remote Actions run. Đọc reviewer browser harness process cleanup/network observer/negative status checks; không lọc console errors để tạo PASS. Generated coverage JSON, XLSX/PNG evidence được inspect theo rủi ro, không review chúng như human-written product code.

## Final evidence và limits

[Final Verification](../08-final-verification.md) có commands/logs, đúng line/branch metrics và AC/Test mapping. Artifact-enabled suite 265 passed, default 254 passed/11 model-path skips; mọi skipped case đã chạy trong artifact-enabled run. M02/M08 policy PASS. Browser desktop/mobile PASS; real WAV runtime COMPLETED/ESTIMATED với 151 grounded comments, restart/logout PASS. Raw report dùng combined coverage nhầm nhãn line ở vài mục; root final metrics hiệu chỉnh từ covered_lines/num_statements, không sửa/xóa lịch sử raw reports.

Mandatory findings còn mở: **0**. Residual risk: WSGI/parser/error/report validation branches chưa instrument đầy đủ; coordinator fail-closed recovery khi response mất/non-RUNNING chưa có direct test; actual-model/browser checks không cộng vào pytest coverage. MP3 native warnings vẫn được ghi; không có WER/CEFR validation/calibration. Các giới hạn này được trình trong evidence, không tự coi là user accepted. Chưa push/deploy hay nghiệm thu module khác. Next action: user review package và ghi final verdict cho cycle/scope.
