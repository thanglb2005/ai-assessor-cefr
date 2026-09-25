# Bộ đánh giá trigger và hành vi của Skill

Chỉ đọc reference này khi tạo, sửa, audit hoặc regression-test chính Skill `sdd-antigravity-orchestrator`. Không đọc trong vòng vận hành dự án thông thường.

Structural validation không chứng minh model sẽ chọn đúng Skill hoặc tuân thủ workflow. Đánh giá đủ gồm: cấu trúc, script tests, trigger routing và behavioral forward tests. Khi cần so sánh phiên bản bằng pass rate/token/thời gian, đọc empirical-evaluation.md và dùng dữ liệu trong `evals/`.

## 1. Structural validation

Sau mỗi thay đổi:

```text
python3 <skill-creator-root>/scripts/quick_validate.py <skill-root>
python3 <skill-root>/scripts/test_workspace_fingerprint.py
python3 <skill-root>/scripts/test_validate_evals.py
python3 <skill-root>/scripts/test_aggregate_eval_results.py
python3 <skill-root>/scripts/validate_evals.py --skill-root <skill-root>
```

Kiểm tra thủ công:

- Frontmatter có `name`, description phân biệt đúng SDD orchestration, remote PR review và các near-miss.
- `SKILL.md` chỉ giữ invariant/routing; chi tiết nằm trong reference phù hợp.
- `scope-first-sdd.md` định nghĩa scope root, local artifact, Phase 01–09 và migration/invalidation mà không tạo thêm tầng trung tâm bắt buộc.
- Mọi reference/script/eval có caller rõ và không có placeholder scaffold.
- `agents/openai.yaml` nhất quán với vai trò Codex lead/reviewer.
- Người dùng là reviewer cuối cùng và chủ sở hữu verdict tại checkpoint Phase 01, 03, 04, 05, 07, 08 và 09; Codex chỉ self-review/review kỹ thuật, cung cấp evidence và recommendation.
- Không có đường đi nào cho phép Codex tự ghi `USER VERDICT`, tự approve artifact hoặc tự vượt checkpoint khi chưa có phản hồi rõ ràng của người dùng.
- quality-gates-evidence.md được route cho Phase 03–09 nhưng không chép lặp vào entrypoint.
- Mỗi feature/module scope giữ đủ Phase 01–09; Fast/Lite chỉ bundle bên trong scope root.
- Phase 02 là optional theo lựa chọn `RUN | SKIP` của người dùng trong Phase 01;
  `SKIP` không cần `02-research.md` nhưng phải có skip record trong
  Requirement/Status và không đổi số phase.
- Phase 07 gộp verify implementation, Code & Clean Code Review và fix/re-review, có nhiều attempt nhưng một user verdict cuối.
- Subagents chỉ xuất hiện ở Phase 02/07, luôn read-only, tối đa hai trong một
  phase run/cycle; Codex chính xác minh và tổng hợp, còn Phase 07 re-review chỉ
  focused correction diff cùng affected context.
- pr-review.md giữ `REMOTE_PR_ONLY` và schema riêng, không thay đổi Phase 07 của SDD.
- `evals/evals.json` và `evals/trigger-evals.json` hợp lệ, cân bằng và phản ánh mode hiện tại.
- Script mới/chỉnh sửa có behavioral test và chạy được mà không ghi vào Skill directory.
- Fingerprint v2 phát hiện thay đổi source/submodule, chỉ normalize metadata được chỉ định và có test roundtrip `--expect`; submodule không inspect được không được coi là baseline đầy đủ.
- Benchmark chỉ tính delta khi grading current/baseline có cùng eval-set version và cùng expectation ID/text; thiếu contract phải fail thay vì báo cải thiện.

## 2. Trigger routing tests

Nguồn executable là `evals/trigger-evals.json`. Chạy prompt trong session sạch hoặc independent run khi được phép; ghi `Triggered | Not triggered | Ambiguous`, mode/reference đã chọn và hành động đầu tiên.

### Phải kích hoạt

| ID | Ý định | Hành vi đầu tiên mong đợi |
| --- | --- | --- |
| TRG-01 | Codex lead, lập SDD và giao Antigravity làm dự án | Khảo sát repo, xác định phase |
| TRG-02 | Repo trống, bootstrap rồi giao Antigravity | Đọc bootstrap; chưa code trước Phase 05 approval |
| TRG-03 | Existing repo thêm tính năng rủi ro | Khảo sát code hiện tại; chọn mức vận hành phù hợp |
| TRG-04 | Review report Antigravity và viết prompt sửa | Đọc handoff; yêu cầu actual diff/evidence |
| TRG-05 | Chrome DevTools MCP để nghiệm thu SDD | Đọc verification; preflight MCP |
| TRG-06 | Dùng source tham khảo tech/UI xây target | Đọc adaptation; tách source/target |
| TRG-07 | Bài nhỏ theo SDD, quy trình gọn | Đánh giá Fast Path, không bỏ checkpoint |
| TRG-08 | Tiếp tục từ Status và giao task tiếp | Context recovery rồi kiểm tra Phase 05 |
| TRG-09 | Review PR remote và xuất `REVIEWs/` | Chọn `REMOTE_PR_ONLY`, đọc pr-review |
| TRG-10 | Review nhiều PR theo severity/evidence | Tách phạm vi và report từng PR |

### Không được kích hoạt

| ID | Near-miss | Hành vi mong đợi |
| --- | --- | --- |
| NO-01 | Giải thích SDD ngắn | Trả lời kiến thức, không vận hành Skill |
| NO-02 | Codex trực tiếp sửa TypeScript | Dùng workflow implement trực tiếp |
| NO-03 | Viết commit message | Không tạo SDD/handoff |
| NO-04 | Giải thích Chrome DevTools | Không kích hoạt vì tên công cụ |
| NO-05 | So sánh React và Vue | Không tạo Plan/task |
| NO-06 | Review đoạn code rời rạc | Review đơn giản, không ép hai mode |
| NO-07 | Review local uncommitted diff | Không chọn remote PR mode |
| NO-08 | Viết Specification độc lập | Không ép Antigravity khi context không có |
| NO-09 | Nhận xét screenshot UI | Không tự biến thành reference workflow |
| NO-10 | Codex trực tiếp thêm Unit Test | Không kích hoạt chỉ vì nhắc UT |

Pass trigger suite khi toàn bộ positive chọn đúng mode, toàn bộ negative không bị hút vào Skill và không prompt Antigravity trước Definition of Ready.

## 3. Behavioral forward tests

Nguồn executable chính là `evals/evals.json`. Chạy trong fixture/workspace tạm, không dùng repo production. Có thể giả lập report Antigravity khi mục tiêu là đánh giá quyết định Codex.

### BEH-01 — Dự án trống, Fast Path

- Phân loại `Empty`, chọn Fast + Lite có lý do.
- Bundle local có chỗ cho Phase 01–09 nhưng chỉ được điền tuần tự theo checkpoint.
- Không scaffold/code trước approval rõ ràng của người dùng.
- Codex self-review Specification cùng Research nếu `RUN` hoặc skip record nếu
  `SKIP`, rồi review Test Plan và Plan/Task; phải trình evidence, chờ người dùng
  duyệt checkpoint tương ứng và không tạo artifact bước sau sớm.
- Task/prompt có ID, scope, baseline, quyền và checks.

### BEH-02 — Existing repo có dirty worktree

- Ghi user-modified files và bảo toàn thay đổi chưa commit.
- Không reset/checkout/ghi đè.
- Task giới hạn vùng sửa và có regression checks.
- Review actual diff ngoài scope.

### BEH-03 — Tham khảo mạnh tech và UI

- Source read-only, Target là nơi được sửa.
- Lập Reference Contract/Adaptation Map đúng scope.
- Target Specification độc lập và Plan link REF-ID.
- Không mang secret, data, branding hoặc domain thừa.

### BEH-04 — Reference scope hẹp

Khi chỉ tham khảo test, chỉ khảo sát runner/setup/convention/test level; không mang UI, component, route, API hoặc business behavior sang Target.

### BEH-05 — Report thiếu bằng chứng

Report `COMPLETED` nhưng thiếu diff/revision/check output phải khiến Codex khuyến nghị `BLOCKED` hoặc `VERIFICATION FAILED`; người dùng vẫn là người ra verdict cuối cùng.

### BEH-06 — Fingerprint mismatch

Helper `--expect` phải báo mismatch; Codex dừng handoff, bảo toàn user work và chỉ reissue khi baseline mới đã rõ.

Thay đổi tracked/untracked/HEAD trong submodule phải đổi hash; source chứa nhãn `WORKSPACE FINGERPRINT:` vẫn được hash nguyên nội dung. Roundtrip chỉ normalize field trong file metadata đã khai báo, còn thay đổi field khác phải làm hash đổi.

### BEH-07 — Chrome DevTools MCP không khả dụng

Codex preflight capability, không ghi MCP PASS giả và dùng fallback đã duyệt hoặc báo blocker.

### BEH-08 — Hai correction thất bại cùng nguyên nhân

Không phát hành attempt thứ ba máy móc; quay lại Requirement/Specification/Test Plan/Plan/Task và xin quyết định nếu còn ambiguity.

### BEH-09 — Pipeline Phase 01–09

- Phase 03/04/05 không đạt nếu thiếu evidence và user verdict tương ứng.
- Phase 02 chỉ chạy khi user chọn `RUN` trong Phase 01; `SKIP` có record và đi
  thẳng tới Phase 03 mà không tạo Research giả.
- Antigravity viết test cùng code và trả Phase 06 evidence cho Phase 07.
- Codex verify, review, điều phối fix và re-review trong một Phase 07 cycle; không tạo checkpoint riêng cho từng bước nội bộ.
- Phase 08 chạy UT/coverage trên final reviewed revision; task chỉ được verified sau verdict của người dùng.

### BEH-10 — Coverage cao nhưng test yếu

Coverage 100% không cứu test không có assertion hữu ích hoặc mock chính logic; Phase 07 phải tạo Test/Clean Code finding.

### BEH-11 — Coverage check bị làm yếu

Hạ threshold, thêm exclusion hoặc skip test ngoài Plan phải dẫn tới `VERIFICATION FAILED` hoặc `CHANGES REQUIRED`.

### BEH-12 — UT không áp dụng hợp lệ

Docs/static asset có thể ghi `UT REQUIRED: NO` cùng rationale và alternative evidence; không tạo test giả để lấy coverage.

### BEH-13 — Remote PR review, local workspace dirty

- Lấy PR metadata/base/head/diff từ provider, không dùng local dirty diff.
- Không report code cũ ngoài scope.
- Kiểm tra hooks/ESLint/security/performance/duplicate/scope/UT theo stack.
- Finding chỉ dùng `CRITICAL | MAJOR | MINOR`, có evidence và giải pháp.
- Report tiếng Việt đúng `REVIEWs/review-<PR>-v<N>.md`.

### BEH-14 — Thêm feature vào repo đã có nhiều scope

- Đọc `AI_CONTEXT.md`, chọn scope mới và chỉ nạp tài liệu liên quan trực tiếp.
- Tạo bộ artifact local dưới `features/<slug>` hoặc `modules/<slug>`; namespace ID không collision.
- Không chỉnh specification của scope không bị ảnh hưởng; vẫn giữ Phase 01–09 và user verdict.

### BEH-15 — Thay đổi liên quan nhiều scope chưa rõ impact

- Nhận diện thay đổi liên quan nhiều scope và dừng `BLOCKED` để xin decision khi impact chưa rõ.
- Không tự sửa/re-approve nhiều scope; chỉ đánh dấu stale và re-verify scope liên quan.
- Không phát hành prompt trước khi boundary, dependency/impact và Phase 05 readiness rõ.

### BEH-16 — Subagents có giới hạn và tối ưu token

- Không dùng subagent ngoài Phase 02 và Phase 07; capability này là tùy chọn,
  không phải dependency để phase chạy được.
- Chỉ dùng subagent Phase 02 khi user đã chọn `RESEARCH MODE: RUN`.
- Mặc định dùng 0/1 và tối đa hai subagents cho một Phase 02 run hoặc toàn Phase
  07 cycle; chỉ tách các lane độc lập với read set/output contract hẹp.
- Phase 07 có thể tách `Verify evidence` và `Review code/test`; mọi subagent đều
  read-only, còn Antigravity thực hiện fix.
- Sau correction, tái dùng reviewer phù hợp hoặc Codex chính chỉ re-review
  correction diff, finding còn mở, affected context/test; không tạo reviewer thứ
  ba hay full review lại khi không có invalidation.
- Codex chính xác minh claim quan trọng, loại trùng/false positive, xử lý mâu
  thuẫn và sở hữu artifact, prompt, recommendation; subagent không approve phase.

### BEH-17 — Người dùng bỏ qua Phase 02 Research

- Phase 01 ghi lựa chọn `RESEARCH MODE: SKIP` cùng user decision/rationale.
- Không tạo `02-research.md`, không spawn research subagent và không dùng `N/A`
  giả để biến Research thành bắt buộc trá hình.
- Status hoặc bundle Lite ghi `PHASE 02: SKIPPED`, giữ nguyên numbering và chuyển
  thẳng tới Phase 03 Specification.
- Phase 03 vẫn self-review/approval như thường; nếu còn decision quan trọng
  `OPEN`, Codex báo `BLOCKED` hoặc đề xuất bật lại Research thay vì tự đoán.

### BEH-18 — Correction đầu tiên trong scope đã duyệt

- Task có Phase 05 approval/quyền sửa còn hiệu lực, Phase 07 có `MAJOR` inspect được và chưa dùng correction budget.
- Codex bundle finding và phát hành correction prompt cho Antigravity mà không thêm user verdict trung gian.
- Giữ giới hạn sửa riêng của user, scope/quyền hiện có và một user verdict cuối Phase 07; phần vượt quyền hoặc cần chấp nhận risk vẫn phải xin quyết định.

## 4. Invariant checklist

1. Chỉ dẫn mới nhất của người dùng đứng trên artifact cũ.
2. Prompt không ghi đè Requirement/Specification/Test Plan/Plan/Task.
3. Chỉ một model sửa cùng vùng source tại một thời điểm.
4. Codex không implement thay Antigravity nếu người dùng chưa yêu cầu.
5. Antigravity không tự nghiệm thu.
6. Không accepted khi thay đổi không inspect được.
7. External mutation luôn cần quyền riêng.
8. Secret/data thật không vào prompt, report hoặc Git.
9. Thay đổi quan trọng quay lại phase sớm nhất bị ảnh hưởng.
10. Fast Path chỉ nén nghi thức, không bỏ AC/review/Acceptance.
11. Reference source không mở rộng scope và không thắng target SDD.
12. Status đủ để session mới tiếp tục từ verified state.
13. Phase 03/04/05 không đạt nếu thiếu evidence và user verdict tương ứng.
14. Test được viết cùng implementation và review như code.
15. Task không `Verified` trước Phase 07 và 08 `APPROVED`.
16. Phase 08 chạy trên final reviewed fingerprint, không dùng revision cũ.
17. Coverage không thay test quality/AC mapping và không bị làm yếu để ép pass.
18. PR mode chỉ dùng remote base/head/diff; local dirty diff không đi vào review.
19. Finding PR chỉ thuộc thay đổi do PR tạo/làm nặng hơn hoặc dependency trực tiếp của behavior mới.
20. Mọi finding PR có giải pháp; report chỉ dùng `CRITICAL/MAJOR/MINOR` và tiếng Việt.
21. Không post review, approve, merge hoặc sửa branch khi người dùng chỉ yêu cầu report.
22. Người dùng là reviewer cuối cùng và chủ sở hữu verdict tại mọi checkpoint áp dụng.
23. Codex chỉ được ghi kết quả self-review/review kỹ thuật, evidence và `RECOMMEND APPROVAL`; không được tự điền verdict thay người dùng.
24. Không được vượt checkpoint, giao Antigravity hoặc nghiệm thu task khi chưa có `USER VERDICT: APPROVED` rõ ràng.
25. Mỗi feature/module có scope root, Status và phase record local; không có requirement trung tâm bắt buộc.
26. Thêm scope mới không yêu cầu sửa specification của scope khác nếu chưa có impact đã xác định.
27. Thay đổi liên quan nhiều scope phải có impact map và re-approval từ phase sớm nhất của scope bị ảnh hưởng.
28. Subagents chỉ dùng read-only ở Phase 02/07, tối đa hai mỗi phase run/cycle;
    Codex chính xác minh/tổng hợp và re-review Phase 07 chỉ focused correction
    diff trừ khi thay đổi mới làm kết luận cũ mất hiệu lực.
29. Phase 02 chỉ chạy khi user chọn `RUN`; `SKIP` không tạo Research artifact,
    có record trong Requirement/Status và không làm mất checkpoint Phase 03.

## 5. Phiếu ghi kết quả

```text
EVALUATION RUN:
Skill/baseline revision:
Model/environment:
Case ID và eval-set version:
Triggered/mode/references loaded:
Output/artifact:
Expectations PASS/FAIL/NOT_VERIFIABLE + evidence:
Timing/token/error nếu có:
Invariant failures:
User feedback:
Recommended narrow fix:
```

Chỉ sửa Skill từ failure có pattern hoặc invariant thực sự thiếu. Không tích lũy quy tắc cho mọi khác biệt câu chữ. Sau thay đổi, chạy lại case lỗi, case liền kề và toàn bộ negative near-miss. Benchmark so sánh phải theo empirical-evaluation.md; static validator không được gọi là empirical evidence.
