# Hồ sơ minh chứng theo rubric

**Nguồn chuẩn:** [PDF rubric gốc](../rubric/Rubric_Do_An_Mon_Hoc_CNPM_sinhvien.docx.pdf), mục 3 và mục 8. Folder này là bộ hồ sơ trình bày cho người chấm; bằng chứng triển khai gốc của từng module tiếp tục nằm ở [Evidence Manifest của module](../sdd/prompt-log.md) và được dẫn về đây. Không nhân đôi file lớn hoặc tách evidence khỏi Prompt ID/revision.

| Mục rubric | Hồ sơ | Tình trạng hiện tại |
| --- | --- | --- |
| Hồ sơ quy trình bắt buộc | [00-process](00-process/README.md) | PARTIAL |
| TC1 — Tính thực tiễn và hiểu biết vấn đề | [tc1-problem](tc1-problem/README.md) | PARTIAL |
| TC2.1 — Phân tích nghiệp vụ, SRS và thiết kế | [tc2-1-requirements-design](tc2-1-requirements-design/README.md) | PARTIAL |
| TC2.2 — Mức độ hoàn thiện sản phẩm | [tc2-2-product](tc2-2-product/README.md) | PENDING |
| TC2.3 — Làm chủ và kiểm soát AI | [tc2-3-ai-usage](tc2-3-ai-usage/README.md) | PARTIAL |
| TC2.4 — Chất lượng mã nguồn | [tc2-4-code-quality](tc2-4-code-quality/README.md) | PENDING |
| TC2.5 — Kiểm thử phần mềm | [tc2-5-testing](tc2-5-testing/README.md) | PENDING |
| TC2.6 — CI/CD và vận hành | [tc2-6-cicd-ops](tc2-6-cicd-ops/README.md) | PENDING |
| TC2.7 — Thực nghiệm người dùng | [tc2-7-user-study](tc2-7-user-study/README.md) | PENDING |
| TC3 — Chất lượng thuyết trình | [tc3-presentation](tc3-presentation/README.md) | PENDING |
| TC4 — Luận văn và tài liệu tham khảo | [tc4-thesis](tc4-thesis/README.md) | PENDING |
| TC5 — Trả lời hội đồng | [tc5-defense](tc5-defense/README.md) | PENDING |
| TC6 — Kết quả nổi bật | [tc6-achievements](tc6-achievements/README.md) | PENDING |

## 12 hồ sơ bắt buộc của rubric

| STT | Hồ sơ | Nơi quản lý chính | Hiện trạng |
| --- | --- | --- | --- |
| 1 | Phiếu đăng ký GV/SV và phân công | [00-process](00-process/README.md) | Phân công W1 có; phiếu ký chưa có |
| 2 | Sổ tiến độ hằng tuần có xác nhận GVHD | [00-process](00-process/README.md) | Báo cáo W1 có; xác nhận GVHD chưa có |
| 3 | Cam kết sản phẩm cuối + metric có chữ ký | [00-process](00-process/README.md) | PENDING |
| 4 | Link Git và lịch sử commit, quyền hội đồng | [TC2.2](tc2-2-product/README.md) / [TC2.4](tc2-4-code-quality/README.md) | PENDING trong repo mới |
| 5 | AI Usage Log hoặc cam kết không dùng AI | [TC2.3](tc2-3-ai-usage/README.md) | Log bắt đầu cho công việc Codex hiện tại; Antigravity chưa có prompt |
| 6 | SRS/SDD và sơ đồ | [TC2.1](tc2-1-requirements-design/README.md) | Báo cáo/sơ đồ W1 có; SDD module còn DRAFT |
| 7 | Static analysis, secret scan, convention | [TC2.4](tc2-4-code-quality/README.md) | PENDING |
| 8 | Test plan/case/code/coverage/defect | [TC2.5](tc2-5-testing/README.md) | PENDING |
| 9 | Config pipeline, run/deploy history, link | [TC2.6](tc2-6-cicd-ops/README.md) | PENDING |
| 10 | User study: task, người tham gia ẩn danh, data, metric, cải tiến | [TC2.7](tc2-7-user-study/README.md) | PENDING |
| 11 | Báo cáo trùng lặp, tài liệu tham khảo ngoại ngữ | [TC4](tc4-thesis/README.md) | PENDING |
| 12 | Minh chứng kết quả nổi bật | [TC6](tc6-achievements/README.md) | PENDING |

`M06 — Diagnostic Report` tạo báo cáo chẩn đoán cho một bài nói của người dùng. Thư mục `docs/evidence/` này là hồ sơ nộp theo rubric; `evidence/` trong từng module lưu kết quả triển khai/kiểm thử của chính module đó.

## Quy tắc lưu và xác minh

- W1: báo cáo/hình gốc giữ ở docs/reports/ và docs/design/; mục rubric trỏ tới chúng. Giờ công 60 giờ là giả định kế hoạch, không là timesheet xác minh.
- W2/W3: prompt Antigravity và raw report/test/coverage/review ở scope module; mỗi mục rubric dẫn về đúng evidence ID/Prompt ID và revision.
- Hồ sơ có chữ ký, dữ liệu người tham gia hoặc thông tin nhạy cảm chỉ lưu bản phù hợp quyền truy cập; manifest ghi nơi lưu và người giữ, không commit dữ liệu thật vào Git.
- Tình trạng PARTIAL/PENDING là tình trạng hồ sơ, không phải điểm rubric hoặc verdict SDD. Chỉ nâng trạng thái khi file, nguồn và kiểm tra thực tế đã đủ.
