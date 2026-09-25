# W3 — 28/09–02/10/2026 — kế hoạch hoàn thiện

**Trạng thái:** DRAFT. Gate W3 phụ thuộc vào diff và evidence thực tế của W2.

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

Hồ sơ tổng hợp theo rubric: [docs/evidence/](../evidence/README.md). Khi có artifact mới, cập nhật manifest TC tương ứng và dẫn về evidence module.
