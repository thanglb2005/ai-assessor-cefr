# W3 — Prompt Log

Ngày 02/10/2026. Mọi prompt đầy đủ đã được lưu file và Excel **trước khi dispatch**. Executor là ba subagents `gpt-6-luna` theo yêu cầu trực tiếp của Thắng; root Codex review actual code và tự chạy final checks. Base revision/fingerprint/file boundary nằm trong từng prompt; amendments/notes cùng correction attempt không tạo nghiệm thu mới.

| Prompt ID / full text | W3-TASK | Executor branch | Trạng thái |
| --- | --- | --- | --- |
| [W3-PROMPT-001](W3-PROMPT-001-pipeline.md) | 001,002 | gpt-6-luna / feat/W3-pipeline | DISPATCHED sau lưu file/Excel |
| [W3-PROMPT-002](W3-PROMPT-002-app.md) | 003,004 | gpt-6-luna / feat/W3-app | DISPATCHED sau lưu file/Excel |
| [W3-PROMPT-003](W3-PROMPT-003-speech.md) | 005,006 | gpt-6-luna / feat/W3-speech | DISPATCHED sau lưu file/Excel |
| [W3-PROMPT-001-AMEND-01](W3-PROMPT-001-AMEND-01.md) | 001,002 | gpt-6-luna / feat/W3-pipeline | DISPATCHED sau lưu file/Excel |
| [W3-PROMPT-001-AMEND-02](W3-PROMPT-001-AMEND-02.md) | 001,002 | gpt-6-luna / feat/W3-pipeline | DISPATCHED sau lưu file/Excel |
| [W3-PROMPT-003-FIX-01](W3-PROMPT-003-FIX-01.md) | 005,006 | gpt-6-luna / feat/W3-speech | DISPATCHED sau lưu file/Excel |
| [W3-PROMPT-001-FIX-01](W3-PROMPT-001-FIX-01.md) | 001,002 | gpt-6-luna / feat/W3-pipeline | DISPATCHED sau lưu file/Excel |
| [W3-PROMPT-002-FIX-01](W3-PROMPT-002-FIX-01.md) | 003,004,007 | gpt-6-luna / feat/W3-app-review | DISPATCHED sau lưu file/Excel |
| [W3-PROMPT-002-FIX-01-NOTE-01](W3-PROMPT-002-FIX-01-NOTE-01.md) | 007 | gpt-6-luna / feat/W3-app-review | DISPATCHED sau lưu file/Excel |
| [W3-PROMPT-002-FIX-01-NOTE-02](W3-PROMPT-002-FIX-01-NOTE-02.md) | 003,004,007 | gpt-6-luna / feat/W3-app-review | DISPATCHED sau lưu file/Excel |

[User audio reply](W3-USER-002-audio-rights.md) ghi đúng trả lời “có quyền”: RECORDED, không phải prompt dispatch, không xác nhận model path/ground truth/acceptance.

Excel hiện tại: [AI Prompt Log W03](../../../../evidence/tc2-3-ai-usage/AI%20Prompt%20Log%20-%20W03%20-%202026-09-28_2026-10-04.xlsx), sheet **Thắng**, rows 14–25 cho user instruction, 10 dispatched prompt/amendment/correction/notes và audio reply (trước khi tách theo tuần là rows 18–29 trong workbook tổng hợp). Cột tool dùng `Codex` đúng summary formulas; `gpt-6-luna` ghi trong activity/full prompt. Giữ nội dung lịch sử và sheets Sang/Nguyên/Tổng hợp; không thêm fake Jira key/giờ công. [Audit full text và workbook](../evidence/final/ai-log-audit.json) giữ theo snapshot W3 trước khi biên tập/tách file, không áp dụng lại script audit lịch sử cho workbook hiện tại.

Source/results/review: [Evidence Manifest](../evidence/evidence-manifest.md), [Review](../reviews/review-01.md), [Final Verification](../08-final-verification.md). Tất cả branch/commits local; không push/deploy. User verdict PENDING.
