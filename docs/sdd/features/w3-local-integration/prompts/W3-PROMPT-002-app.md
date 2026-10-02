# W3-PROMPT-002 — app

PROMPT ID: W3-PROMPT-002
TASK IDS: W3-TASK-003, W3-TASK-004
SCOPE ID/TYPE/ROOT: W3 / feature / docs/sdd/features/w3-local-integration/
ATTEMPT: 1
HANDOFF MODE: isolated local Git worktree
REPO ROOT: /tmp/aicefr-w3-app
BRANCH: feat/W3-app
BASE REVISION: 7bb327b655c67d8eb5aafc4cd8ec9481fabdff28
BASE SOURCE REVISION: 2b428ceea9e4459f3235d4ce67f10bab31585ebf
WORKSPACE FINGERPRINT: 81731688bfea48acb6cf8e752d7b947f131a057b46fc7378f277505f837e55c6
FINGERPRINT ALGORITHM: sdd-workspace-v2
FINGERPRINT METADATA FILES: docs/sdd/features/w3-local-integration/prompts/W3-PROMPT-002-app.md
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
Ứng dụng local chạy được bằng python -m aicefr.local, login/logout/consent browser và teacher report/audio/review, composition actual M01–M08 interfaces.

## Allowed files
src/aicefr/local/** (mới); src/aicefr/auth/service.py (logout/session revocation additive); src/aicefr/api/wsgi.py; src/aicefr/api/templates.py; tests/local/**; tests/api/test_local_sessions.py; evidence/raw-app.md của scope W3. Không sửa contracts/student.py, storage/report/pipeline/asr/features/scoring, CI, README hoặc workbook.

## Dependencies đã khóa
PipelineCoordinator(*, responses,reports,reviews,qc_config,asr,extractor,scorer), SQLiteReportRepository(store) ở spec. Adapter FasterWhisperEngine(model_dir,*,weight_name='small',device='cpu',compute_type='int8') và SileroVadEngine(*,threshold=.5,min_silence_ms=150) do lane speech. Không cần import nặng/adapter khi optional config không có; inject actual services/engines cho test. Agent worktree chỉ có baseline, các import mới sẽ có khi root tích hợp; tránh fallback giả vì dependency chưa cherry-pick.

## Behavior
- CLI --help, init-demo provisioning fixture accounts explicit (getpass hoặc password stdin, không ghi credential/token vào evidence), serve --data-dir ngoài repo; loopback bind, server single-thread stdlib WSGI. Config QC explicit JSON; --demo sử dụng documented demo-only test config, UI cảnh báo synthetic/local demonstrator. Không auto-consent/login khi serve. No production claims/dependency mới.
- Factory tạo SQLiteStore, BlobStore, AuthService, ConsentService, ResponseService, ReportService (SQLiteReportRepository + verified SQLiteReviewRepository), ReviewService report_sink và StudentService pipeline.
- Ridge model default pinned loader; thiếu artifact/optional engine vẫn app hoạt động, report NOT_EVALUATED + reason, không fake score/transcript. Feature order/trained provenance lấy artifact nếu có, không hard-code duplicate feature list. Không relax SHA-256. Local ASR weight chỉ local path config; VAD silero defaults matching trained_with=.5/150; no cloud/model download.
- Login form/session cookie HttpOnly, SameSite, Path=/; no role claims/signup. Logout thật revoke session server-side. Cookie unsafe routes same-origin enforcement, gồm login/consent/logout/teacher actions; API bearer remains supported. Authenticated consent accept/withdraw user actions, block submit sau withdrawal.
- Browser upload form action redirects đến status/report; API submit vẫn JSON behavior cũ. Điều hướng đúng student/teacher role; readable errors/success/empty state; labeled form/keyboard/mobile layout.
- Teacher authenticated đọc report/listen audio ONLY when corresponding candidate exists; student/foreign actor denied, không leak existence/private blob path. Render teacher decision/AI provisional separately. Override requires band/reason; no fake teacher_verified.
- Controlled exception/config messages không expose secrets/paths/internal stack trace. Close store when server/test factory shutdown.

## Testing
W3-TEST-005, app/session CLI tests offline. Cover consent withdrawal, role/owner/audio denials, cookie CSRF/login/logout token invalidation, login restart persistence, generic errors, MIME/request caps. App production default no synthetic transcript. Agent báo exact invocation/interface to root for README/browser QA. Targeted tests + Ruff + diff check; integration imports missing report honestly and root resolves after lanes land.
