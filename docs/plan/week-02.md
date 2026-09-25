# W2 — 21–25/09/2026 — kế hoạch và đối chiếu

**Trạng thái tại 25/09/2026:** chưa xác minh kết quả trong repo mới; thư mục đích chưa có source code. Mốc cuối tuần này là mục tiêu kế hoạch, không được ghi DONE nếu thiếu diff/test/evidence.

## Phân công đề xuất

| Thắng | Sang | Nguyên |
| --- | --- | --- |
| M08 identity/storage, M02 audio QC; contract chung, pipeline coordinator, CI tối thiểu | M03 ASR, M04 features, M05 baseline scoring; model/version và failure path | M01 luồng sinh viên, M06 báo cáo chẩn đoán; chuẩn bị contract/UI cho M07 |

## Thứ tự và đầu ra

1. Soạn bản nháp 5 tiêu chí độc thoại theo lựa chọn chủ dự án; review Requirement, Research nếu RUN, Specification, Test Plan rồi Plan/Tasks theo checkpoint trước implementation.
2. Thắng phát hành contract có kiểu, reason code và schema/storage tối thiểu. Sang/Nguyên review phần họ dùng; mỗi người giữ vùng source riêng.
3. M02 → M03 → M04 → M05 → M06 được nối bằng artifact có version. Unit/integration test dùng fixture do nhóm tạo; smoke ASR local dùng audio có quyền sử dụng và kết quả thật. M08/M01 cung cấp nộp bài và trạng thái.
4. Chạy test cho audio lỗi, ASR fail, missing feature, score refusal, owner access và evidence refs. Ghi lệnh/kết quả thật, không dùng kết quả test phiên bản trước.

**Gate cuối W2 (chưa đạt/chưa xác minh):** code mới + test thật cho upload/quyền/QC/ASR/features/report. Một audio có quyền sử dụng chạy offline qua ASR local với model/version/smoke record; nếu chưa có model/audio, ghi `NOT_RUN` và gate còn thiếu. M05 chỉ phát band nếu rubric/model/data phù hợp được duyệt; nếu không, report ghi `NOT_EVALUATED`. `teacher_verified=false` trước hành động M07 thật. Fixture test không phải dữ liệu thực nghiệm CEFR.

## Task W2 theo người (bản nháp, chưa phải công việc đã hoàn tất)

| Owner đề xuất | Task và đầu ra review được | Phụ thuộc/gate |
| --- | --- | --- |
| Thắng | [M08-TASK-001/002](../sdd/modules/m08-identity-storage-admin/06-tasks.md) auth/consent/storage; [M02-TASK-001/002](../sdd/modules/m02-audio-qc/06-tasks.md) QC; thống nhất contract/pipeline/CI | M08 contract trước M01; ngưỡng QC chưa chốt |
| Sang | [M03-TASK-001/002](../sdd/modules/m03-asr/06-tasks.md) ASR contract và local smoke; [M04-TASK-001/002](../sdd/modules/m04-features/06-tasks.md) feature; [M05-TASK-001](../sdd/modules/m05-scoring/06-tasks.md) refusal path | Local model/audio và rubric/model scoring là hai gate khác nhau; M05-TASK-002/003 có điều kiện |
| Nguyên | [M01-TASK-001/002](../sdd/modules/m01-intake-student/06-tasks.md) upload/status; [M06-TASK-001/002](../sdd/modules/m06-diagnostic-report/06-tasks.md) report; [M07-TASK-001](../sdd/modules/m07-teacher-review/06-tasks.md) chuẩn bị contract W3 | Cần M08 owner/consent và output M03–M05; M07 runtime thuộc W3 |

**Thứ tự chấp thuận:** Phase 01 → Phase 03 → Phase 04 → Phase 05 theo từng module; artifact W2 hiện chỉ là bản nháp. Chưa có prompt nào được phát hành cho Antigravity. Kế hoạch này không tự xác nhận task đã làm từ 21–25/09.

## Prompt log và evidence cần có

- Mỗi prompt Antigravity được lưu trước khi gửi tại docs/sdd/modules/MODULE/prompts/; ghi Prompt ID, Task ID, base revision/fingerprint và link trong Prompt Log cùng module.
- Raw report, diff/commit, command output/test, ảnh QA nếu có được lưu hoặc dẫn chiếu tại evidence/ cùng module. Status module trỏ tới bản mới nhất.
- Nếu W2 đã làm ở workspace khác, đưa về repo mới bằng diff/commit và evidence truy cập được rồi mới cập nhật gate. Không chỉ dùng lời tóm tắt.

## Rủi ro

W2 đến hạn 25/09 nhưng source của repo mới vẫn trống tại thời điểm lập file này. Nếu chưa có implementation ở nơi khác, cần giảm scope của W3 còn vertical slice tối thiểu hoặc đổi hạn 02/10; không đánh dấu W2 hoàn thành theo lịch.

Tự rà soát tài liệu: [week-02-sdd-review.md](week-02-sdd-review.md). Hồ sơ tổng hợp theo rubric: [docs/evidence/](../evidence/README.md). Khi có artifact mới, cập nhật manifest TC tương ứng và dẫn về evidence module.
