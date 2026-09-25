# Verification, browser QA và phục hồi context

Đọc reference này khi cần runtime/browser QA, Phase 08/09 hoặc tiếp tục sau session bị gián đoạn.

## 1. Browser QA có điều kiện

Chỉ dùng Chrome DevTools MCP khi dự án có web UI và công cụ khả dụng. Codex phải preflight capability trước khi phát hành prompt. Nếu không có MCP, dùng fallback đã duyệt trong Plan; Antigravity không được giả vờ MCP đã pass. Không chạy lại browser QA chỉ vì report, docs, lint metadata hoặc bookkeeping thay đổi; rerun khi user-visible/runtime integration thay đổi, evidence cũ stale hoặc Plan/Test Plan yêu cầu rõ.

Với web, kiểm tra khi phù hợp:

- Critical journey từ trạng thái sạch.
- Loading, success, empty, error, retry, repeated action.
- Console không có error/warning bất thường.
- Network URL, method, payload, status, response và call count.
- Auth, persistence, refresh, navigation và sign-out.
- Keyboard, label, focus và error announcement.
- Viewport desktop/tablet/mobile/minimum width.
- Visual comparison với reference đã duyệt.

Mẫu bug:

```text
Route:
Viewport:
Preconditions:
Steps:
Expected:
Actual:
Severity:
Console/Network evidence:
Screenshot/artifact:
```

MCP output là test evidence, không phải quyền đổi requirement.

## 2. Status và context recovery

Status luôn thuộc scope root: Lite dùng section Status trong
`docs/sdd/<kind>/<scope-slug>/PROJECT_SDD.md`; Standard dùng
`docs/sdd/<kind>/<scope-slug>/07-status.md`. Cập nhật Status local sau mỗi prompt
được phát hành và mỗi review outcome:

```text
Current phase:
Phase status: DRAFT | IN_REVIEW | CHANGES_REQUIRED | APPROVED | BLOCKED
Operating mode: Fast | Standard | Strict
SCOPE ID/TYPE/ROOT:
Prompt/evidence/review paths:
Artifact versions/approval state:
Research mode/record: RUN + path/version | SKIP + user decision/rationale
Phase records: 01 / 03 / 04 / 05 / 07 / 08 / 09
User verdicts/approval timestamps: 01 / 03 / 04 / 05 / 07 / 08 / 09
Current Task/Prompt ID/attempt/status/owner:
Last verified task:
Latest verified revision:
Handoff mode/inbound baseline:
WORKSPACE FINGERPRINT:
Fingerprint algorithm/metadata files:
Fingerprint exclusions:
Latest inspectable Antigravity change:
User-modified files:
Checks and results:
Review ID/findings/resolution:
Final-state UT/coverage evidence:
Browser QA and results:
Open defects:
Blockers/decisions:
Next action:
Last updated:
```

Khi bắt đầu session mới:

1. Đọc skill, project `AI_CONTEXT.md` và xác định feature/module active.
2. Resolve scope active; đọc `07-status`, Requirement, Specification, Test Plan,
   Plan và Tasks của scope; chỉ đọc Research khi mode là `RUN`, cùng tài liệu
   liên quan trực tiếp khi cần.
3. Kiểm tra Git/diff nếu có; nếu không ghi `Git not initialized`. Khi verify fingerprint, dùng đúng algorithm/metadata/exclusion trong Status; hash `v1` phải được xác minh lại và phát hành thành `v2` trước handoff mới.
4. Xác nhận active phase, task và next action.
5. Chỉ tiếp tục qua checkpoint có user verdict `APPROVED`; Codex recommendation chưa được người dùng duyệt vẫn là trạng thái chờ.

## 3. Phase 08 — Final Verification

Sau Phase 07 `APPROVED`, đọc quality-gates-evidence.md và chạy lại UT/coverage
trên final reviewed head/fingerprint. Phase 08 không được tái sử dụng report của
revision trước correction. Nếu UT/coverage `N/A`, record phải có applicability
rationale và alternative evidence đã được Test Plan/Plan/Task duyệt.

Codex kiểm tra Phase 08 và trình evidence/recommendation. Task chỉ đặt `Verified`
khi Phase 07/08 cùng inspect được, đạt kỹ thuật và Phase 08 có user verdict
`APPROVED`. Failed test, coverage check, critical uncovered risk hoặc stale
fingerprint làm task chưa sẵn sàng để người dùng chấp nhận.

## 4. Phase 09 — Acceptance

Codex sở hữu kế hoạch kiểm tra và review kỹ thuật; người dùng sở hữu quyết định
nghiệm thu. Codex tổng hợp evidence Phase 01–08, đối chiếu AC/Definition of Done
và trình Phase 09 package cùng recommendation. Không chạy lại toàn bộ checks mặc
định nếu Phase 08 vẫn khớp final fingerprint; chỉ tạo verification-only prompt
khi acceptance journey hoặc runtime evidence bắt buộc chưa có.

Preflight Phase 09 xác nhận mỗi artifact/task có evidence và user verdict tương
ứng. Thiếu record hoặc approval thì Codex recommendation là `BLOCKED`; scope chỉ
được accepted khi người dùng review và ghi verdict `APPROVED`.

Mỗi lần dùng ID `09-ACCEPTANCE-A<n>` và ghi vào Status. Nếu phát hiện regression:

1. Mark Phase 09 `CHANGES_REQUIRED` và link failed AC/Test ID.
2. Reopen task chịu trách nhiệm hoặc tạo bounded defect task.
3. Quay về Phase 07 và giao prompt sửa.
4. Sau Phase 07 được approve, chạy lại Phase 08 rồi trình Phase 09 mới.

Kiểm tra tương ứng của dự án:

- Lint/static analysis.
- Typecheck/compile.
- Unit/integration tests.
- Coverage threshold/no-regression delta, changed/critical code và uncovered branch analysis.
- Production build/package.
- Runtime smoke test.
- Conditional browser/Network/Console/accessibility/responsive/visual QA.

Không làm yếu test, exclusion hoặc threshold để ép pass.

## 5. Definition of Done

- Mọi Acceptance Criteria đã duyệt pass.
- Mọi task áp dụng ở trạng thái `Verified`.
- Phase Record 01, 03, 04, 05, 07, 08 và Review Record áp dụng đầy đủ, khớp final revision/fingerprint.
- Mọi automated required check bắt buộc pass.
- Clean Code review không còn `BLOCKER/MAJOR` mở.
- Final-state UT/coverage policy pass hoặc `N/A` có rationale/alternative evidence hợp lệ.
- Manual/runtime checks bắt buộc được ghi lại.
- Không còn blocker hoặc defect nghiêm trọng trong scope.
- Requirement, Specification, Test Plan, Plan, Tasks và Status của scope đúng
  thực tế; Research đúng thực tế khi `RUN`, hoặc skip record còn hợp lệ khi
  `SKIP`; README trỏ đúng path nếu có.
- Setup/verification chạy được từ môi trường sạch.
- Security/secret checks pass.
- Người dùng là final reviewer và đã approve Phase 09 của scope. Nghiệm thu cấp dự án chỉ là package tổng hợp các scope liên quan đã được nghiệm thu.

## 6. An toàn repository

- Bảo toàn dirty worktree và thay đổi ngoài scope.
- Không dùng destructive command nếu chưa được phép.
- Git init và local commit phải nằm trong workflow/prompt được duyệt.
- Push, deploy, production/external mutation luôn cần người dùng cho phép.
- Inspect staged content trước commit.
- Không commit generated output, dependency, local editor files hoặc secrets.
- Dùng `.env.example` với placeholder khi cần.
- Ghi dependency/architecture changes vào Plan trước implementation.
