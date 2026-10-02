# W3-PROMPT-001 — pipeline

PROMPT ID: W3-PROMPT-001
TASK IDS: W3-TASK-001, W3-TASK-002
SCOPE ID/TYPE/ROOT: W3 / feature / docs/sdd/features/w3-local-integration/
ATTEMPT: 1
HANDOFF MODE: isolated local Git worktree
REPO ROOT: /tmp/aicefr-w3-pipeline
BRANCH: feat/W3-pipeline
BASE REVISION: 7bb327b655c67d8eb5aafc4cd8ec9481fabdff28
BASE SOURCE REVISION: 2b428ceea9e4459f3235d4ce67f10bab31585ebf
WORKSPACE FINGERPRINT: 411c2366ca9d656366523883a3a6f7383506620208b8d0d7ba1495358c20aa84
FINGERPRINT ALGORITHM: sdd-workspace-v2
FINGERPRINT METADATA FILES: docs/sdd/features/w3-local-integration/prompts/W3-PROMPT-001-pipeline.md
FINGERPRINT EXCLUSIONS: KHÔNG CÓ
ARTIFACT VERSIONS: W3 v0.1
AUTHORIZATION: direct user instruction in 01-requirement, implementation/delegation allowed; final user verdict PENDING

## Authorization và vai trò
Thắng trực tiếp yêu cầu dùng subagents Luna triển khai hết W3, Codex review, lưu prompt/AI log và tạo nhánh riêng (02/10/2026). Chỉ dẫn mới nhất này thay executor Antigravity và giới hạn subagents read-only trong skill. Bạn là implementation agent gpt-6-luna; không tự approve phase/nghiệm thu. Không cần hỏi lại quyền implement. Mọi formal USER VERDICT giữ PENDING.

## Context phải đọc
AGENTS.md; AI_CONTEXT.md; docs/sdd/features/w3-local-integration/01-requirement.md, 02-research.md, 03-specification.md, 04-test-plan.md, 05-plan.md, 06-tasks.md, 07-status.md; các source/SDD trực tiếp liên quan. W2 specification/rubric/model mapping giữ nguyên. Bỏ qua context cấp repo đã cũ khi có record scope/revision mới hơn.

## Quy tắc worktree và báo cáo
Chỉ làm trong REPO ROOT chỉ định. Root integration branch và worktrees khác thuộc agents khác. Không git switch/reset/rebase/cherry-pick/push, không sửa AI workbook/Status/SDD của root. Local commit được user authorize; git add đúng allowed files + prompt của mình + raw report của mình. Không git add -A. Cài thêm dependency hoặc đổi shared contracts phải báo root trước. Không cần tạo subagents con.

Trước sửa: git status, git rev-parse HEAD, verify fingerprint bằng helper với đúng metadata files. Dùng PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python -m pytest ... trong worktree để tránh import editable root. Ruff /tmp/aicefr-w3-venv/bin/ruff. Env đã có existing .[dev], openpyxl và Playwright; optional ASR/VAD chưa cài. Report/coverage output ở /tmp theo lane.

UT REQUIRED: YES. Viết tests với code; assertion trên hành vi và rollback/privacy, không network/real data/model download. Đo line/branch changed packages và nêu uncovered critical paths; không hạ threshold/exclusion/skips để ép PASS. Không ghi stacktrace có nội dung input/secret/transcript. Không dùng test_only transcript/fixture score cho default runtime hoặc claim CEFR accuracy.

Raw report tiếng Việt, có Prompt/Task ID, starting fingerprint/base, commit/source tree fingerprint, file list, commands+exit+PASS/FAIL/SKIP, coverage/tool/report path, source citations khi dùng, assumption/limitation. Commit source/tests trước, sau đó viết raw report dẫn code commit và commit evidence. Return code/evidence commit SHA và blockers thật. Root sẽ review actual diff/rerun; COMPLETED không là user acceptance.

## Mục tiêu
Triển khai PipelineCoordinator và report SQLite bền vững theo spec W3; nối M01 và M02–M07, typed/injected services.

## Allowed files
src/aicefr/pipeline/** (mới); src/aicefr/report/sqlite.py (mới); src/aicefr/report/service.py (protocol/type annotation + transactional integration nhỏ); src/aicefr/storage/sqlite.py (schema v3 report + compatible migration + transaction-aware helper nếu cần); src/aicefr/api/student.py (refresh status sau synchronous enqueue); tests/pipeline/**; tests/report/test_sqlite_report.py; tests/storage/test_report_migration.py; evidence/raw-pipeline.md của scope W3.
Không sửa contracts.py, runtime/local, WSGI/templates, scoring/asr/features, CI hoặc test của lane khác.

## Contract khóa cho consumer app
PipelineCoordinator(*, responses, reports, reviews, qc_config, asr, extractor, scorer), public enqueue(ResponseRecord)->None. SQLiteReportRepository(store) implements put(DiagnosticReport), get(response_id). Dùng store.connection chung với SQLiteReviewRepository; put phải dùng transaction đang có để decision/report/audit rollback nguyên tử, không nested BEGIN.

## Hành vi và edge cases
- Enqueue synchronous local/demo. Chỉ QUEUED response có đúng current revision; duplicate/stale/final enqueue không đánh giá lại hay ghi đè teacher result. CAS cập nhật trạng thái.
- Bytes đọc từ BlobStore của ResponseService với checksum/owner provenance. ResponseRecord không chứa filename; nhận diện actual container từ bounded bytes và chuyển declared_extension nội bộ khớp M02 whitelist. Không nhận arbitrary path hoặc đổi raw audio.
- QC REJECT không ASR/scorer/report giả: status REJECTED reason; REVIEW tạo NOT_EVALUATED report/candidate với QC reasons, không ASR. PASS chạy AsrService, FeatureExtractor, RidgeScorer. ASR failure không ép default transcript/score; reason không bị mất.
- Report persisted trước final COMPLETED; trường hợp cần review final response revision dùng cho ReviewCandidate. Queue creation/report/status failure không để report hoàn chỉnh sai lifecycle hoặc stale candidate ngay sau tạo. Unexpected error controlled FAILED+reason, không input log.
- Grounded report evidence refs chỉ tạo từ actual transcript words/features; không invent timestamps. Preserve 5 coverage, Interaction null.
- Reopening SQLiteStore giữ report/result/audit; migration v1/v2→v3 bảo toàn dữ liệu; schema future rejected. Test callback rollback with real SQLite report repo + review repo.
- Refresh StudentService return status từ persisted response sau enqueue, không trả QUEUED cũ nếu pipeline đã kết thúc.

## Checks
W3-TEST-001–004 + tests/api existing regression impacted. Synthetic signal WAV in-memory; engine/scorer ports controlled only in tests. Targeted tests; line+branch coverage pipeline/report/storage; Ruff allowed source/tests, git diff --check. Agent tự chọn tests tối thiểu đủ critical states/restart/rollback/failure/duplicate privacy. Report failures thật.
