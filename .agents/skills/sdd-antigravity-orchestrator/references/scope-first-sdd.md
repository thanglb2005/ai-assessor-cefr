# Scope-first SDD và cấu trúc tài liệu

Đọc reference này khi khởi tạo SDD, thêm feature/module, tách một SDD monolith,
đổi cấu trúc thư mục docs hoặc xác định scope cho một task. Đây là quy ước tổ
chức tài liệu; nó không thay đổi vai trò Codex/Antigravity hay quyền duyệt của
người dùng.

## 1. Nguyên tắc

SDD là **scope-first**: mỗi feature hoặc module có một scope root riêng và chạy
đầy đủ cùng một vòng:

```text
01 Requirement → [02 Research — optional] → 03 Specification → 04 Test Plan →
05 Plan & Task Readiness → 06 Implementation & Test →
07 Implementation Review → 08 Final Verification → 09 Acceptance
```

Không dùng một specification cấp repo làm nơi chứa tất cả requirement của mọi
feature. Khi thêm feature/module mới, tạo folder mới; không sửa các
specification đã duyệt của scope không bị ảnh hưởng chỉ để “đồng bộ”.

`AI_CONTEXT.md` có thể giữ context cấp repo. Nó không thay thế bộ tài liệu của
một scope.

Phase 01 ghi `RESEARCH MODE: RUN | SKIP`. Codex đề xuất theo uncertainty/risk,
nhưng người dùng chọn cùng verdict Phase 01. `SKIP` không đổi số phase: scope đi
thẳng từ Phase 01 sang Phase 03 và Status ghi lý do; không cần tạo file rỗng.

## 2. Cấu trúc đơn giản

Tên file có thể theo convention của repo, nhưng cấu trúc logic nên tương đương:

```text
AI_CONTEXT.md
docs/sdd/
├── features/
│   └── <feature-slug>/
│       ├── 01-requirement.md
│       ├── 02-research.md        # chỉ khi RESEARCH MODE: RUN
│       ├── 03-specification.md
│       ├── 04-test-plan.md
│       ├── 05-plan.md
│       ├── 06-tasks.md
│       ├── 07-status.md
│       ├── prompts/
│       ├── evidence/
│       └── reviews/
└── modules/
    └── <module-slug>/
        ├── 01-requirement.md
        ├── 02-research.md        # chỉ khi RESEARCH MODE: RUN
        ├── 03-specification.md
        ├── 04-test-plan.md
        ├── 05-plan.md
        ├── 06-tasks.md
        ├── 07-status.md
        ├── prompts/
        ├── evidence/
        └── reviews/
```

`features/` dành cho user-facing feature; `modules/` dành cho domain hoặc
technical module. Mỗi scope tự chứa requirement, research khi được chọn, specification,
test-plan, plan, tasks, status và mọi prompt/evidence/review của nó. Không tạo
thêm tầng tài liệu trung tâm mặc định; tài liệu cấp repo chỉ tồn tại khi dự án
thật sự cần và không chứa requirement riêng của scope.

`Implement` là thay đổi trong source code, không phải một file markdown bắt
buộc: `06-tasks.md` điều khiển việc triển khai, prompt nằm trong `prompts/`, kết
quả chạy/test nằm trong `evidence/`, review nằm trong `reviews/`, còn
`07-status.md` ghi phase hiện tại.

`07-status.md` là ledger của toàn scope, không chỉ là output của Phase 07.
Review attempts của Phase 07 nằm trong `reviews/`; Final Verification và
Acceptance records của Phase 08/09 nằm trong `evidence/` và được link từ Status.

Lite/Fast Path có thể gộp các file đánh số thành `PROJECT_SDD.md`, nhưng bundle
phải nằm bên trong folder feature/module, được điền tuần tự theo checkpoint và
vẫn giữ đúng thứ tự trên.

## 3. Metadata và traceability local

`AI_CONTEXT.md` chỉ giữ context cấp repo, command ổn định và đường dẫn docs. Mỗi
feature/module folder là source of truth duy nhất cho scope đó; `prompts/`,
`evidence/` và `reviews/` lưu ngay trong scope để không trộn record.

Mỗi `01-requirement.md` hoặc bundle phải ghi tối thiểu:

```text
SCOPE ID: <stable-id>
SCOPE TYPE: feature | module
SCOPE ROOT: <path>
OWNER:
LIFECYCLE: proposed | active | verified | archived
RELATED SCOPES: <path/IDs hoặc KHÔNG CÓ>
RESEARCH MODE: RUN | SKIP — <user decision/rationale>
```

Dùng ID có namespace để tránh collision khi nhiều scope cùng có `FR-001`:
`<SCOPE_KEY>-FR-001`, `<SCOPE_KEY>-AC-001`, `<SCOPE_KEY>-TASK-001`,
`<SCOPE_KEY>-TEST-001`. Khi migrate tài liệu cũ, giữ nguyên ID đã được dùng và
ghi mapping ngay trong scope mới hoặc migration note; không đổi ID chỉ vì đổi
folder.

Version, approval và evidence được quản lý trong scope root. `07-status.md` là
trạng thái vận hành hiện tại của scope. Không ghi `USER VERDICT: APPROVED` thay
người dùng.

Mọi checkpoint dùng cùng trạng thái:

```text
DRAFT | IN_REVIEW | CHANGES_REQUIRED | APPROVED | BLOCKED
```

## 4. Chọn scope cho yêu cầu mới

1. Đọc `AI_CONTEXT.md` và xác định feature/module liên quan.
2. Nếu là feature/module mới, tạo `docs/sdd/features/<slug>/` hoặc
   `docs/sdd/modules/<slug>/` và bắt đầu bằng `01-requirement.md`. Sau Phase 01
   `APPROVED`, tạo Research trước Specification nếu `RESEARCH MODE: RUN`; nếu
   `SKIP`, ghi skip record trong Status và tạo Specification. Sau Phase 03 tạo
   Test Plan; sau Phase 04 tạo Plan + draft Tasks. Các thư mục record local có
   thể tạo khi phát sinh prompt/evidence/review đầu tiên.
3. Nếu là scope hiện có, đọc `07-status.md` và tiếp tục từ phase gần nhất có
   verdict; không đọc toàn bộ docs của scope khác theo mặc định.
4. Đọc các file liên quan trực tiếp trong scope khác nếu có dependency; chỉ sửa
   chúng khi requirement/impact đã được xác định và user approve.
5. Nếu chưa rõ nên thuộc feature hay module nào, dừng ở Requirement và hỏi user;
   không tự gộp requirement vào một scope hiện có.

### Thay đổi liên quan nhiều scope

Không cần tạo thêm loại folder mới. Chọn scope chính, ghi rõ `RELATED SCOPES`
trong Requirement/Plan và các file bị ảnh hưởng trong Tasks. Nếu thay đổi làm
thay đổi behavior của scope khác, scope đó phải được re-verify từ phase sớm nhất
bị ảnh hưởng; nếu impact chưa rõ thì trả `BLOCKED` để user quyết định.

## 5. Invalidation và lifecycle

Thay đổi trong scope chỉ làm stale các artifact phía sau của scope đó. Nếu
Requirement/Plan ghi rõ ảnh hưởng tới scope khác, chỉ scope liên quan phải
re-verify từ phase sớm nhất bị ảnh hưởng; không làm stale toàn bộ repo.

Khi một scope hoàn tất, giữ nguyên folder và Status/evidence để audit. Chỉ archive
khi repo convention hoặc user yêu cầu; không xóa tài liệu cũ để “dọn” docs.

## 6. Tách SDD monolith hiện có

Migration phải incremental:

1. Giữ tài liệu cũ làm legacy source trong lúc chưa có mapping.
2. Phân loại requirement/task theo feature hoặc module thực tế.
3. Tạo từng scope folder, chuyển nội dung tương ứng và giữ ID/version/approval;
   phần chưa phân loại giữ ở tài liệu legacy.
4. Cập nhật `AI_CONTEXT.md` với path mới và artifact cần review lại. Không điền
   approval mới nếu user chưa duyệt.
5. Chỉ đánh dấu tài liệu cũ là legacy/superseded sau khi mapping và user verdict
   cho migration đã rõ; feature mới luôn đi vào scope folder riêng.

Không cần tách toàn bộ repo trước khi bắt đầu feature mới. Có thể tạo scope mới
cho feature đó và dẫn chiếu tài liệu legacy, rồi migrate phần còn lại theo từng
bounded change.

## 7. Handoff và evidence

Prompt/evidence luôn ghi `SCOPE ID`, `SCOPE ROOT`, artifact versions và các scope
liên quan. Shared workspace chỉ được sửa vùng source/SDD đã nêu; Separated
workspace chỉ cần bàn giao scope root cùng tài liệu liên quan trực tiếp. Review
được giới hạn ở active scope và impact đã khai báo.

Phase review package và Review Record dùng scope-qualified subject. Phase 09 của
một scope chỉ kết luận scope đó; nghiệm thu cấp dự án là package tổng hợp các
scope đã được người dùng nghiệm thu, không thay thế Phase 09 local.
