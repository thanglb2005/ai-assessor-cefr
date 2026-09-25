# Review PR chỉ từ remote, có evidence

Đọc reference này khi người dùng yêu cầu review pull request/merge request, chỉ kiểm tra nội dung PR, chia finding theo severity hoặc xuất báo cáo vào `REVIEWs/`. Chế độ này do Codex thực hiện độc lập; không chạy pipeline Phase 01–09 và không giao Antigravity trừ khi người dùng yêu cầu một bước sửa riêng sau review.

## 1. Hợp đồng đầu vào

Xác định trước khi review:

```text
CHẾ ĐỘ: REMOTE_PR_ONLY
REPOSITORY/REMOTE:
PR ID/URL:
REQUIREMENT SOURCES:
BASE REF/SHA:
HEAD REF/SHA:
REPORT VERSION:
OUTPUT PATH: REVIEWs/review-<PR>-v<version>.md
```

Có thể suy ra repository, PR ID và requirement từ remote hiện tại, URL, PR description, issue/spec được liên kết hoặc chỉ dẫn người dùng. Chỉ hỏi khi không thể xác định đúng PR hoặc thiếu quyền truy cập; không đoán một PR có khả năng gây review nhầm.

Ký hiệu `@REVIEWs/...` trong prompt là cách nhắc tới file. Tên file thật không chứa ký tự `@`.

## 2. Baseline chuẩn: chỉ nội dung PR remote

Nguồn review bắt buộc là trạng thái PR trên provider:

- Metadata PR: ID/URL, trạng thái, base branch/SHA, head branch/SHA và thời điểm lấy dữ liệu.
- Danh sách changed files và patch/diff do provider trả về hoặc diff giữa đúng immutable base/head của PR.
- Nội dung file tại base/head revision khi cần context.
- Requirement/AC từ prompt, PR description và artifact được liên kết.
- CI/check/test artifact gắn đúng head SHA nếu truy cập được.

Không được:

- Dùng `git diff` của working tree, staged diff, untracked file hoặc local branch chưa chứng minh trùng head SHA làm nội dung review.
- Trộn thay đổi local chưa nằm trong PR vào finding, file list, test result hoặc kết luận.
- Tin một patch/report được dán mà không xác định được PR/base/head khi người dùng yêu cầu review remote chính xác.

Có thể dùng CLI/API của provider như `gh pr view`, `gh pr diff` hoặc công cụ tương đương. Nếu cần chạy check, dùng isolated temporary checkout/worktree tại đúng head SHA; không checkout, sửa hay làm sạch workspace hiện tại. Ghi rõ check nào lấy từ CI và check nào Codex tự chạy. Không thể truy cập remote/diff thì kết luận `BỊ CHẶN`, không suy ra `PASS` từ local workspace.

## 3. Ranh giới finding

Đọc đủ context ở base/head để hiểu code, nhưng chỉ tạo finding khi vấn đề:

1. Được PR tạo ra; hoặc
2. Bị PR làm nghiêm trọng hơn; hoặc
3. Nằm ở code không đổi nhưng PR trực tiếp phụ thuộc vào đó khiến behavior mới sai, không an toàn hoặc không đạt requirement.

Không report lỗi code cũ không liên quan chỉ vì nhìn thấy trong lúc đọc context. Không yêu cầu cleanup toàn repo. Nếu cần nói rõ giới hạn, ghi trong phần phạm vi/evidence, không biến thành finding chính thức.

Mỗi finding phải trỏ tới file:dòng thuộc head revision và ưu tiên changed line/hunk. Nếu vị trí gốc nằm ngoài hunk theo trường hợp (3), evidence phải chỉ rõ changed call path hoặc behavior trong PR làm issue trở nên liên quan.

## 4. Thứ tự nguồn requirement

1. Chỉ dẫn trực tiếp mới nhất của người dùng.
2. Acceptance Criteria/spec/issue được PR liên kết và đã duyệt.
3. PR description và commit intent có thể kiểm chứng.
4. Contract, convention và behavior hiện có tại base revision.

Lập trace ngắn `requirement/AC → changed file/hunk → test/evidence`. Kiểm tra cả:

- PR có thực hiện đủ requirement không.
- Diff có thêm feature, refactor, dependency hoặc cleanup ngoài requirement không.
- File ngoài phạm vi có bị sửa không.
- Thay đổi generated/lock/config có lý do truy ngược được không.

Thiếu requirement đủ rõ thì ghi giới hạn review; chỉ đặt finding khi có contract/evidence khách quan, không biến sở thích cá nhân thành lỗi.

## 5. Checklist review bắt buộc

Áp dụng theo stack và mức rủi ro của PR:

### Tính đúng và lỗi code

- Success, invalid input, boundary, error/recovery, state transition, concurrency/async và integration contract.
- Runtime/type/null/undefined/resource leak và backward compatibility.
- Error có bị nuốt, log sai dữ liệu nhạy cảm hoặc trả trạng thái gây hiểu nhầm không.

### Performance

- Thuật toán, vòng lặp, allocation, render, query/network call, cache và tải dữ liệu có regression đáng kể không.
- Chỉ report khi có call path, độ phức tạp, benchmark/profile hoặc bằng chứng hợp lý; không gắn nhãn “chưa tối ưu” chung chung.

### Security

- Authentication/authorization, input validation, injection, XSS/CSRF/SSRF, path traversal, secret/PII, crypto và dependency/config thay đổi theo phạm vi PR.
- Phân biệt exploit thực tế với hardening tùy chọn; nêu attack path và tác động trong evidence.

### Hook rules, ESLint và static checks

- Đọc package scripts, lint config và convention tại base/head để xác định check áp dụng.
- Với React hoặc framework có hooks: kiểm tra thứ tự gọi hook, conditional/loop/early-return, dependency array, stale closure, side effect/cleanup và custom-hook convention.
- Chạy hoặc đọc CI của ESLint/linter/typecheck đúng cấu hình repo khi có thể. Không tuyên bố pass nếu không chạy hoặc không có log đúng head SHA.
- Không report style preference nếu formatter/linter/convention không yêu cầu.

### Clean Code, tối ưu cấu trúc và duplication

- Tên, trách nhiệm, coupling, abstraction, complexity và error contract rõ ràng.
- Không over-engineer, abstraction speculative hoặc thêm dependency không cần thiết.
- Không tạo duplication có hại, dead code, unused import/export hoặc nhánh không thể tới.
- “Tối ưu” ưu tiên correctness, readability và maintainability; không yêu cầu micro-optimization thiếu evidence.

### Unit test và regression

1. Xác định behavior mới/thay đổi/bug fix trong PR.
2. Tìm module tương tự và test tương ứng ở base/head: runner, file naming, setup, test level, assertion và convention.
3. Nếu module tương tự có test cho cùng loại behavior, kiểm tra PR đã thêm/cập nhật test tương ứng chưa.
4. Nếu không có module tương tự, vẫn đánh giá test theo risk/requirement; không tự miễn UT.
5. Kiểm tra test có fail khi behavior hỏng, bao phủ success/error/boundary/regression phù hợp và không mock chính logic cần kiểm tra.
6. Đối chiếu changed production module với changed test files và CI/test result đúng head SHA.

Thiếu UT chỉ là finding khi logic có thể kiểm thử và rủi ro/contract cần test. Với docs, generated file, static asset hoặc thay đổi không có executable behavior, ghi `Không áp dụng` cùng lý do thay vì yêu cầu test giả.

## 6. Evidence và mức độ chắc chắn

Mọi kết luận phải phân biệt:

- `Đã xác minh`: có diff/file:line/command/CI artifact đúng head SHA.
- `Suy luận có căn cứ`: nêu call path và giả định còn lại.
- `Chưa xác minh`: thiếu quyền, runtime, dependency hoặc log; không viết thành sự thật đã pass.

Evidence tối thiểu của report:

```text
PR ID/URL:
BASE SHA:
HEAD SHA:
THỜI ĐIỂM REVIEW:
REQUIREMENT SOURCES:
CHANGED FILES/HUNKS ĐÃ REVIEW:
CHECK/CI ĐÃ ĐỌC HOẶC CHẠY:
GIỚI HẠN REVIEW:
```

Không ghi `không có lỗi security/performance` nếu chỉ đọc một phần diff hoặc thiếu context thiết yếu. Có thể kết luận `không phát hiện issue trong phạm vi đã review` và ghi giới hạn.

## 7. Finding và severity

Chỉ dùng ba cấp độ sau trong report chính:

- `CRITICAL`: có khả năng gây compromise, mất/hỏng dữ liệu, outage nghiêm trọng, bypass kiểm soát quan trọng hoặc khiến PR không thể review đáng tin. Phải sửa trước merge.
- `MAJOR`: sai requirement, lỗi chức năng/regression đáng kể, vi phạm hook/static rule gây behavior sai, performance/security đáng kể hoặc thiếu test cho behavior rủi ro. Phải sửa trước merge.
- `MINOR`: vấn đề giới hạn về maintainability, duplication, test quality hoặc edge case rủi ro thấp; vẫn phải có giải pháp cụ thể.

Không dùng `BLOCKER`, `NIT` hoặc severity khác trong report PR. Style preference không có rule/evidence thì bỏ qua.

Mọi finding, kể cả `MINOR`, bắt buộc có giải pháp:

```markdown
#### [MAJOR] RV-<PR>-<n> — <tiêu đề ngắn>

- Loại: <Mã nguồn | Hiệu năng | Bảo mật | Hook/ESLint | Mã sạch | Trùng lặp | Phạm vi | Unit test>
- Vị trí: `<file:line>` tại head `<sha-ngắn>`
- Bằng chứng: <hành vi/diff/call path/check output quan sát được>
- Ảnh hưởng: <risk, regression hoặc requirement/AC thất bại>
- Giải pháp đề xuất: <thay đổi nhỏ nhất, cụ thể và nằm trong scope PR>
- Cách xác minh sau sửa: <test/lint/typecheck/runtime check cần chạy>
```

Không gộp nhiều nguyên nhân độc lập vào một finding. Không đề xuất refactor ngoài scope khi một sửa chữa hẹp giải quyết được issue.

## 8. Cấu trúc report tiếng Việt

Mặc định một PR tạo một file. Nếu người dùng yêu cầu báo cáo tổng hợp nhiều PR, tạo section riêng cho từng PR và không trộn finding/evidence giữa các PR.

```markdown
# Báo cáo review PR #<ID> — phiên bản <N>

## PR #<ID>: <tiêu đề>

### Thông tin và phạm vi

- Kho mã nguồn/URL:
- SHA nền:
- SHA đầu:
- Requirement đã đối chiếu:
- Tệp/hunk thay đổi đã review:
- Kiểm tra/CI đã xác minh:
- Giới hạn review:

### CRITICAL

Không có.

### MAJOR

<finding hoặc “Không có.”>

### MINOR

<finding hoặc “Không có.”>

### Unit test

- Module tương tự/test convention đã tham khảo:
- Test PR đã thêm/cập nhật:
- Kết luận và evidence:

### Kết luận

- Số issue: CRITICAL <n>, MAJOR <n>, MINOR <n>.
- Kết quả: <CẦN SỬA TRƯỚC KHI MERGE | CÓ THỂ MERGE | BỊ CHẶN>
```

Toàn bộ lời giải thích, finding và kết luận phải bằng tiếng Việt. Chỉ giữ nguyên tên code, identifier, đường dẫn, command, log, tên tool và ba nhãn severity bắt buộc khi cần chính xác kỹ thuật.

## 9. Đường dẫn, phiên bản và quyền

- Output mặc định khi được yêu cầu: `REVIEWs/review-<PR>-v<version>.md` trong workspace báo cáo.
- Tạo thư mục `REVIEWs/` nếu chưa có. Không ghi đè report cũ; nếu file đã tồn tại, tăng version hoặc hỏi khi version bị người dùng cố định.
- Report v2/v3 phải ghi đúng head SHA được review; không tái sử dụng kết luận v1 nếu PR đã đổi head.
- Tạo file report không đồng nghĩa được phép post comment, approve/request changes, merge PR, push code hoặc sửa branch. Mọi external mutation cần quyền riêng.

## 10. Điều kiện hoàn tất

Chỉ kết luận review hoàn tất khi:

1. PR remote, base/head SHA và requirement source được xác định.
2. Toàn bộ changed files/hunks thuộc PR đã được xem hoặc giới hạn được ghi rõ.
3. Checklist áp dụng đã được đánh giá bằng evidence.
4. Lỗi code cũ ngoài phạm vi không bị đưa vào findings.
5. Mỗi finding có severity đúng, evidence, ảnh hưởng, giải pháp và cách xác minh.
6. UT đã được đối chiếu với behavior thay đổi và module/test tương tự.
7. Report chỉ dùng tiếng Việt theo quy ước và nằm đúng output path.

Nếu thiếu điều kiện 1–3 do không truy cập được remote/evidence, kết luận `BỊ CHẶN`; không thay thế bằng review local workspace.
