# Bootstrap và tạo SDD

Đọc reference này khi repo trống/đã scaffold, thiếu tài liệu SDD, hoặc yêu cầu thay đổi đáng kể. Trước khi tạo artifact, đọc [scope-first-sdd.md](scope-first-sdd.md) để xác định scope root; quy trình bên dưới áp dụng cho một scope, không mặc định cho toàn bộ repo.

## 1. Khảo sát ban đầu

Phân loại bằng thao tác chỉ đọc:

- `Empty`: chưa có file dự án có ý nghĩa.
- `Scaffolded`: có nền tảng nhưng chưa có tính năng chính.
- `Existing`: có source code và hành vi hiện tại.

Với repo có sẵn, kiểm tra cấu trúc, README, hướng dẫn agent, Git status, manifest, scripts, test, build, kiến trúc và convention. Không scaffold chồng lên code cũ.

## 2. Requirement

Thu thập hoặc suy ra:

```text
Tên dự án:
Scope ID/type/root:
Mục tiêu trong một câu:
Người dùng chính:
Hành trình chính:
In scope:
Out of scope:
Thiết kế/tài liệu/API tham chiếu:
Nền tảng và môi trường:
Ràng buộc kỹ thuật:
Bảo mật/quyền riêng tư:
Thời hạn:
Required checks và coverage:
Mục tiêu deploy:
Depends on/Impacts:
Research mode: RUN | SKIP — user decision/rationale:
Chế độ tài liệu: Lite | Standard
Mức vận hành: Fast | Standard | Strict
Chế độ bàn giao: Shared | Separated workspace
Câu hỏi còn mở:
Giả định:
```

Tìm fact trong repo trước khi hỏi. Gom các câu hỏi độc lập thành một nhóm nhỏ. Không đoán hành vi sản phẩm, quyền riêng tư hoặc lựa chọn khó hoàn tác. Phase 01 đạt khi người dùng duyệt Requirement và phạm vi.

## 3. Chế độ tài liệu, scope và mức vận hành

Hai lựa chọn độc lập:

- **Chế độ tài liệu** quyết định artifact được gộp (`Lite`) hay tách file (`Standard`).
- **Mức vận hành** quyết định độ chặt của approval, baseline, handoff và verification (`Fast | Standard | Strict`).

`Fast` dùng cho một scope nhỏ, ít rủi ro và thường đi với Lite; đọc fast-path.md trước khi tạo artifact. `Standard` là mặc định. `Strict` dùng khi separated workspace, production, dữ liệu/quyền nhạy cảm, migration khó hoàn tác hoặc cần audit trail chặt. Không tự chọn Fast chỉ vì người dùng muốn ít tài liệu nếu risk yêu cầu Standard/Strict.

Mặc định repo dùng topology:

```text
AI_CONTEXT.md
docs/sdd/
├── features/<feature-slug>/
│   ├── 01-requirement.md
│   ├── 02-research.md              # chỉ khi Research mode: RUN
│   ├── 03-specification.md
│   ├── 04-test-plan.md
│   ├── 05-plan.md
│   ├── 06-tasks.md
│   ├── 07-status.md
│   ├── prompts/
│   ├── evidence/
│   └── reviews/
└── modules/<module-slug>/
    ├── 01-requirement.md
    ├── 02-research.md              # chỉ khi Research mode: RUN
    ├── 03-specification.md
    ├── 04-test-plan.md
    ├── 05-plan.md
    ├── 06-tasks.md
    ├── 07-status.md
    ├── prompts/
    ├── evidence/
    └── reviews/
```

Mỗi feature/module tự chứa toàn bộ quy trình và record của nó. Không đặt
requirement của nhiều scope vào một file chung hoặc tạo thêm tầng tài liệu trung
tâm mặc định. Prompt, evidence và Review Record nằm trong scope tương ứng.

### Lite

Dùng cho prototype, bài học hoặc dự án nhỏ, ít rủi ro:

```text
AI_CONTEXT.md
docs/sdd/<kind>/<scope-slug>/PROJECT_SDD.md  # local bundle của một scope
README.md
```

`PROJECT_SDD.md` Lite vẫn phải chứa đủ section Requirement, Specification, Test
Plan, Plan, Tasks và Status của **một scope**; section Research chỉ có nội dung
khi `RUN`, còn `SKIP` dùng một dòng skip record. Không tạo một
bundle Lite chung ở repo root chỉ để chứa nhiều feature. Các section được điền
tuần tự theo checkpoint; bundle không cho phép vượt qua phase cần user approval.

### Standard

Dùng cho dự án nhóm, dài hạn, nhiều tích hợp hoặc production:

```text
AI_CONTEXT.md
README.md
docs/sdd/<kind>/<scope-slug>/01-requirement.md
docs/sdd/<kind>/<scope-slug>/02-research.md  # optional; chỉ tạo khi RUN
docs/sdd/<kind>/<scope-slug>/03-specification.md
docs/sdd/<kind>/<scope-slug>/04-test-plan.md
docs/sdd/<kind>/<scope-slug>/05-plan.md
docs/sdd/<kind>/<scope-slug>/06-tasks.md
docs/sdd/<kind>/<scope-slug>/07-status.md
```

Không tạo cấu trúc tài liệu trùng convention đã có.

## 4. AI_CONTEXT.md tối thiểu

Giữ file này ngắn:

```text
Mục tiêu và phạm vi dự án
Scope active, phase và đường dẫn Status hiện tại
Route/contract/lệnh ổn định
Phase model 01–09, Clean Code/UT/coverage policy và evidence path
Guardrail kỹ thuật, bảo mật và repository
Vai trò Codex/Antigravity và handoff mode
Definition of Done tham chiếu
Version và ngày cập nhật
```

## 5. Phase 01 — Requirement

Ghi mục tiêu, user, user journey, in scope, out of scope, ràng buộc, câu hỏi
mở, Acceptance Criteria sơ bộ và lựa chọn `RESEARCH MODE: RUN | SKIP`. Codex
đề xuất dựa trên uncertainty/risk, nhưng Phase 01 đạt khi người dùng duyệt phạm
vi cùng lựa chọn này.

## 6. Phase 02 — Research

Phase 02 là optional cho từng scope:

- Đề xuất `RUN` khi còn domain/technical uncertainty đáng kể, dependency/API
  chưa rõ, có reference project cần khảo sát hoặc quyết định khó hoàn tác cần
  evidence.
- Đề xuất `SKIP` khi Requirement, constraint và code/context hiện tại đã đủ để
  viết Specification testable mà không cần khảo sát riêng.
- Người dùng chọn `RUN | SKIP` trong Phase 01. Codex không tự ghi đè lựa chọn.

Nếu `RUN`, tạo `02-research.md` và ghi nghiên cứu cần thiết cho scope:

- Domain/business context và các assumption cần xác nhận.
- Tech/architecture/API/reference repo khi có liên quan.
- Convention, constraint, dependency và risk phát hiện được.
- Kết luận `ADOPT | ADAPT | INSPIRE | REJECT | OPEN` khi dùng reference.

Research giải thích cơ sở quyết định, không tự tạo requirement hoặc thay thế
Specification. Research không có checkpoint riêng; Codex trình nó cùng
Specification ở Phase 03.

Nếu `SKIP`, không tạo `02-research.md`; ghi `PHASE 02: SKIPPED — <user
decision/rationale>` trong Requirement/Status hoặc bundle Lite rồi chuyển sang
Phase 03. `SKIP` không che uncertainty: nếu Specification vẫn còn quyết định
quan trọng `OPEN`, Phase 03 là `BLOCKED` cho tới khi user quyết định, chấp nhận
assumption hoặc bật lại Research.

## 7. Phase 03 — Specification

Mô tả sản phẩm phải làm gì:

- Scope ID/type/root, mục tiêu, người dùng, user stories.
- In scope/out of scope.
- Functional Requirement có ID `FR-*`.
- Input/output, validation và chuẩn hóa.
- Loading/success/empty/error/recovery.
- Boundary và failure behavior.
- Security/privacy/accessibility/responsive khi liên quan.
- Acceptance Criteria quan sát được có ID `AC-*`.
- Giả định, dependency/impact và câu hỏi mở.

Phase 03 đạt khi hành trình chính và lỗi quan trọng đã rõ, AC kiểm tra được và người dùng approve.

Codex self-review Specification cùng Research nếu `RUN`, hoặc kiểm tra skip
record nếu `SKIP`, rồi trình evidence/recommendation.
Codex không tự ghi user verdict hoặc tạo Test Plan trước Phase 03
`APPROVED` cho đúng artifact version.

## 8. Phase 04 — Test Plan

Test Plan đi trước Plan để xác định cách kiểm chứng AC:

- Test ID, Requirement/AC, scenario, expected result và test level.
- Success, invalid, boundary, failure/recovery, regression và user-visible checks.
- UT/coverage applicability, command, policy và alternative evidence nếu N/A.

Codex self-review Test Plan và trình evidence/recommendation. Phase 04 chỉ đạt
sau user verdict `APPROVED`; khi đó mới tạo Plan.

## 9. Phase 05 — Plan & Task Readiness

Mô tả cách triển khai Specification:

- Công nghệ, runtime, package manager và lý do chọn.
- Kiến trúc, module boundary và data flow.
- State, persistence, API/storage/error contract.
- Validation, security, accessibility, recovery.
- Chiến lược automated/manual test.
- Clean Code/code review policy, script và required checks.
- Unit Test applicability, test level/command và coverage tool/policy.
- Rủi ro, trade-off và giả định.

Với repo trống, thêm directory structure, dependency policy, environment/`.env.example`, `.gitignore`, README, lint, typecheck, test, build và quyết định có khởi tạo Git hay không. Người dùng duyệt lựa chọn ảnh hưởng đáng kể đến chi phí, hosting, bảo trì, bảo mật hoặc kiến trúc.

Coverage policy không dùng một con số mặc định cho mọi dự án. Plan xác định threshold hoặc no-regression delta theo criticality, changed code và khả năng đo của stack; đồng thời yêu cầu xem critical uncovered branches. Nếu UT/coverage không áp dụng, ghi rationale và alternative verification.

Codex tạo draft Task sau Plan, rồi self-review Plan + Task readiness và trình
evidence/recommendation. Phase 05 chỉ đạt và prompt chỉ được phát hành sau user
verdict `APPROVED` cho đúng Plan/Task version.

## 10. Tasks và Prompt readiness — thuộc Phase 05

Tạo task theo phụ thuộc: tài liệu/assets → scaffold/required checks → domain/validation → data/integration → state/navigation → UI → accessibility/responsive/error → verification/docs.

Mẫu task:

```text
Scope ID/root:
Task ID và tiêu đề:
Trạng thái:
Requirement/AC:
Mục tiêu:
In scope/Out of scope:
File/khu vực được phép sửa:
Phụ thuộc:
Implementation notes:
UT REQUIRED: YES | NO — rationale:
Test IDs/AC mapping:
Coverage command/policy/report:
Clean Code/static review checks:
Kiểm tra và bằng chứng bắt buộc:
Browser QA nếu có:
Owner: Antigravity
Reviewer: Codex
Final reviewer: User
```

Definition of Ready:

- Liên kết yêu cầu đã duyệt trong đúng scope root.
- Mục tiêu và phạm vi không mơ hồ.
- Input/phụ thuộc có sẵn.
- Quyết định kỹ thuật quan trọng đã duyệt.
- Kiểm tra và bằng chứng đã ghi rõ.
- UT/coverage applicability và Clean Code review checks đã ghi rõ.
- Đủ nhỏ cho một vòng implement–review.

Codex self-review Definition of Ready và trình Phase 05 evidence/recommendation.
Task chỉ chuyển `In progress` và prompt chỉ được phát hành sau user verdict
`APPROVED` tại Phase 05.

Test Plan dùng ma trận trong `04-test-plan.md`:

```text
Test ID | Requirement/AC | Kịch bản | Kết quả mong đợi | Cấp test | Coverage/risk | Trạng thái
```

Bao phủ success, invalid, boundary, failure, retry, repeated action, security,
accessibility và responsive khi phù hợp. Logic unit-testable mới/thay đổi và bug
fix mặc định cần UT; ngoại lệ phải có rationale và alternative test trong
Test Plan/Task.

## 11. Version và phê duyệt

Mỗi artifact/section đã duyệt ghi:

```text
SCOPE ID/ROOT:
Version:
STATUS: DRAFT | IN_REVIEW | CHANGES_REQUIRED | APPROVED | BLOCKED
APPROVED BY:
APPROVED AT:
Supersedes:
```

`Approved by` tại checkpoint phải là người dùng. Codex có thể ghi `Checked by: Codex` và recommendation nhưng không tự điền user verdict.

Thay đổi quan trọng làm các artifact và Phase Record phía sau của scope đó thành
`CHANGES_REQUIRED`/stale. Cập nhật và review lại theo thứ tự Phase 01
Requirement → Phase 02 Research khi `RUN` → Phase 03 Specification → Phase 04 Test Plan →
Phase 05 Plan & Task Readiness trước khi phát hành prompt mới.
