# TC2.3 — Làm chủ và kiểm soát AI

**Nguồn tiêu chí:** rubric PDF tại docs/rubric/. Trạng thái của folder: PARTIAL

## Hồ sơ cần có

AI Usage Log, prompt gốc, mục đích dùng AI, file sinh ra, phần người làm chủ/kiểm tra; log Antigravity theo module.

## Minh chứng hiện có

| Artifact | Vai trò | Tình trạng |
| --- | --- | --- |
| [AI Prompt Log.xlsx](AI%20Prompt%20Log.xlsx) | Mỗi người ghi prompt vào sheet Thắng, Sang hoặc Nguyên; sheet Tổng hợp đếm theo người và công cụ AI | Đang cập nhật |
| [AI Usage Log](ai-usage-log.md) | Bốn bản ghi Codex lúc khởi tạo; prompt mới ghi trong Excel | Lịch sử |
| [Prompt Log các module](../../sdd/prompt-log.md) | Log Antigravity theo scope | Chưa có prompt phát hành |
| [AGENTS.md](../../../AGENTS.md) và [skill SDD chung](../../../.agents/skills/sdd-antigravity-orchestrator/SKILL.md) | Quy tắc/skill nhóm dùng từ bàn giao W2 | Đã lưu trong repo; không thay log prompt hay chứng minh file rule W1 |

## Quy ước ghi AI Prompt Log

Mỗi prompt ghi một dòng trong sheet của người thực hiện: Thắng, Sang hoặc Nguyên. Điền ngày (cột A), tên người tạo (B), công cụ AI (C), công việc (D), prompt (E) và link minh chứng (F). Sheet `Tổng hợp` đếm các dòng có ngày trong phạm vi hàng 6–306 của từng sheet; thống kê công cụ cộng cả ba sheet.

Ba dòng mẫu `abc` đã được xóa nội dung ngày 25/09/2026 để không bị tính như prompt thật. Sheet Thắng hiện có 4 prompt Codex ngày 25/09/2026; sheet Sang/Nguyên để trống chờ prompt do đúng người thực hiện. Chỉ dùng số liệu sau khi từng dòng có prompt và minh chứng thật.

## Còn thiếu / cần xác minh

Chưa có prompt Antigravity được phát hành; link Jira và tệp AI rules có nguồn gốc W1 vẫn chưa có để xác minh. Bộ rule/skill trong repo là bản dùng chung cho W2.

Khi có evidence mới, thêm dòng gồm: Evidence ID, nguồn/path hoặc URL, ngày, owner, Prompt/Task/AC nếu áp dụng, revision/checksum và trạng thái xác minh. Chỉ ghi số liệu và trạng thái PASS khi có phép đo cùng evidence tương ứng.
