# Fast Path cho scope nhỏ và ít rủi ro

Đọc reference này khi một **scope** nhỏ, người dùng muốn bắt đầu nhanh, hoặc
nghi thức Standard gây tốn công hơn giá trị kiểm soát. Fast Path giữ nguyên SDD
và mô hình Codex–Antigravity, nhưng gộp tài liệu, phê duyệt và trạng thái ở mức
tối thiểu có thể kiểm tra được. Đọc [scope-first-sdd.md](scope-first-sdd.md)
trước để chọn `features/<slug>`, `modules/<slug>` hoặc scope phù hợp.

## 1. Fast Path không phải bỏ SDD

Fast Path vẫn bắt buộc:

- Mục tiêu, in scope và out of scope rõ.
- Requirement/Acceptance Criteria quan sát được.
- Hướng triển khai và required checks phù hợp.
- Task đủ nhỏ, có phạm vi file và cách kiểm tra.
- Antigravity trả diff/report; Codex review bằng thay đổi thực tế.
- Phase 01–09 có record/evidence tương xứng; Phase 07 kiểm tra implementation, Clean Code và test quality trong một review cycle.
- Codex self-review/review và đưa recommendation; người dùng là final reviewer, approve tại checkpoint trước khi đi tiếp.
- UT/coverage applicability được quyết định trong Test Plan/Task và chạy lại trên final reviewed state.
- Phase 09 đối chiếu Definition of Done trước khi tuyên bố hoàn thành.

Được phép nén:

- Requirement, optional Research, Specification, Test Plan và Plan vào một
  `PROJECT_SDD.md` **bên trong scope root**, không phải ở repo root.
- Test Plan thành checklist có liên kết AC thay vì ma trận dài.
- Status thành một block ngắn cập nhật sau handoff/review.
- Verification/Review Record thành block một dòng/checklist miễn vẫn truy được evidence.
- Prompt Antigravity còn các trường bắt buộc, bỏ trường không áp dụng thay vì để placeholder dài.

Nén file không có nghĩa chuẩn bị trước mọi artifact. Mỗi section chỉ được tạo
theo transition của phase; không được vượt checkpoint đang chờ user verdict.

## 2. Điều kiện chọn Fast Path

Codex có thể đề xuất hoặc tự chọn Fast Path khi mọi điều sau đều đúng:

- Prototype, bài tập, demo, tool nội bộ nhỏ hoặc tính năng độc lập ít rủi ro.
- Shared workspace hoặc handoff đơn giản và inspect được actual diff.
- Không có production mutation trong task hiện tại.
- Không có payment, dữ liệu nhạy cảm, quyền truy cập phức tạp, migration khó hoàn tác hoặc yêu cầu compliance đáng kể.
- Hành vi chính đủ rõ để viết AC kiểm tra được.
- Phạm vi có thể chia thành các task nhỏ cho một vòng implement–review.

Không dùng hoặc phải nâng cấp khỏi Fast Path khi có một trong các dấu hiệu:

- Deploy/production, payment, auth/phân quyền quan trọng, PII/secret hoặc thay đổi schema/migration.
- Nhiều service/repo/team, separated workspace phức tạp hoặc dependency bên ngoài chưa ổn định.
- Quyết định kiến trúc ảnh hưởng dài hạn, chi phí hosting hoặc khả năng phục hồi.
- Scope tăng mạnh, AC liên tục thay đổi hoặc hai lần correction thất bại cùng nguyên nhân.
- Người dùng yêu cầu audit trail/approval riêng cho từng artifact.

Khi nâng cấp, giữ lại ID/AC/task đã có; tách bundle trong scope sang cấu trúc
Standard nếu cần, ghi artifact nào `CHANGES_REQUIRED` và tiếp tục từ phase sớm
nhất bị ảnh hưởng. Nếu scope mới liên quan scope khác, ghi rõ trong Requirement
và Tasks; không nối thêm requirement vào bundle của scope cũ.

## 3. Gói SDD tối thiểu trong một scope

Fast Path mặc định dùng:

```text
AI_CONTEXT.md
docs/sdd/<kind>/<scope-slug>/PROJECT_SDD.md
README.md
```

`<kind>` là `features` hoặc `modules`.

Prompt, evidence và Review Record của Fast Path đặt cạnh bundle trong các thư mục
con `prompts/`, `evidence/`, `reviews/` của scope nếu cần lưu thành file.

`PROJECT_SDD.md` tối thiểu:

```text
# 01 — Requirement
SCOPE ID/ROOT/TYPE:
Mục tiêu:
Người dùng/hành trình chính:
In scope:
Out of scope:
Ràng buộc và giả định:
Research mode: RUN | SKIP — user decision/rationale:
Status/User verdict: DRAFT | IN_REVIEW | APPROVED | CHANGES_REQUIRED | BLOCKED

# 02 — Research (optional)
Mode/status: RUN | SKIPPED
Nguồn/context đã xem:
Finding/constraint/risk:
Decision hoặc skip rationale:

# 03 — Specification
FR-*:
AC-*:
Failure/boundary quan trọng:
Codex check/recommendation + User verdict:
Status: DRAFT | IN_REVIEW | APPROVED | CHANGES_REQUIRED | BLOCKED

# 04 — Test Plan
Test ID/Requirement/AC/scenario/expected result:
UT/coverage applicability:
Codex check/recommendation + User verdict:
Status: DRAFT | IN_REVIEW | APPROVED | CHANGES_REQUIRED | BLOCKED

# 05 — Plan & Task Readiness
Kiến trúc/data flow chính:
Convention/dependency:
Lệnh chạy và required checks:
Clean Code/UT/coverage policy:
Rủi ro/trade-off:
Codex check/recommendation + User verdict:
Status: DRAFT | IN_REVIEW | APPROVED | CHANGES_REQUIRED | BLOCKED

# 06 — Tasks / Implementation & Test
Task ID/status/scope/file/AC/check:
UT required/rationale + test checklist liên kết AC:
Coverage command/policy/report:
Implementation report/evidence:

# 07 — Implementation Review
Attempt/status/findings/resolution:
Codex check/recommendation + User verdict:

# 08 — Final Verification
Final fingerprint/checks/coverage:
Codex check/recommendation + User verdict:

# 09 — Acceptance
AC/Definition of Done evidence:
Codex recommendation + User verdict:

# Status
Mode: Fast
Scope ID/root:
Current phase/task/prompt/attempt:
Base revision:
WORKSPACE FINGERPRINT:
Fingerprint algorithm/metadata files/exclusions:
Last checks:
Open issue:
Next action:
```

Các section có thể nằm trong cùng một file, nhưng được trình duyệt tuần tự theo
Phase 01–09. Checkpoint cần user verdict nằm ở Phase 01, 03, 04, 05, 07, 08 và
09. Phase 02 chỉ được review cùng Phase 03 khi `RUN`; nếu `SKIP`, một dòng skip
record trong bundle là đủ. Phase 06 được review trong Phase 07.
Self-review của Codex không thay user approval.

## 4. Vòng vận hành Fast

1. Khảo sát repo, `AI_CONTEXT.md`, dirty worktree và chọn/tạo một scope root dưới `features/` hoặc `modules/`.
2. Soạn Phase 01 Requirement, self-review và dừng để người dùng duyệt phạm vi.
3. Sau Phase 01 `APPROVED`, nếu Research là `RUN` thì soạn Phase 02 trước; nếu
   `SKIP` thì ghi skip record. Sau đó soạn Phase 03 Specification, self-review
   và dừng chờ user verdict cho Phase 03.
4. Sau Phase 03 `APPROVED`, soạn Phase 04 Test Plan, self-review và dừng chờ user verdict.
5. Sau Phase 04 `APPROVED`, soạn Phase 05 Plan + draft Task, self-review và dừng chờ user verdict.
6. Sau Phase 05 `APPROVED`, phát hành prompt và Antigravity thực hiện Phase 06 Implementation & Test.
7. Codex thực hiện Phase 07: verify evidence, review code/test, phát hành correction khi cần và re-review trong cùng cycle. Người dùng đưa một verdict cuối.
8. Sau Phase 07 `APPROVED`, chạy Phase 08 Final Verification trên final fingerprint và trình người dùng chấp nhận task.
9. Khi mọi task đã verified, trình Phase 09 Acceptance để người dùng nghiệm thu scope.

## 5. Prompt Fast tối thiểu

Không bỏ các trường sau:

```text
PROMPT ID / TASK ID / ATTEMPT
SCOPE ID / SCOPE ROOT / SCOPE TYPE
HANDOFF MODE / REPO ROOT / BASE REVISION / WORKSPACE FINGERPRINT
FINGERPRINT ALGORITHM / METADATA FILES / EXCLUSIONS
ARTIFACT VERSION hoặc SDD bundle version đã duyệt
APPROVED PHASE RECORDS: 01 / 03 / 04 / 05
RESEARCH MODE + PATH/DECISIONS hoặc SKIP RECORD
MỤC TIÊU
CONTEXT/AC PHẢI ĐỌC
IN SCOPE / OUT OF SCOPE
FILE/KHU VỰC ĐƯỢC PHÉP SỬA
QUYỀN LOCAL / EXTERNAL ACTION
CHECKS VÀ BẰNG CHỨNG BẮT BUỘC
UT REQUIRED/RATIONALE + COVERAGE POLICY
CLEAN CODE SELF-REVIEW
ĐỊNH DẠNG REPORT
```

Các mục không áp dụng ghi một dòng `KHÔNG CÓ`; không chép lại toàn bộ SDD vào prompt.

## 6. Fingerprint trong Fast Path

Nếu có Python 3, chạy helper của Skill:

```text
python3 <skill-root>/scripts/workspace_fingerprint.py --root <repo-root> --metadata-file <scope-root>/PROJECT_SDD.md
```

Tạo bundle và điền Status/metadata options trước khi hash. Nếu lưu prompt/evidence riêng có field fingerprint, tạo file trước và thêm đúng path bằng `--metadata-file` lặp lại. Ghi `base_revision` và `fingerprint`, rồi chạy lại cùng options cộng `--expect <fingerprint>`. Chỉ field `WORKSPACE FINGERPRINT:` trong các file metadata đã chọn được chuẩn hóa; source và file khác được hash nguyên nội dung. Xem handoff reference cho submodule/exclusion; baseline `v1` phải được xác minh lại và phát hành bằng `sdd-workspace-v2`.

Nếu helper không chạy được, ghi base SHA cùng `git status --short` và nêu rõ `Fingerprint unavailable`; Fast Path không được giả vờ có fingerprint hợp lệ.

## 7. Review và Acceptance theo rủi ro

Fast Path không đồng nghĩa chạy mọi check có thể có. Codex chọn check nhỏ nhất đủ chứng minh AC và chống regression:

- Luôn xem actual diff và thay đổi ngoài scope.
- Luôn chạy targeted tests/checks ghi trong task.
- Luôn review Clean Code/test quality theo phần thay đổi và ghi finding bắt buộc.
- Logic unit-testable/bug fix phải có UT trừ khi Plan/Task ghi ngoại lệ hợp lệ; coverage phải có evidence khi policy áp dụng.
- Sau review/correction, luôn chạy lại final-state UT/coverage ở Phase 08; không tái sử dụng kết quả revision cũ.
- Chạy lint/typecheck/build khi thay đổi có thể ảnh hưởng toàn ứng dụng hoặc đây là required check đã duyệt.
- Browser QA cho critical journey/UI thay đổi; kiểm tra Console/Network khi liên quan.
- Phase 09 có thể dùng package build + test + critical journey compact với dự án rất nhỏ, nhưng phải ghi kết quả theo AC/DoD.

Nếu bằng chứng không đủ, Codex đề xuất nâng mức verification thay vì chấp nhận theo report. Mọi checkpoint áp dụng vẫn cần user verdict.
