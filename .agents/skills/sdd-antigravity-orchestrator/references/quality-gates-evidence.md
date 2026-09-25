# Phase Review, Clean Code, Unit Test, Coverage và Evidence

Đọc reference này khi tạo/verify Research, Specification, Test Plan, Plan, Task;
khi viết prompt implement; khi review code; hoặc khi nghiệm thu UT/coverage.
Đây là quality contract dùng chung cho Phase 03–09. Mọi record phải gắn với một
`SCOPE ID` và `SCOPE ROOT`.

## Mục lục

1. Pipeline và Evidence Contract.
2. Phase 03–05: Specification, Test Plan, Plan và Task Readiness.
3. Phase 07: verify implementation, review và fix/re-review cycle.
4. Unit Test, Coverage Contract và Phase 08.
5. Phase 09 traceability và cơ sở kỹ thuật.

## 1. Pipeline bắt buộc

```text
01 Requirement → User approval
→ [02 Research khi user chọn RUN] → 03 Specification → Codex self-review/evidence → User approval
→ 04 Test Plan → Codex self-review/evidence → User approval
→ 05 Plan & Task Readiness → Codex self-review/evidence → User approval
→ 06 Implementation & Test → Antigravity report/evidence
→ 07 Implementation Review
   → verify implementation/evidence
   → review code, Clean Code và test
   → fix + re-review khi có finding bắt buộc
   → User final verdict cho toàn review cycle
→ 08 Final Verification trên final state → User task acceptance
→ 09 Acceptance theo AC/Definition of Done → User scope acceptance
```

Test phải được thiết kế cùng code để review được testability và tính đúng của test. Bước UT sau Review là **lần chạy lại bắt buộc trên trạng thái cuối đã xử lý review**, không phải đợi review xong mới bắt đầu viết test.

Codex không được tự vượt checkpoint từ technical check của mình. Phase 01, 03,
04, 05, 07, 08 và 09 chỉ được đi tiếp khi người dùng review evidence và ghi
verdict `APPROVED`. `CHANGES_REQUESTED`, `BLOCKED` hoặc `PENDING` đều chưa được
đi tiếp. Phase 02 là optional: nếu `RUN` thì được review cùng Phase 03; nếu
`SKIP` thì Phase 03 dùng skip record đã được người dùng chọn trong Phase 01.
Phase 06 được review trong Phase 07.
`N/A` chỉ hợp lệ khi Codex nêu rationale/alternative evidence và người dùng chấp thuận.
`SKIPPED` chỉ áp dụng cho Phase 02 khi người dùng đã chọn `RESEARCH MODE: SKIP`;
đây không phải overall `N/A` của checkpoint Phase 03.

Fast Path được gộp record nhưng không bỏ phase hoặc checkpoint áp dụng. Standard/Strict lưu record đầy đủ trong artifact/Status hoặc đường dẫn evidence đã duyệt.

Record có thể trình bày compact và tránh lặp evidence. Với task nhỏ, một package
chỉ cần outcome, command/evidence chính, blocking findings và next action. Phase
07 có nhiều attempt nhưng chỉ một user verdict cuối; Phase 08 luôn trỏ tới final
fingerprint sau review.

## 2. Evidence Contract dùng chung

Mọi kết luận `PASS` phải dựa trên evidence inspect được, không chỉ lời khẳng định của model.

Mẫu Phase Review Package:

```text
PHASE RECORD ID: <scope>-<01|03|04|05|07|08|09>-A<attempt>
PHASE: <number — name>
SCOPE ID/TYPE/ROOT:
SUBJECT: <artifact version | Task ID | Prompt ID>
BASE/HEAD REVISION:
WORKSPACE FINGERPRINT:
FINGERPRINT ALGORITHM/METADATA FILES/EXCLUSIONS:
CHECKS/SELF-REVIEW PERFORMED BY CODEX:
- <check>: PASS | FAIL | N/A — <actual result>
APPLICABILITY: REQUIRED | N/A
APPLICABILITY RATIONALE:
ALTERNATIVE EVIDENCE:
EXPECTED:
ACTUAL:
EVIDENCE:
- <artifact path/section, diff, file:line, command output, report path, screenshot/log>
OPEN FINDINGS/RISKS:
CODEX CHECK RESULT: PASS | FAIL | BLOCKED | N/A
CODEX RECOMMENDATION: RECOMMEND APPROVAL | CHANGES REQUIRED | BLOCKED | N/A
USER VERDICT: APPROVED | CHANGES_REQUESTED | BLOCKED | PENDING
VERIFIED/APPROVED BY: User
USER VERDICT AT:
NEXT ACTION:
```

Evidence đạt khi:

- Liên kết đúng artifact/task/prompt và revision/fingerprint.
- Ghi command/check chính xác cùng kết quả thực tế; không ghi `PASS` nếu command không chạy.
- Report/file/screenshot/log có đường dẫn hoặc nội dung tóm tắt đủ kiểm tra.
- Failed/skipped checks và giới hạn môi trường không bị ẩn.
- `N/A` có lý do và alternative evidence, không dùng để né required check.
- Codex kiểm tra actual diff và chạy lại targeted/risk-based checks ở Shared workspace.
- Không có `USER VERDICT: APPROVED` thì package chỉ là self-review/recommendation, chưa phải phase approval.

Evidence từ Antigravity là implementation evidence đầu vào. Codex sở hữu
technical self-review, Phase 07 review cycle, kiểm tra evidence và
recommendation. Người dùng sở hữu mọi verdict, task acceptance và nghiệm thu cuối.

Các checkpoint không được có overall `RESULT: N/A`. Chỉ phần UT/coverage của
Phase 08 được `N/A` khi thật sự không áp dụng, applicability đã được Phase 04/05
duyệt, record có rationale cùng alternative evidence và các check khác vẫn đạt.

## 3. Phase 03 — Specification Approval

Phase 03 luôn review Specification; chỉ review Research khi Phase 02 được chọn
`RUN`. Nếu người dùng chọn `SKIP` trong Phase 01, Phase 03 kiểm tra skip record
thay vì yêu cầu `02-research.md`.

Phase 02 chỉ có thể dùng read-only subagents khi mode là `RUN` và có các
research lane thật sự độc lập. Mặc định dùng 0; tối đa hai subagents trong toàn
Phase 02. Mỗi lane chỉ nhận
objective, read set/path, câu hỏi cần trả lời và output contract cần thiết; không
chép toàn bộ context nếu có thể dẫn chiếu. Subagent chỉ trả fact/finding,
uncertainty và evidence reference, không sửa artifact và không biến option thành
decision. Codex chính phải mở nguồn quan trọng để xác minh, xử lý mâu thuẫn,
tổng hợp `02-research.md` và trình decision cần người dùng duyệt. Nếu một lane
phụ thuộc kết quả lane khác thì xử lý tuần tự bằng Codex chính, không parallelize
giả tạo.

Kiểm tra:

1. Requirement/Status ghi `RESEARCH MODE: RUN | SKIP` theo quyết định của user.
   Nếu `RUN`, Research ghi nguồn/context đã xem, finding, constraint, risk và
   assumption. Nếu `SKIP`, không yêu cầu artifact Research nhưng phải có skip
   rationale ngắn.
2. Research khi `RUN` không tự thêm requirement và phân biệt fact, inference,
   option và decision của user.
3. Scope ID/root, mục tiêu, user journey, in scope và out of scope nhất quán.
4. Mỗi `FR-*` có hành vi/input/output đủ rõ và không mâu thuẫn.
5. Mỗi `AC-*` quan sát được, testable và liên kết ít nhất một requirement.
6. Success, invalid, boundary, failure và recovery quan trọng đã được mô tả.
7. Security/privacy/accessibility/responsive được xử lý hoặc ghi `N/A` có lý do.
8. Assumption, dependency/impact và open question được tách khỏi requirement đã duyệt; related scope được khai báo.
9. Không còn product decision khó hoàn tác bị model tự đoán.

Evidence tối thiểu: Specification version/path; Research version/path cùng
nguồn/finding chính nếu `RUN`, hoặc skip record nếu `SKIP`; bảng trace
`FR-* → AC-*`, danh sách ambiguity/open decision và kết quả từng check.

Codex ghi `CODEX CHECK RESULT` và recommendation. Chỉ user verdict `APPROVED`
mới hoàn tất Phase 03 và cho phép tạo Test Plan.

## 4. Phase 04 — Test Plan Approval

Phase 04 phải được review trước khi tạo Plan.

Kiểm tra:

1. Mỗi `FR/AC` quan trọng có Test ID, scenario và expected result.
2. Test Plan bao phủ success, invalid, boundary, failure/recovery và regression phù hợp.
3. Test level, command, UT/coverage applicability và alternative evidence được xác định.
4. User-visible behavior có browser/manual verification khi cần.
5. Test cases có thể thực thi trong runtime/package manager/convention của repo.
6. Không dùng Test Plan để thêm requirement ngoài Specification.

Không đặt một coverage % toàn cầu cho mọi dự án. Chủ dự án chọn policy theo criticality, lifetime, change frequency và testability. Coverage là chỉ báo rủi ro, không thay thế review chất lượng test.

Evidence tối thiểu: artifact version/path, `FR/AC → Test ID → test level/command`, coverage/applicability policy, risk/trade-off và open decision.

Codex tự review Test Plan và đưa recommendation. Chỉ user verdict `APPROVED`
mới hoàn tất Phase 04 và cho phép tạo Plan.

## 5. Phase 05 — Plan & Task Readiness Approval

Phase 05 chính là Definition of Ready có evidence, chạy trước prompt Antigravity.

Kiểm tra:

1. Plan truy ngược được tới `FR/AC` và Test Plan, đúng scope boundary.
2. Module boundary, data flow, state, API/storage/error contract và dependency đủ rõ để implement.
3. Plan phù hợp runtime, package manager, convention và code hiện tại.
4. Rủi ro, rollback/recovery, Clean Code policy và required checks đã được nêu.
5. Task liên kết Specification/AC, Test Plan và Plan version đã duyệt.
6. Mục tiêu quan sát được; in/out scope và vùng file rõ.
7. Dependency/input/reference và scope liên quan đã sẵn sàng.
8. Task đủ nhỏ cho một vòng implement–review; không trộn cleanup lớn ngoài scope.
9. Evidence/report format và quyền local/external rõ.

Evidence tối thiểu: Plan/Task version/status, trace `FR/AC → Test ID → Task`, applicability decisions, commands, expected outputs và Phase 05 record.

Codex chỉ được đề xuất task ready. Prompt Antigravity chỉ được phát hành sau
user verdict `APPROVED` cho Phase 05.

## 6. Phase 07 — Implementation Review Cycle

Phase 07 bắt đầu từ implementation report của Phase 06 và kết thúc bằng một
user verdict cho toàn cycle. Mỗi diff mới tạo một attempt `07-A<n>`; verify,
review và fix/re-review là các bước nội bộ, không phải ba checkpoint riêng.

### Subagent lanes và token boundary

Chỉ dùng subagents khi diff/evidence đủ lớn hoặc có hai lane độc lập tạo giá trị
rõ. Mặc định dùng 0 hoặc 1; tối đa hai subagents trong toàn Phase 07 cycle:

1. `Evidence reviewer`: đối chiếu report, baseline/fingerprint, command output,
   failed/skipped checks và evidence path.
2. `Code/test reviewer`: review actual diff, affected context, Clean Code, hành
   vi và chất lượng test theo scope/AC đã duyệt.

Hai lane đều read-only và không được sửa source/artifact, chạy mutation, gửi
correction prompt hay đưa phase verdict. Input phải bounded bằng Task/AC ID,
base/head hoặc diff range, file/path cần đọc và output schema; không fork toàn bộ
hội thoại. Output chỉ gồm finding có location/evidence, uncertainty và phần chưa
kiểm tra được.

Codex chính phải kiểm tra lại evidence/finding quan trọng, loại trùng và false
positive, xử lý mâu thuẫn giữa hai lane, chạy check cần thiết và sở hữu Review
Record/recommendation. Antigravity thực hiện fix. Sau fix, tái dùng reviewer phù
hợp hoặc để Codex chính re-review chỉ correction diff, finding còn mở, affected
context và targeted tests; không tạo reviewer thứ ba hoặc review lại toàn bộ
repo/diff cũ trừ khi correction làm scope/kết luận cũ mất hiệu lực. Thiếu
capability subagent không làm phase `BLOCKED`; Codex chính thực hiện checklist.

### 6.1 Verify implementation và evidence

Codex xác minh:

1. Baseline/fingerprint/artifact version đúng.
2. Diff nhỏ nhất và không vượt file/scope hoặc direct impact đã được duyệt.
3. Production code và test được thêm/cập nhật trong cùng task khi UT áp dụng.
4. Targeted tests, lint/typecheck/build và runtime/browser check đã chạy theo prompt.
5. Coverage command đã chạy khi áp dụng; report không che failed/skipped tests.
6. Antigravity tự review diff và ghi assumption/blocker.
7. Evidence có thể inspect bằng diff/patch/revision và command output.

Nếu baseline/diff không inspect được, required check bị che, scope violation
đáng kể hoặc evidence thiếu đến mức không thể đánh giá, Phase 07 là `BLOCKED`
hoặc `CHANGES_REQUIRED`. Không ghi review `PASS` dựa trên report không đáng tin.

### 6.2 Review code, Clean Code và test

Khi thay đổi inspect được, Codex review mọi dòng human-written trong active
scope và đủ context của file/module cùng direct dependency/impact. Generated hoặc
vendor data chỉ được scan theo risk và phải ghi phạm vi review.

Review checklist:

- **Scope/traceability:** đúng Scope root, Task, AC và Plan; không thêm feature/cleanup hoặc sửa scope khác ngoài impact đã duyệt.
- **Design:** boundary, abstraction, dependency direction và integration phù hợp hệ thống.
- **Functionality:** success/error/boundary/concurrency/state behavior đúng người dùng và contract.
- **Simplicity:** không phức tạp hơn cần thiết, không over-engineer, không abstraction speculative.
- **Responsibility/coupling:** function/class/component có trách nhiệm rõ, dependency explicit, code testable.
- **Duplication/dead code:** không tạo duplication có hại, unused import/code/TODO/comment cũ được xử lý trong scope.
- **Naming:** tên diễn đạt mục đích/domain, không mơ hồ hoặc dài vô ích.
- **Comments/docs:** comment ưu tiên giải thích `why`; README/API/setup được cập nhật nếu hành vi sử dụng thay đổi.
- **Style/consistency:** theo formatter/linter/style guide và convention repo; không block chỉ vì sở thích cá nhân.
- **Error/security/accessibility/performance:** kiểm tra theo risk/task và gọi reviewer/chuyên môn khác nếu Codex không đủ evidence.
- **Tests:** đúng test level, behavior-focused, sẽ fail khi behavior hỏng, assertion có ý nghĩa, không quá coupled implementation.
- **Test code quality:** test dễ đọc, deterministic, không phức tạp hoặc duplication vô lý.
- **Repository health:** thay đổi cải thiện hoặc ít nhất không làm giảm maintainability/readability/testability.

Review finding và severity:

```text
FINDING ID: FINDING-<task>-<n>
SEVERITY: BLOCKER | MAJOR | MINOR | NIT
CATEGORY: Scope | Design | Functionality | Clean Code | Test | Security | Accessibility | Docs | Other
LOCATION: <file:line | artifact section>
OBSERVED EVIDENCE:
RISK/FAILED AC:
REQUIRED CHANGE: <bắt buộc với BLOCKER/MAJOR>
STATUS: OPEN | RESOLVED | ACCEPTED_RISK | SUPERSEDED
RESOLUTION EVIDENCE:
```

- `BLOCKER`: không thể nghiệm thu, có nguy cơ nghiêm trọng hoặc evidence/baseline không đáng tin.
- `MAJOR`: sai AC/Plan, regression, clean-code/test issue ảnh hưởng maintainability/correctness; phải sửa.
- `MINOR`: nên sửa trong task nếu nhỏ; có thể tạo bounded follow-up nếu không ảnh hưởng acceptance.
- `NIT`: không block, chỉ polish/style preference.

Review Record:

```text
REVIEW ID: 07-<task>-A<attempt>
TASK/PROMPT ID:
BASE/HEAD/FINGERPRINT:
REVIEWED SCOPE/FILES:
CHECKLIST RESULT:
FINDINGS: <IDs + severity/status>
CHECKS RERUN BY CODEX:
RESULT: PASS | CHANGES_REQUIRED | BLOCKED
EVIDENCE:
```

### 6.3 Fix và re-review

Khi có finding bắt buộc:

1. Bundle mọi `BLOCKER/MAJOR` vào correction prompt đầu tiên trong phạm vi Task/quyền Phase 05 còn hiệu lực, không cần user yêu cầu sửa từng finding. Giới hạn sửa rõ ràng của user vẫn được giữ; phần vượt scope/quyền hoặc cần chấp nhận risk phải xin quyết định.
2. Antigravity sửa và trả diff/evidence cho attempt tiếp theo.
3. Codex verify lại evidence, re-review correction diff cùng finding còn mở,
   affected context/test và cập nhật từng finding; nếu dùng subagent thì tái dùng
   reviewer phù hợp trong giới hạn hai subagents của cycle.
4. Lời giải thích chat không thay code/evidence cần thiết.
5. `ACCEPTED_RISK` phải do người có thẩm quyền chấp nhận và ghi lý do; model không tự miễn.
6. Nếu correction đổi behavior/Plan hoặc mở rộng scope, quay lại phase sớm nhất bị ảnh hưởng.

Không cần user verdict giữa ba bước nội bộ. Chỉ dừng xin quyết định khi cần mở
rộng scope/quyền, chấp nhận risk, evidence bị block hoặc cùng root cause lặp lại
sau correction budget. Codex chỉ đưa `RECOMMEND APPROVAL` khi evidence đáng tin
và không còn `BLOCKER/MAJOR` mở. Một user verdict `APPROVED` kết thúc Phase 07 và
cho phép chạy Phase 08.

## 7. Unit Test Quality Contract

UT bắt buộc cho logic unit-testable mới/thay đổi và bug fix, trừ khi Test Plan/Plan/Task ghi `NO` với lý do hợp lệ và alternative test. UI-only markup, docs, generated code hoặc integration boundary có thể dùng component/integration/e2e test thay thế nhưng vẫn phải ghi applicability.

UT tốt phải:

- Fast, isolated, repeatable/deterministic theo khả năng của stack.
- Tập trung vào behavior/contract, không khóa implementation detail không cần thiết.
- Tên test thể hiện subject/scenario/expected behavior theo convention repo.
- Có cấu trúc Arrange–Act–Assert hoặc cấu trúc tương đương rõ ràng khi phù hợp.
- Dùng input nhỏ nhất đủ chứng minh behavior.
- Bao phủ success, invalid, boundary, failure/recovery và regression theo Task/Test Plan.
- Mock/stub ở boundary cần thiết; không mock chính logic đang kiểm tra.
- Assertion cụ thể, có khả năng fail khi behavior hỏng; không chỉ “không throw” nếu AC yêu cầu output/state.
- Không phụ thuộc network, database, clock, randomness hoặc global state thật nếu đó không phải mục tiêu integration test.
- Được review như production code về naming, simplicity và maintainability.

Bug fix nên có regression test chứng minh lỗi cũ khi khả thi. Không yêu cầu phá working tree hiện tại chỉ để tạo log đỏ; có thể dùng lịch sử, test thiết kế đúng failure mode hoặc bằng chứng reproduction được kiểm soát.

## 8. Coverage Contract

Coverage evidence khi tooling hỗ trợ gồm:

```text
COVERAGE TOOL/VERSION:
COMMAND:
SCOPE: whole project | changed code | package/module
POLICY: threshold | no-regression delta | approved baseline
STATEMENT/LINE:
BRANCH:
FUNCTION/METHOD:
PREVIOUS/DELTA nếu có:
REPORT PATH:
CRITICAL UNCOVERED LINES/BRANCHES:
RISK/RATIONALE:
EXCLUSIONS VÀ CĂN CỨ:
RESULT: PASS | FAIL | N/A
```

Quy tắc:

- Không dùng một % duy nhất làm bằng chứng test tốt.
- Ưu tiên xem changed/critical code, branch quan trọng và phần **chưa được cover**.
- Statement/line coverage không thay branch coverage khi code có decision path và tool hỗ trợ branch.
- Threshold/delta lấy từ Plan đã duyệt; thay đổi threshold/exclusion phải cập nhật Plan trước, không hạ để ép pass.
- Coverage không thay AC mapping, test review, assertion quality hoặc integration/runtime evidence.
- Với legacy coverage thấp, không bắt buộc sửa toàn repo trong một task; yêu cầu không regression và cải thiện changed code theo policy đã duyệt.
- Nếu coverage tool chưa có nhưng logic cần UT, task scaffold/required-check phải thiết lập tool trước acceptance hoặc xin quyết định cập nhật Plan.

## 9. Phase 08 — Final Verification

Phase 08 chạy **sau Phase 07 `APPROVED`** trên final head/fingerprint đã review.

Kiểm tra:

1. Chạy targeted UT và regression tests liên quan trên final state.
2. Không có failed test; skipped/quarantined test có lý do và không che AC.
3. Coverage policy/threshold/delta pass khi áp dụng.
4. Critical changed branches/behaviors được cover hoặc có accepted risk rõ.
5. Test files và AC/Test ID mapping đúng final implementation.
6. Test/coverage report khớp revision/fingerprint sau review correction.
7. Codex inspect report và chạy lại risk-based command ở Shared workspace.

Phase 08 evidence tối thiểu:

```text
UT EVIDENCE
- Final head/fingerprint:
- Test files và AC/Test ID mapping:
- Command:
- Passed/failed/skipped:
- Coverage metrics/policy/delta:
- Coverage report path:
- Critical uncovered branches/risk:
- Codex rerun:
- CODEX CHECK RESULT: PASS | FAIL | BLOCKED | N/A
- CODEX RECOMMENDATION:
- USER VERDICT: APPROVED | CHANGES_REQUESTED | BLOCKED | PENDING
```

Codex chỉ được ghi `RECOMMEND APPROVAL` sau khi evidence kỹ thuật đạt. Chỉ sau
user verdict `APPROVED` cho Phase 08 mới được đặt task `Verified`.

## 10. Phase 09 — Acceptance và traceability cuối

Codex không tự nghiệm thu. Codex chuẩn bị Phase 09 evidence package để người dùng review:

- Ghi rõ `SCOPE ID/ROOT`; package kết luận đúng scope, không suy ra acceptance cho scope khác.
- Phase 01, 03, 04 và 05 có record cùng user verdict tương ứng.
- Mỗi task áp dụng có Phase 07 và 08 inspect được.
- Full regression/build/runtime checks pass trên final revision.
- Coverage/quality policy không bị hạ hoặc exclusion mở rộng để ép pass.
- Mọi AC/critical risk map tới evidence cuối.

Thiếu record/evidence hoặc có scope impact chưa được xử lý thì Codex recommendation
phải là `BLOCKED` hoặc `CHANGES REQUIRED`. Phase 09 chỉ đạt khi người dùng ghi
verdict `APPROVED`; không suy ra PASS từ code hiện tại hay self-review của Codex.
Nghiệm thu cấp dự án là package tổng hợp các scope đã được approve, không thay
thế Phase 09 của từng scope.

## 11. Cơ sở kỹ thuật tham khảo

Workflow này áp dụng có chọn lọc các nguyên tắc ổn định từ:

- [OpenAI Docs — Build skills](https://learn.chatgpt.com/docs/build-skills): Skill giữ entrypoint gọn, route chi tiết theo phase qua references, dùng script cho thao tác cần tính xác định.
- [Google Engineering Practices — What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html): review design, functionality, complexity, tests, naming, comments, style, docs và context; test đi cùng production change; review không làm code health giảm.
- [Microsoft Learn — Unit testing best practices](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices): test fast/isolated/repeatable, readable, naming rõ, Arrange–Act–Assert và behavior-focused.
- [Google Testing Blog — Code Coverage Best Practices](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html): coverage là metric gián tiếp, không có threshold lý tưởng cho mọi sản phẩm; cần xem uncovered risk và new/changed code.
- [Coverage.py — Branch coverage measurement](https://coverage.readthedocs.io/en/7.12.0/branch.html): statement được chạy chưa chứng minh mọi decision destination đã được thực thi.

Không biến khuyến nghị của một stack thành luật cứng cho mọi công nghệ; Plan của dự án quyết định tool, threshold và alternative evidence phù hợp.
