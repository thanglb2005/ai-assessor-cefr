# Prompt, bàn giao và review Antigravity

Đọc reference này trước khi Codex giao task, review báo cáo hoặc phát hành prompt sửa.

## 1. Handoff mode

- `Shared workspace`: hai model cùng repo; Codex đọc actual diff và chạy lại targeted/risk-based check.
- `Separated workspace`: chuyển baseline bất biến mới nhất gồm SDD của scope active và tài liệu của related scope thật sự cần thiết sang Antigravity bằng commit/ref, bundle, patch hoặc archive có checksum; Antigravity trả patch/commit, base/head revision, log và bằng chứng truy cập được.

Không nghiệm thu separated workspace chỉ từ bản tóm tắt.

## 2. Issuance transaction

Trước khi đưa prompt cho người dùng, dùng helper xác định thay vì tự nghĩ thuật toán hash:

```text
python3 <skill-root>/scripts/workspace_fingerprint.py --root <repo-root> --metadata-file <scope-root>/07-status.md --metadata-file <scope-root>/prompts/<prompt>.md
python3 <skill-root>/scripts/workspace_fingerprint.py --root <repo-root> --metadata-file <scope-root>/07-status.md --metadata-file <scope-root>/prompts/<prompt>.md --expect <fingerprint>
```

Helper `sdd-workspace-v2` bao phủ base revision, Git index, nội dung tracked/untracked không bị ignore và executable/symlink state. Submodule đã initialized được hash đệ quy, gồm HEAD và nội dung working tree; nếu gặp thư mục submodule không inspect được, helper báo lỗi và không tự tải/init. Không có Git thì helper tạo manifest, bỏ các thư mục dependency/generated phổ biến.

Mặc định mọi file được hash nguyên nội dung. Chỉ field `WORKSPACE FINGERPRINT:` trong file `.md`/`.txt` được chỉ định bằng `--metadata-file` mới được chuẩn hóa thành `<SELF>`. Path phải tương đối từ repo root, là file thật đã tồn tại trong manifest, không dùng symlink, không bị ignore/exclude. Chọn đúng file Status/prompt/evidence cần ghi fingerprint; không chọn source, fixture hay tài liệu sản phẩm để né thay đổi. Các field khác vẫn được hash. Ghi danh sách metadata trước khi tính hash và dùng đúng danh sách khi `--expect`.

Chỉ dùng `--exclude <glob>` cho output đã được Plan xác định là không thuộc baseline; ghi các glob vào Status/prompt. Option áp dụng cho entry của repo root: có thể loại cả path submodule, nhưng không loại riêng file bên trong submodule; nội dung submodule được hash nguyên trạng thái theo quy tắc Git ignore của nó, không kế thừa metadata/exclusion của repo cha. Baseline `v1` không tương thích: xác minh lại state và phát hành fingerprint `v2`, không dùng hash cũ làm evidence mới.

Trình tự Standard/Strict:

1. Tạo Prompt ID, Task ID, `SCOPE ID/ROOT`, attempt, artifact versions và base revision.
2. Lưu file prompt và Tasks/Status của scope active, đặt task `In progress`, `Next action = Send prompt`, hoàn tất danh sách metadata/exclusion và tạm đặt fingerprint thành `<SELF>`.
3. Chạy helper với đúng `--metadata-file`/`--exclude` đã ghi, lưu đúng `base_revision`, `fingerprint` vào Status/prompt.
4. Chạy helper với `--expect` để xác nhận không đổi.
5. Separated mode: tạo/tham chiếu inbound baseline bất biến.
6. Chỉ sau đó mới bàn giao baseline và prompt.

Fast Path Shared workspace dùng cùng helper nhưng có thể ghi issuance trong một Status block ngắn. Không tạo archive/checksum hoặc approval record riêng nếu task không cần. Nếu helper không khả dụng, ghi `Fingerprint unavailable` cùng base SHA và `git status --short`; chỉ tiếp tục Fast khi actual diff vẫn inspect được và risk thấp. Standard/Strict không được bỏ fingerprint mà không ghi blocker/fallback được duyệt.

## 3. Mẫu prompt triển khai

```text
PROMPT ID: <project>-<task>-A<attempt>
TASK ID(S):
SCOPE ID/TYPE/ROOT:
ATTEMPT:
OPERATING MODE: Fast | Standard | Strict
HANDOFF MODE: Shared | Separated workspace
INBOUND BASELINE: <shared | ref/bundle/patch/archive + checksum>
REPO ROOT:
BASE REVISION: <SHA | no commits | Git not initialized>
WORKSPACE FINGERPRINT:
FINGERPRINT ALGORITHM: sdd-workspace-v2
FINGERPRINT METADATA FILES: <exact repo-relative paths dùng với --metadata-file>
FINGERPRINT EXCLUSIONS: <glob đã duyệt hoặc KHÔNG CÓ>
APPROVED ARTIFACT VERSIONS:
APPROVED PHASE RECORDS: 01 Requirement / 03 Specification / 04 Test Plan / 05 Plan & Task Readiness
RESEARCH MODE/RECORD: <RUN + path/version | SKIP + approved rationale>
DIRECT DEPENDENCY/IMPACT SCOPES: <scope IDs hoặc KHÔNG CÓ>

ROLE
Bạn là Antigravity, implementation agent. Chỉ làm trong prompt này.

CONTEXT PHẢI ĐỌC
- AI_CONTEXT:
- Active scope Requirement/Specification/AC:
- Active scope Research nếu `RUN`, hoặc skip record:
- Active scope Test Plan:
- Active scope Plan:
- Active scope Task:
- Related scope/document nếu có:
- Source/design/API liên quan:

MỤC TIÊU
<Một kết quả cụ thể, quan sát được>

IN SCOPE
- ...

OUT OF SCOPE
- ...

FILE/KHU VỰC ĐƯỢC PHÉP SỬA
- ...

YÊU CẦU VÀ EDGE CASE
- ...

MÔI TRƯỜNG
- Runtime/tool versions:
- Package manager:
- Setup/prerequisite:

THAO TÁC LOCAL ĐƯỢC PHÉP
- <dependency install/generator/commit cụ thể hoặc KHÔNG CÓ>

EXTERNAL ACTION ĐƯỢC NGƯỜI DÙNG CHO PHÉP
- <push/deploy/external action cụ thể hoặc KHÔNG CÓ>

QUY TẮC
- Bảo toàn thay đổi ngoài phạm vi của người dùng.
- Không sửa SDD đã duyệt hoặc mở rộng scope; không sửa scope/docs khác ngoài vùng được prompt cho phép.
- Nếu phát hiện impact sang scope khác chưa được khai báo, trả `BLOCKED` và không tự mở rộng task.
- Prompt không ghi đè Requirement/Specification/Test Plan/Plan/Task.
- Không init Git, commit, cài dependency hoặc chạy generator nếu không được phép.
- Không push/deploy/production mutation/gửi dữ liệu nếu người dùng chưa cấp quyền.
- Thiếu quyết định quan trọng thì trả BLOCKED, không tự đoán.
- Viết/cập nhật test cùng production code khi `UT REQUIRED: YES`; không trì hoãn test tới sau review.
- Không hạ threshold, thêm exclusion, skip test hoặc làm yếu assertion để ép pass.

LỆNH SETUP/CHẠY
- <lệnh, URL/port, readiness, timeout, cách dừng>

KIỂM TRA BẮT BUỘC
- Targeted tests:
- Lint/typecheck/build:
- Browser QA/Chrome DevTools MCP nếu phù hợp:
- Kết quả mong đợi:

QUALITY CONTRACT
- UT REQUIRED: YES | NO — rationale:
- Test IDs/AC mapping:
- UT command và expected result:
- Coverage tool/command/policy/report path:
- Clean Code/static self-review checks:
- Alternative evidence nếu N/A:

BẰNG CHỨNG NGHIỆM THU
- ...

ĐỊNH DẠNG TRẢ VỀ
Dùng mẫu báo cáo bên dưới, không bỏ ID, revision, diff/patch hoặc failed checks.
```

Prompt phải tự đầy đủ nhưng tham chiếu tài liệu bằng path/section ID thay vì chép nội dung dài.

## 4. Preflight và thực thi của Antigravity

Antigravity phải:

1. Đọc mọi context được tham chiếu và kiểm tra Git nếu có.
2. Xác nhận base revision, fingerprint với đúng algorithm/metadata/exclusion options, artifact versions và inbound baseline.
3. Mismatch thì trả `BLOCKED` trước khi sửa.
4. Implement thay đổi nhỏ nhất; viết/cập nhật test trong cùng task khi áp dụng.
5. Chạy mọi check/coverage theo Quality Contract, tự review production code và test, thực hiện runtime QA rồi trả báo cáo; không tự nghiệm thu.
6. Tạo Phase 06 implementation evidence đủ để Codex thực hiện Phase 07 review cycle; `COMPLETED` không hợp lệ nếu failed/skipped check bị che hoặc final diff không inspect được.

## 5. Mẫu báo cáo

```text
PROMPT ID:
TASK ID(S):
ATTEMPT:
SCOPE ID/TYPE/ROOT:
STATUS: COMPLETED | BLOCKED | VERIFICATION_FAILED
OPERATING MODE:
HANDOFF MODE:
INBOUND BASELINE USED:
BASE REVISION:
STARTING FINGERPRINT:
FINGERPRINT ALGORITHM:
FINGERPRINT METADATA FILES:
FINGERPRINT EXCLUSIONS:
ARTIFACT VERSIONS USED:
APPROVED PHASE RECORDS USED: 01 / 03 / 04 / 05
DIRECT DEPENDENCY/IMPACT SCOPES USED:
HEAD REVISION:

TÓM TẮT

FILE ĐÃ ĐỔI
- <path>: <reason>

THAY ĐỔI CÓ THỂ KIỂM TRA
- Shared: exact working tree/git diff
- Separated: patch hoặc commit/bundle

VERIFICATION
- <command/check>: PASS | FAIL — <result>

UNIT TEST / COVERAGE
- UT required/rationale:
- Test files và AC/Test ID mapping:
- Passed/failed/skipped:
- Coverage tool/command/policy/metrics/delta:
- Coverage report path:
- Critical uncovered lines/branches và risk:

CLEAN CODE SELF-REVIEW
- Design/complexity/naming/comments/style/docs/test quality:
- Finding còn lại:

BROWSER QA
- Route/viewport/journey:
- Console:
- Network:
- Screenshot/evidence:

GIẢ ĐỊNH

VẤN ĐỀ/BLOCKER CÒN LẠI
```

## 6. Codex review

Codex thực hiện toàn bộ Phase 07 Implementation Review theo
quality-gates-evidence.md. Verify implementation, Code & Clean Code Review và
fix/re-review là một cycle; không dừng xin ba verdict riêng. Mỗi incoming diff
dùng một attempt `07-A<n>`.

Kiểm tra tối thiểu:

1. Actual diff đúng prompt, đúng scope root và không sửa ngoài phạm vi.
2. Hành vi đúng Specification/AC.
3. Design, abstraction, complexity, naming, comments, style, duplication/dead code và docs đúng Plan/convention; không over-engineer.
4. Error, boundary, security và accessibility liên quan.
5. Test đúng level, xác minh hành vi/edge case, có assertion hữu ích và được maintain như production code.
6. UT/coverage policy, lệnh kiểm tra và runtime evidence đầy đủ; phân tích critical uncovered branches thay vì chỉ nhìn %.
7. Revision/diff khớp Prompt ID và Task ID.

Shared workspace: đọc diff thật và chạy lại targeted/risk-based check. Separated
workspace: đọc patch/commit và bằng chứng truy cập được. Ghi file:line, severity
và resolution cho mọi finding; không xem được thay đổi thì Phase 07 `BLOCKED`.

Trong Phase 07:

- Evidence/diff không đáng tin: ghi `BLOCKED` hoặc `CHANGES_REQUIRED` và nêu input còn thiếu.
- Có `BLOCKER/MAJOR`: tạo một bundled correction prompt trong scope đã duyệt; Antigravity sửa rồi Codex re-review ở attempt tiếp theo.
- Cần mở rộng scope/quyền, chấp nhận risk hoặc cùng root cause lặp lại: dừng xin quyết định người dùng.
- Không còn finding bắt buộc và evidence đáng tin: Codex ghi `RECOMMEND APPROVAL` và trình một user verdict cuối cho toàn cycle.

Chỉ sau Phase 07 `APPROVED` mới chạy Phase 08 Final Verification. Task chỉ đặt
`Verified` sau Phase 08 `APPROVED`; không dùng kết quả UT/coverage của revision
trước correction làm final evidence.

## 7. Prompt sửa và retry

Correction prompt phải tự đủ để thực thi nhưng **compact**: dẫn chiếu Original Prompt/Task/Specification bằng ID, path và version thay vì chép lại toàn bộ nội dung đã duyệt. Chỉ gồm context tối thiểu, finding bắt buộc, active scope root, allowed/frozen scope, checks bị ảnh hưởng và report cần trả. Không tạo prompt riêng cho checkpoint, bookkeeping, `MINOR` hoặc `NIT`.

Mặc định bundle mọi `BLOCKER/MAJOR` vào correction prompt đầu tiên khi scope, quyền và Phase 05 đã duyệt vẫn còn hiệu lực. Codex được phát hành prompt này và re-review mà không yêu cầu user approve từng finding; Antigravity thực hiện fix. Nếu user đã giới hạn quyền sửa, finding cần mở rộng scope/quyền hoặc cần chấp nhận risk thì xin quyết định trước phần đó. User vẫn đưa một verdict cuối cho toàn Phase 07. Thêm:

```text
Original Prompt ID:
Correction Prompt ID:
Attempt:
Current base/workspace state:
SCOPE ID/ROOT:
Failed AC/review finding:
Observed evidence:
Required correction:
Unchanged scope/files không được sửa:
Checks phải chạy lại:
Phase 07 Review Record bị ảnh hưởng phải cập nhật:
```

Không bắt buộc Antigravity lặp lại full report, checksum từng file hoặc mọi check
không liên quan correction. Codex cập nhật Phase 07 từ actual diff/evidence và
chỉ lập Phase 08 sau khi review cycle được approve.

Ngân sách mặc định là một bundled correction attempt cho mỗi task. Chỉ phát hành attempt tiếp theo khi còn `BLOCKER/MAJOR` thực sự và người dùng quyết định tiếp tục; nếu cùng root cause lặp lại, dừng retry, đánh giá lại Specification/Plan/task thay vì tạo chuỗi A2/A3/A4.
