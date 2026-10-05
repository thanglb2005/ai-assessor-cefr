# W3 — Final Verification

PHASE RECORD ID: W3-08-A01
SCOPE ID/TYPE/ROOT: W3 / feature / docs/sdd/features/w3-local-integration/
SUBJECT: W3-TASK-001–008 sau correction review
BASE REVISION: 2b428ceea9e4459f3235d4ce67f10bab31585ebf
W3 SOURCE REVISION MEASURED BY THE FINAL REGRESSION: ffb325cc5ba8127f8c76a137a53e15a3dc0599b0
EVIDENCE HEAD: 6ae8b4060f0fa189d7f9a18dbe63c41c214c412e
WORKSPACE FINGERPRINT: ac30965ba60e1e27d1c57a1504e971c2caf07a4e83facaf5151feb66824f3e3c
CODEX CHECK RESULT: PASS at the measured W3 source; regression at the current merge head is pending.
CODEX RECOMMENDATION: RECOMMEND APPROVAL after merge-head CI passes.
USER VERDICT: PENDING
VERIFIED/APPROVED BY: chưa có user verdict
Ngày chạy: 02/10/2026, Asia/Ho_Chi_Minh. Reviewer: Codex, độc lập với raw reports của ba Luna.

Chỉ dẫn trực tiếp trong [Requirement](01-requirement.md) cho phép hoàn tất implementation/review/checks; package này không tạo phase approval hoặc task `Verified`. Các commit cuối chỉ thêm evidence/docs. Snapshot fingerprint được đo trước final docs commit, dùng `sdd-workspace-v2`, HEAD `6ae8b40`, metadata normalization chỉ cho file này và `07-status.md`; không thêm exclusions. Sau commit, Git HEAD/index làm workspace fingerprint thay đổi. Product trees đã kiểm chứng giống nhau tại `ffb325c` và `6ae8b40`:

| Tree | Git tree ID |
| --- | --- |
| src | eff3c24c5ff2c9e75eda879e095cc10a0b913be6 |
| tests | 5ae0807c1c405b542e5fee36e60d3df70c80f7a6 |
| scripts | 59def3beb3e94981922ac069082d5ad04cb30737 |
| .github | c8d069d5752d3a475e0cbf4769696b3a303091c5 |

## Checks và kết quả

Các lệnh dùng repo chính thức làm working directory, `PYTHONPATH=src`, Python/CLI từ `/tmp/aicefr-w3-venv`. Môi trường/version ghi tại [environment.json](evidence/final/environment.json). Các command bắt buộc đã chạy thực tế, exit 0; remote CI/deploy không chạy.

| Check | Lệnh / kết quả | Evidence |
| --- | --- | --- |
| Artifact-enabled regression + coverage | `AICEFR_MODEL_DIR=<external-model-directory> python -m pytest -q -m 'not smoke' --cov=aicefr --cov-branch --cov-report=term-missing --cov-report=json:/tmp/aicefr-w3-final/coverage.json`; 265 passed, 0 skipped, 0 failed, 8.58s | [pytest log](evidence/final/pytest-artifact.log), [coverage JSON](evidence/final/coverage.json) |
| Default offline regression | `env -u AICEFR_MODEL_DIR python -m pytest -q -m 'not smoke'`; 254 passed, 11 skipped, 0 failed, 5.96s | [default log](evidence/final/pytest-default.log) |
| Browser journey | `PLAYWRIGHT_BROWSERS_PATH=/tmp/aicefr-w3-browsers python scripts/qa/w3_app_browser.py --model-artifact <external-artifact> --evidence-dir /tmp/aicefr-w3-final/browser`; PASS | [result/hashes](evidence/final/browser-result.json), [stderr](evidence/final/browser-stderr.log), ảnh bên dưới |
| Real local pipeline | `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=1 python docs/sdd/features/w3-local-integration/evidence/final/local-pipeline-smoke.py`; actual runtime/persist/restart/logout PASS | [reviewer harness](evidence/final/local-pipeline-smoke.py), [log](evidence/final/local-pipeline-smoke.log) |
| Ruff | `ruff check src tests scripts`; PASS | [log](evidence/final/ruff.log) |
| Markdown links | `python scripts/ci/check_md_links.py`; local links PASS; external internal-reference targets skipped theo guard | [log](evidence/final/md-links.log) |
| Forbidden-file guard | `python scripts/ci/check_forbidden_files.py`; không tracked audio/model/DB/secret extension bị cấm | [log](evidence/final/forbidden-files.log) |
| Credential patterns | `python docs/sdd/features/w3-local-integration/evidence/final/credential-pattern-review.py`; 0 finding, chỉ bốn pattern families, không phải full PII/secret audit | [result](evidence/final/credential-patterns.json) |
| Compile | `PYTHONPYCACHEPREFIX=/tmp/aicefr-w3-final/pycache python -m compileall -q src`; exit 0 | [check record](evidence/final/static-checks.json) |
| CLI | `python -m aicefr.local --help`; exit 0 | [help](evidence/final/cli-help.log) |
| Build | `python -m pip wheel . --no-deps --no-build-isolation --wheel-dir /tmp/aicefr-w3-final/wheel`; exit 0 | [wheel build](evidence/final/wheel-build.log) |
| Diff | `git diff --check 2b428ce` trên final working state và staged diff check; PASS | [check record](evidence/final/static-checks.json) |
| AI log | Excel mở được; full text của 10 dispatched prompt files và user audio reply khớp cột E; giữ sheets/rows lịch sử | [audit](evidence/final/ai-log-audit.json), [Prompt Log](prompts/prompt-log.md) |

External Ridge directory đã dùng: `/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src/aicefr/scoring/models`; artifact hash `7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a`. Wheel không commit: `aicefr-0.1.0-py3-none-any.whl`, 79022 bytes, SHA256 `247c680cf964c614d3955a115c3086b8da4485c327d8e1d469c52ce2d57846ef`.

Final whitespace check phát hiện trailing blank lines ở các tài liệu ban đầu. Đã normalize EOF và đồng bộ hai amendment prompt copies với Excel, giữ nguyên nội dung đã dispatch; kiểm tra diff cuối chạy lại PASS. Không đổi product source.

Default 11 skips đều do chưa đặt external Ridge artifact path: 10 tests features/scoring kế thừa và 1 factory pin/reopen test mới. Tất cả đã chạy trong 265-pass artifact-enabled run; missing-model refusal vẫn được test độc lập, không bị skip.

## Coverage và uncovered risk

Coverage.py 7.16.2, pytest-cov 7.1.0, branch enabled. Line = `covered_lines / num_statements`; branch = `covered_branches / num_branches`. `percent_covered`/terminal `Cover` là combined metric khi bật branch, không phải line coverage. Raw lane reports giữ nguyên lịch sử; các nhãn line bị nhầm combined trong raw report được hiệu chỉnh bằng số đo dưới đây và [coverage-metrics.json](evidence/final/coverage-metrics.json).

| Scope | Line | Branch | Policy / kết quả |
| --- | --- | --- | --- |
| Global | 2677/2923 = 91.58% | 579/736 = 78.67% | Số đo; không có global threshold mới |
| M02 audio + QC | 216/228 = 94.74% | 84/94 = 89.36% | ≥90% line / ≥85% branch: PASS |
| M08 auth + storage | 356/366 = 97.27% | 55/62 = 88.71% | ≥90% line / ≥85% branch: PASS |
| PipelineCoordinator | 125/126 = 99.21% | 31/32 = 96.88% | CAS, refusals, transactional rollback covered |
| SQLite report repository | 17/17 = 100% | 2/2 = 100% | Persistence/reopen và rollback covered |
| WSGI | 303/395 = 76.71% | 94/152 = 61.84% | Parser/exception/config variants còn chưa covered |
| Templates | 76/81 = 93.83% | 9/14 = 64.29% | Teacher variants được browser kiểm thêm |
| Local factory | 88/107 = 82.24% | 6/14 = 42.86% | Lazy real adapters được smoke kiểm thêm |
| ASR adapter | 46/58 = 79.31% | 12/14 = 85.71% | Real pinned hash/decode được smoke kiểm thêm |
| VAD adapter | 43/48 = 89.58% | 11/14 = 78.57% | Real bundled inference được smoke kiểm thêm |
| M06 report service | 150/166 = 90.36% | 48/60 = 80.00% | Invalid evidence/teacher shape variants còn thiếu |

Function/method coverage: tool không báo riêng; không suy ra từ line metric. Không thay thresholds/config exclusions để đạt PASS; giữ 101 excluded lines của tooling hiện hành. Các run browser/real-model không instrument trong pytest coverage, không cộng vào phần trăm. Global branch giảm/tăng không được suy ra vì baseline W3 không có comparable global branch report.

Critical residual paths: coordinator line 157 là recovery khi response biến mất/không còn RUNNING, hiện fail closed bằng raise; test đã cover rollback và stale RUNNING revision nhưng chưa cover biến thể này. WSGI malformed-input/exception variants, CLI startup errors và report malformed feature/teacher-result shapes còn có gaps; source đã review fail-closed guards, không claim branch-complete. Không còn finding bắt buộc mở. Các gaps được trình user cùng runtime/browser evidence, không tự ghi risk accepted.

## Browser và actual local smoke

Browser fixture tự tạo dài 2s, QC REVIEW nên ASR/VAD được bypass có chủ đích. Journey: login→current consent→upload→report null overall→teacher queue/claim→authorized audio (MIME/hash đúng)→override B1→student report có teacher result riêng, AI overall vẫn null. Withdraw consent chặn lần submit thứ hai, vẫn chỉ một response; logout làm token cũ bị từ chối; student/foreign access trả 403/404 đúng. Có 11 DOM/document/viewport checks, desktop 1280×800 và mobile 390×844; 0 console errors, 0 failed requests, 0 external requests. Codex đã mở và kiểm đủ bốn ảnh:

- [Desktop student report](evidence/final/browser/browser-qa-desktop-student-report.png)
- [Desktop teacher review](evidence/final/browser/browser-qa-desktop-teacher-review.png)
- [Mobile student upload](evidence/final/browser/browser-qa-mobile-student-upload.png)
- [Mobile teacher detail](evidence/final/browser/browser-qa-mobile-teacher-detail.png)

Actual smoke dùng WAV được phép, SHA256 `5bb09620a28f6935902f1cab9180ce81960a2109b823897313bdc859a936609f`, 41.145s. Factory/services/SQLite thật, QC PASS, pinned Whisper small, Silero 6.2.1, features v3/18 và Ridge pin; không ASR/scorer double. Hoàn tất 20.58s, response COMPLETED, report ESTIMATED, 151 comments có 151 evidence IDs khác nhau, 0 invalid evidence. `teacher_verified=false`, không tự thêm teacher verdict. Reopen giữ nguyên report/status/session và logout revoke PASS. Versions QC/ASR/transcript/features/assessment có trong log. Audio/model/runtime DB/password/token/transcript không ghi vào Git evidence.

Reviewer smoke attempt đầu dừng ở assertion dùng nhầm field `DiagnosticReport.evidence_refs`; report thực tế có `comments` và `evidence_issues`. [Log thất bại](evidence/final/local-pipeline-smoke-attempt-01.log) được giữ. Chỉ sửa reviewer harness rồi rerun toàn luồng; không sửa product để làm test pass. [Adapter smoke trước đó](evidence/real-speech-smoke.md) giữ MP3 native decoder warnings và independent decoder cross-check; không claim clean MP3/bit-exact equivalence. WER/CEFR accuracy/calibration **NOT_MEASURED**; filename CEFR không dùng làm ground truth.

## Kiểm tra đồng bộ main ngày 05/10/2026

`origin/main` tại `8032e55d911745e9cd4267f6a9c5dcae8d24b440` có 13 commits mới từ baseline W3 `2b428ce`. `git merge-tree origin/main HEAD` báo đúng một content conflict ở README AI log. Mình đã kết hợp mục AI Usage Log của Sang từ main với các link W3 và cập nhật ngày/prompt log. `src/aicefr/asr/service.py` được auto-merge sạch: main chuyển QC reject reasons sang transcript; W3 giữ log exception an toàn. Main đi kèm thay đổi fixture, assertion chuyển QC reasons tới scorer và tests integration scoring. Không còn conflict marker; `git diff --check origin/main` PASS. Hai đường dẫn duy nhất bị sửa bởi cả hai nhánh là README này và ASR service.

Các con số 265-pass/254-pass, coverage, browser và real-model ở mục trên được đo tại W3 source revision `ffb325c`, trước khi đồng bộ commit main. Environment hiện tại không có pytest cài sẵn, nên chưa rerun regression tại merge head; không ghi kết quả cũ như test cho merge head. Khi PR được mở, CI của nhánh đã tích hợp cần xác nhận các thay đổi upstream cùng W3.

## Traceability và kết luận kỹ thuật

| Test IDs | Tests / evidence cuối |
| --- | --- |
| TEST-001–004 | tests/pipeline/test_coordinator.py; tests/report/test_sqlite_report.py; tests/storage/test_report_migration.py; actual pipeline smoke |
| TEST-005 | tests/local/test_sessions.py, test_consent_submission.py, test_consent_version_guard.py, test_factory_integration.py; tests/auth/test_logout.py; tests/api/test_local_sessions.py; browser journey |
| TEST-006 | tests/asr/test_local.py; tests/features/test_local.py; tests/scoring/test_w3_validation.py; actual speech/pipeline logs |
| TEST-007 | scripts/qa/w3_app_browser.py + final browser result/ảnh |
| TEST-008 | regression, Ruff, guards, compile/build/CLI, AI log audit, CI actual diff |

[Review cycle](reviews/review-01.md) đã resolve W3-RV-001–010; [hash manifest](evidence/final/artifact-hashes.json) cho phép đối chiếu evidence. Merge với `origin/main` không còn conflict nhưng regression chưa được chạy tại merge head; review CI sau khi PR được mở. Deployment NOT_RUN; real learner operations/calibration ngoài scope. User verdict vẫn PENDING.
