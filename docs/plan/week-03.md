# W3 — 28/09–02/10/2026 — kế hoạch hoàn thiện

**Trạng thái ngày 02/10/2026:** implementation đã được Thắng trực tiếp giao cho ba subagents `gpt-6-luna`, Codex review trên nhánh `feat/W3-local-integration`. [Scope W3](../sdd/features/w3-local-integration/07-status.md) giữ Task/Prompt/Evidence/Review hiện hành; formal verdict nghiệm thu `PENDING`. Git `main` đã đồng bộ `origin/main` tại `2b428ceea9e4459f3235d4ce67f10bab31585ebf` trước khi tách nhánh.

## Phân công đề xuất

| Thắng | Sang | Nguyên |
| --- | --- | --- |
| Hoàn thiện auth/consent/storage, tích hợp API, local run guide, CI và kiểm tra secret/PII | Hoàn thiện scorer, ASR local smoke nếu đủ điều kiện, edge cases, error analysis và model provenance | Hoàn thiện M07 teacher review, giao diện sinh viên/giảng viên, báo cáo và browser QA bằng fixture được phép |

## Nhịp 5 ngày

| Ngày | Mốc |
| --- | --- |
| 28/09 | Đồng bộ W2, khóa contract và chỉ nhận task SDD đã qua Phase 05 |
| 29/09 | Nối report với hàng đợi/duyệt của giảng viên; kiểm tra quyền và audit |
| 30/09 | Sửa integration, audio/ASR/scoring edge cases và lỗi evidence |
| 01/10 | Chạy full test/CI, local smoke, browser QA cần thiết; review actual diff |
| 02/10 | Chạy lại required checks trên final revision, đóng evidence và trình nghiệm thu từng module |

**Gate cuối W3:** demo sinh viên → AI report → giảng viên duyệt/sửa; không bịa score khi bằng chứng thiếu; CI/test có log và revision; README chạy local; SDD của module active có Review, Final Verification và Acceptance record. Chỉ module thực sự đủ AC mới được đề xuất nghiệm thu.

## Evidence bàn giao

- Prompt log, prompt file, raw report, test output, coverage và code review record nằm trong scope root từng module.
- Final verification ghi final revision/fingerprint và lệnh chạy lại sau review; không tái sử dụng kết quả của revision cũ.
- Báo cáo tuần 3 dẫn về evidence module và nêu rõ hạn chế mô hình/chưa có validation người học nếu vẫn còn.

**Điều kiện lịch:** nếu W2 không có vertical slice kiểm được, gate 02/10 phải thu hẹp hoặc dời theo quyết định của người dùng.

## Lượt triển khai 02/10

| Lane thực hiện | Task local | Người review | Evidence |
| --- | --- | --- | --- |
| Luna pipeline | W3-TASK-001/002: coordinator, SQLite report, rollback/restart | Codex | [raw-pipeline](../sdd/features/w3-local-integration/evidence/raw-pipeline.md) |
| Luna app | W3-TASK-003/004/007: local CLI, auth/consent/UI và browser QA | Codex | [raw-app](../sdd/features/w3-local-integration/evidence/raw-app.md) |
| Luna speech | W3-TASK-005/006: ASR/VAD adapters, scorer robustness, CI | Codex | [raw-speech-fix-01](../sdd/features/w3-local-integration/evidence/raw-speech-fix-01.md) |
| Codex lead | W3-TASK-008: review, verification độc lập, docs/manifest/AI log | Thắng nghiệm thu cuối | [Evidence Manifest](../sdd/features/w3-local-integration/evidence/evidence-manifest.md) |

Task IDs trên là local traceability; không tạo Jira keys hoặc giờ công giả. Phân công owner Thắng/Sang/Nguyên trong kế hoạch gốc được giữ để đối chiếu; automation không được xem là xác nhận giờ làm của từng người. [Local run guide](../local-run.md) cung cấp lệnh chạy demo và cấu hình offline. Không push/deploy từ lượt này; remote CI, calibration/validation trên người học và phê duyệt học thuật chỉ ghi khi có evidence/authorization thực.

Hồ sơ tổng hợp theo rubric: [docs/evidence/](../evidence/README.md). Khi có artifact mới, cập nhật manifest TC tương ứng và dẫn về evidence module.
