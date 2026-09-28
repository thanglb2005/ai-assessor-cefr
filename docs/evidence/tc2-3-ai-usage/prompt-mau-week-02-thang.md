# Bộ prompt mẫu W2 — Thắng

> 8 prompt mẫu cho lead giao coding agent. Bốn prompt review/sửa là kịch bản giả định, chưa được gửi và không phải finding lịch sử.
> Sheet `Prompt mẫu W2` trong AI Prompt Log.xlsx chứa cùng nội dung; sheet `Thắng` là nhật ký sử dụng.

## W2-P01 — SCRUM-46 / M02-TASK-001

**Loại:** Triển khai · **Trạng thái:** MẪU / CHƯA GỬI

```text
Bạn là coding agent phụ trách M02-TASK-001. Làm trên branch SCRUM-46; trước khi sửa, đọc M02 Requirement v0.2, Specification v0.3, Test Plan v0.2, 05-plan và 06-tasks; báo HEAD và fingerprint của worktree.
Triển khai decoder SoundFile 0.14.0 + SoXR 1.1.0 từ bytes đã được cấp quyền: WAV PCM, FLAC, OGG/Vorbis, MP3; mono giữ nguyên, stereo lấy trung bình, >2 kênh REJECT. Dùng QCConfig versioned bắt buộc cho byte/rate/frame/duration caps và ngưỡng đo; xuất PCM float32 mono 16 kHz, SHA-256 raw bytes, duration/silence/clipping và reason code an toàn.
Chỉ sửa M02, M02 additions trong shared contract, dependency và tests đã ghi ở 05-plan. Không đặt threshold sản phẩm, không commit audio/model/secret/dữ liệu thật. Chạy M02-TEST-001–006, regression, Ruff; đạt line ≥90%, branch ≥85%. Trả commit, diff summary, lệnh/exit code, PASS/SKIP, coverage và evidence path; ghi Sang review shared contract là PENDING.
```

**Đầu ra kỳ vọng:** Decoder + contracts + tests; M02-TEST-001–006 PASS; coverage và evidence có revision.

## W2-P02 — SCRUM-46 / M02-TASK-001

**Loại:** Review/sửa mẫu · **Trạng thái:** MẪU / CHƯA GỬI

```text
Kịch bản review giả định cho SCRUM-46: chưa chấp nhận nếu input khai WAV nhưng bytes thực là format khác, decoder vượt hard cap, native exception lộ thông tin, hoặc PCM đầu ra sai mono/float32/16 kHz. Hãy kiểm tra actual diff và chạy test để xác nhận từng nghi vấn; không mặc định rằng lỗi đã tồn tại.
Với lỗi tái hiện được, viết test boundary trước, sửa tối thiểu trong file scope SCRUM-46, giữ QC reason ổn định và đo lại line/branch coverage. Với nghi vấn không tái hiện, ghi lệnh, kết quả và lý do đóng finding. Kiểm tra không có audio fixture nhị phân hay secret trong commit.
Trả bảng finding → root cause → commit sửa → Test ID/evidence; chạy lại M02-TEST-001–006 và regression. Không ghi review PASS cho test chưa chạy; Sang contract review vẫn PENDING.
```

**Đầu ra kỳ vọng:** Finding có bằng chứng; test tái hiện trước fix; regression/coverage sau fix.

## W2-P03 — SCRUM-47 / M02-TASK-002

**Loại:** Triển khai · **Trạng thái:** MẪU / CHƯA GỬI

```text
Bạn là coding agent phụ trách M02-TASK-002. Bắt đầu từ commit SCRUM-46 đã kiểm tra, làm trên branch SCRUM-47; đọc M02 Specification v0.3, Test Plan v0.2 và contract hiện hành, báo base SHA/fingerprint.
Từ QCMeasurement và QCConfig versioned, triển khai policy PASS/REVIEW/REJECT với min-duration, silence và clipping thresholds cấu hình tường minh. Missing/invalid measurements phải fail closed; giữ reason và config version. Thêm pipeline boundary nhận ASR port qua injection: chỉ PASS gọi ASR đúng một lần; REVIEW chờ duyệt, REJECT bị chặn; non-PASS không tạo transcript/score. Không sửa M03 AsrService hoặc đặt production thresholds.
Viết M02-TEST-007/008 bằng signal tổng hợp và ASR spy, chạy lại M02-TEST-001–008, full regression, Ruff và coverage line ≥90%/branch ≥85%. Trả code diff, lệnh/exit code, PASS/SKIP, coverage, revision và evidence; ghi Sang review boundary là PENDING.
```

**Đầu ra kỳ vọng:** Policy/pipeline gate; ASR spy chứng minh PASS-only; Test IDs 001–008 và evidence.

## W2-P04 — SCRUM-47 / M02-TASK-002

**Loại:** Review/sửa mẫu · **Trạng thái:** MẪU / CHƯA GỬI

```text
Kịch bản review giả định cho SCRUM-47: chưa chấp nhận nếu REVIEW/REJECT vẫn gọi ASR, missing measurement được hiểu là 0, config version sai bị bỏ qua, hoặc một REJECT reason bị hạ xuống REVIEW. Hãy kiểm tra diff thực tế, đo call count bằng ASR spy và chứng minh từng tình huống bằng test; không tuyên bố finding nếu không tái hiện.
Với lỗi xác nhận, sửa riêng policy/pipeline/tests trong scope SCRUM-47, giữ shared contract và M03 service ổn định. Test cả trường hợp nhiều reason cùng lúc, threshold tại biên và format structural REJECT từ decoder. Chạy toàn bộ M02 Test IDs và regression sau sửa.
Trả finding, test đỏ trước fix/test xanh sau fix, commit, coverage, lệnh/exit code và evidence; ghi rõ Sang chưa duyệt shared boundary nếu vẫn PENDING.
```

**Đầu ra kỳ vọng:** Review gate PASS/REVIEW/REJECT có ASR spy; finding và correction evidence.

## W2-P05 — SCRUM-48 / M08-TASK-001

**Loại:** Triển khai · **Trạng thái:** MẪU / CHƯA GỬI

```text
Bạn là coding agent phụ trách M08-TASK-001. Làm trên branch SCRUM-48; đọc M08 Requirement v0.2, Specification v0.3, Test Plan v0.2 và 05-plan/06-tasks; báo base SHA/fingerprint trước khi sửa.
Chỉ bootstrap tài khoản fixture tường minh. Dùng Argon2id m=19456 KiB, t=2, p=1; token opaque từ 32 byte ngẫu nhiên, repository chỉ lưu SHA-256 digest; session idle 30 phút, absolute 8 giờ qua SessionRecord typed; persistence sau restart được kiểm chứng khi nối SQLite ở SCRUM-49. Role lấy từ account đã xác thực, không từ client. Consent active/versioned và withdrawal phải chặn submit mới; owner check trả cùng lỗi cho missing/foreign resource.
Chỉ sửa auth, M08 auth contract, dependency/tests trong scope. Không HTTP/UI, tài khoản thật, PII, credential/token trong log hoặc Git. Chạy M08-TEST-001/002/004/005, regression, Ruff, coverage line ≥90%/branch ≥85%. Trả commit, lệnh/exit code, PASS/SKIP, coverage và evidence; Nguyên review shared contract PENDING.
```

**Đầu ra kỳ vọng:** Fixture auth/consent/owner; digest-only session; scoped tests và privacy evidence.

## W2-P06 — SCRUM-48 / M08-TASK-001

**Loại:** Review/sửa mẫu · **Trạng thái:** MẪU / CHƯA GỬI

```text
Kịch bản review giả định cho SCRUM-48: chưa chấp nhận nếu raw token/password lộ trong DB/log, client tự chọn role, idle TTL được kéo dài quá absolute TTL, idle/absolute TTL sai sau các lần resolve, hoặc foreign/missing owner trả lỗi khác nhau. Hãy đọc diff, kiểm tra session repository fixture/caplog và tái hiện từng nghi vấn bằng fake clock; không gán nhãn lỗi khi chưa có bằng chứng.
Nếu xác nhận, thêm regression test trước khi sửa rồi giới hạn correction trong auth/contract/tests của SCRUM-48. Kiểm tra consent withdrawal chỉ chặn submit mới, không âm thầm xóa dữ liệu fixture cũ. Không đưa dữ liệu thật vào test.
Trả finding, ảnh hưởng bảo mật, test đỏ/xanh, lệnh/exit code, coverage, commit và evidence; nêu Nguyên review M01/M07 vẫn PENDING.
```

**Đầu ra kỳ vọng:** Security review có fake clock, caplog và session-store assertion; correction có test chứng minh.

## W2-P07 — SCRUM-49 / M08-TASK-002

**Loại:** Triển khai · **Trạng thái:** MẪU / CHƯA GỬI

```text
Bạn là coding agent phụ trách M08-TASK-002. Bắt đầu từ SCRUM-48 typed interfaces và làm trên branch SCRUM-49; đọc M08 Specification v0.3, Test Plan v0.2, 05-plan/06-tasks; báo base SHA/fingerprint.
Tạo SQLite schema versioned và repositories với transaction tường minh cho account, session, consent, response, audit. data_dir phải cấu hình ngoài repo. BlobStore nhận bytes giới hạn, ghi staging cùng filesystem, fsync/atomic replace, lưu SHA-256/size và verify lúc đọc; nếu metadata transaction fail thì bù trừ blob. Audit append-only; orphan reconciliation chỉ báo, không tự xóa. Owner/consent gate phải đứng trước read/submit.
Chỉ sửa storage, M08 storage contract và tests trong scope; dùng tmp_path/actor giả danh, không dữ liệu thật hoặc export/delete/retention W3. Chạy M08-TEST-001–005, regression, Ruff, coverage line ≥90%/branch ≥85%. Trả commit, PASS/SKIP, lệnh/exit code, coverage, revision/evidence; Nguyên review PENDING.
```

**Đầu ra kỳ vọng:** SQLite + BlobStore + audit; rollback/checksum/restart tests và revision evidence.

## W2-P08 — SCRUM-49 / tích hợp W2

**Loại:** Review/sửa mẫu · **Trạng thái:** MẪU / CHƯA GỬI

```text
Kịch bản review giả định cho SCRUM-49 và tích hợp W2: chưa chấp nhận nếu DB commit fail để lại blob không được báo, checksum sai vẫn đọc được, path ngoài data_dir lọt qua, audit bị update/delete, hoặc owner check diễn ra sau blob read. Kiểm tra actual diff và dùng tmp_path/fault injection để tái hiện; không tạo finding giả.
Với lỗi xác nhận, viết test tái hiện, sửa tối thiểu trong scope SCRUM-49 và chạy lại M08-TEST-001–005. Sau đó kiểm tra stack SCRUM-46 → 47 → 48 → 49: hợp nhất contracts/dependency, không commit DB/blob/audio/transcript/model/secret, full non-smoke regression, Ruff và coverage cho M02/M08. Ghi mọi SKIP với lý do, tránh báo PASS thay cho SKIP.
Bàn giao review record gồm finding/correction, commit/revision/fingerprint, lệnh/exit code, PASS/SKIP, coverage và evidence. Sang/Nguyên cross-owner review và Thắng merge verdict chỉ đánh dấu APPROVED khi có phản hồi thật.
```

**Đầu ra kỳ vọng:** Fault-injection review + final four-branch verification; evidence và pending owner gates.
