# TC2.3 — Làm chủ và kiểm soát AI

**Nguồn tiêu chí:** rubric PDF tại docs/rubric/. Trạng thái của folder: PARTIAL

## Hồ sơ cần có

AI Usage Log, prompt gốc, mục đích dùng AI, file sinh ra, phần người làm chủ/kiểm tra; log Antigravity theo module.

## Minh chứng hiện có

| Artifact | Vai trò | Tình trạng |
| --- | --- | --- |
| [AI Prompt Log.xlsx](AI%20Prompt%20Log.xlsx) | Mỗi người ghi prompt vào sheet Thắng, Sang hoặc Nguyên; sheet Tổng hợp đếm theo người và công cụ AI | Đang cập nhật |
| [AI Usage Log](ai-usage-log.md) | Bốn bản ghi Codex lúc khởi tạo; prompt mới ghi trong Excel | Lịch sử |
| [AI Usage Log của Sang W1–W3](sang/README.md) ([CSV đầy đủ](sang/ai-usage-log-sang-W1-W3.csv)) | Bản xuất 55 dòng từ ba tab Sang trong Google Sheet, mỗi dòng có PR/commit; kèm 7 lỗi của AI đã phát hiện và sửa, quy trình kiểm soát đầu ra AI | Đủ W1–W3 (04/10/2026) |
| [Prompt Log các module](../../sdd/prompt-log.md) | Log prompt theo module/feature và người thực hiện | Đọc trạng thái từng scope |
| [W3 Prompt Log](../../sdd/features/w3-local-integration/prompts/prompt-log.md) | Prompt gốc/amendment/correction đã lưu trước giao ba Luna; Codex review | Actual delegation 02/10/2026, sheet Thắng |
| [W3 Review](../../sdd/features/w3-local-integration/reviews/review-01.md) | Findings từ actual diff, correction và independent checks | User verdict PENDING |
| [AGENTS.md](../../../AGENTS.md) và [skill SDD chung](../../../.agents/skills/sdd-antigravity-orchestrator/SKILL.md) | Quy tắc/skill nhóm dùng từ bàn giao W2 | Đã lưu trong repo; không thay log prompt hay chứng minh file rule W1 |

## Quy ước ghi AI Prompt Log

Mỗi prompt ghi một dòng trong sheet của người thực hiện: Thắng, Sang hoặc Nguyên. Điền ngày (cột A), tên người tạo (B), công cụ AI (C), công việc (D), prompt (E) và link minh chứng (F). Sheet `Tổng hợp` đếm các dòng có ngày trong phạm vi hàng 6–306 của từng sheet; thống kê công cụ cộng cả ba sheet.

Ba dòng mẫu `abc` đã được xóa nội dung ngày 25/09/2026 để không bị tính như prompt thật. Các bản ghi khởi tạo ngày 25/09 được giữ; lượt W3 02/10 ghi thêm user instruction, prompt gốc, amendments/corrections và xác nhận quyền audio vào sheet Thắng, với full text và file evidence. Tool column dùng `Codex` để summary formulas hiện có đếm đúng; executor `gpt-6-luna` và vai trò Codex review ghi trong activity/prompt. Không ghi giờ công hay hoạt động của Sang/Nguyên thay họ. Chỉ dùng số liệu sau khi mỗi dòng có prompt/evidence thật; templates chưa có ngày không được tính như prompt thực.

Ngày 02/10/2026, Thắng xác nhận tám prompt Codex W2 `W2-P01–W2-P08` đã được sử dụng thực tế ngày **28/09/2026**. Các hàng 10–17 trong sheet Thắng đã bỏ nhãn `MẪU`/`CHƯA GỬI`, dùng tool `Codex` và điền ngày 28/09/2026; giữ nguyên nội dung prompt. Yêu cầu đính chính được ghi ở hàng 30 với ngày nhận yêu cầu 02/10/2026.

## Còn thiếu / cần xác minh

Lượt W3 dùng Luna, không giả mạo prompt Antigravity. Link Jira cho local W3 Task IDs và tệp AI rules có nguồn gốc W1 chưa có để xác minh. Bộ rule/skill trong repo là bản dùng chung cho W2; authority override W3 ghi rõ tại Requirement, không thay log hay user acceptance.

Khi có evidence mới, thêm dòng gồm: Evidence ID, nguồn/path hoặc URL, ngày, owner, Prompt/Task/AC nếu áp dụng, revision/checksum và trạng thái xác minh. Chỉ ghi số liệu và trạng thái PASS khi có phép đo cùng evidence tương ứng.
