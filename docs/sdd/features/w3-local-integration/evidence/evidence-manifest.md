# W3 — Evidence Manifest

Đo ngày 02/10/2026 trên repo chính thức, nhánh `feat/W3-local-integration`. Final product source `ffb325c`; HEAD `6ae8b40` chỉ thêm raw evidence, product trees giống nhau. [Final Verification](../08-final-verification.md) là kết luận kiểm thử độc lập của Codex; raw lane reports giữ lịch sử, không thay final checks hoặc user acceptance.

| ID | Artifact | Kết quả / phạm vi |
| --- | --- | --- |
| W3-EV-BASE | [Baseline](baseline.md) | main 2b428ce: 189 pass/10 skip; pinned Ridge env: 199 pass/0 skip |
| W3-EV-PIPELINE | [Raw pipeline](raw-pipeline.md), [correction](raw-pipeline-fix-01.md) | Agent source 66d23d4 → 5056d05; typed coordinator/SQLite/rollback/evidence |
| W3-EV-APP | [Raw app](raw-app.md), [correction](raw-app-fix-01.md) | Agent source 6415e11 → a750639; factory/auth/consent/UI/browser; old Silero failure retained |
| W3-EV-SPEECH | [Raw speech](raw-speech.md), [correction](raw-speech-fix-01.md), [provenance](model-provenance.md) | Agent source dfac63a → af5dc8a; pinned local adapters/validation/CI |
| W3-EV-BROWSER-AGENT | [Browser report](browser-qa.md) | Input evidence của Luna, riêng với root final rerun |
| W3-EV-ASR | [Actual adapter smoke](real-speech-smoke.md), [raw log](local-adapter-smoke.log), [MP3 cross-check](mp3-independent-decode.log) | Actual WAV/MP3; MP3 native warnings giữ nguyên; WER/CEFR accuracy chưa đo |
| W3-EV-REVIEW | [Review cycle](../reviews/review-01.md) | 10 findings resolved, no mandatory open; user verdict PENDING |
| W3-EV-TEST-FINAL | [Artifact test](final/pytest-artifact.log), [default test](final/pytest-default.log) | 265 pass/0 skip/0 fail; default 254 pass/11 model-path skips |
| W3-EV-COVERAGE | [Coverage JSON](final/coverage.json), [metrics](final/coverage-metrics.json) | Line/branch riêng; M02/M08 inherited policy PASS; uncovered risk ghi tại final record |
| W3-EV-BROWSER-FINAL | [Result và ảnh hashes](final/browser-result.json), [Final Verification](../08-final-verification.md) | Root actual Chromium rerun, desktop/mobile; 11 checks PASS, zero console/failed/external requests |
| W3-EV-RUNTIME-FINAL | [Actual pipeline log](final/local-pipeline-smoke.log), [reviewer harness](final/local-pipeline-smoke.py) | Factory/QC/Whisper/Silero/Ridge/SQLite thật; restart/session/logout PASS |
| W3-EV-HARNESS-HISTORY | [Reviewer failed attempt](final/local-pipeline-smoke-attempt-01.log) | Assertion field sai trong reviewer harness, không product finding; đã sửa harness và rerun PASS |
| W3-EV-CHECKS | [Static check record](final/static-checks.json), [environment](final/environment.json) | Ruff/docs/forbidden-file/patterns/compile/CLI/build/diff PASS; remote CI NOT_RUN |
| W3-EV-AI-LOG | [Prompt Log](../prompts/prompt-log.md), [audit](final/ai-log-audit.json) | Full dispatched prompts đã lưu file/Excel sheet Thắng trước gửi; historical sheets giữ nguyên |
| W3-EV-HASHES | [Artifact hash inventory](final/artifact-hashes.json) | SHA256/size của final evidence; inventory tự loại chính nó để tránh self-hash |
| W3-EV-FINAL | [Final Verification](../08-final-verification.md), [Acceptance package](../09-acceptance.md) | Codex technical PASS/RECOMMEND APPROVAL; user verdict PENDING |

Không commit raw audio/model/database/token/password/transcript. Fixture teacher override chỉ là dữ liệu kiểm thử, không teacher validation học thuật. Không push/deploy; không nhận code local là remote CI execution hoặc CEFR calibration.
