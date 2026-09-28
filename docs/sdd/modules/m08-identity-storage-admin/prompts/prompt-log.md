# M08 — Prompt Log (nhật ký prompt Antigravity)

**Hiện trạng:** Codex trực tiếp implement theo lệnh của Thắng. M08-EXEC-048 được ghi sau triển khai; không phát hành Antigravity prompt.

| Prompt ID | Task ID | Attempt | Issued at | Phase 05 verdict | Base revision / fingerprint | Prompt file | Raw report / evidence | Review | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M08-EXEC-048 | SCRUM-48 | 1 | Recorded 28/09/2026 after code | APPROVED by Thắng | `55d8952` / `ebe405ae9263` | M08-EXEC-048-SCRUM-48.md | ../evidence/scrum-48-implementation.md | Codex PASS; Nguyên PENDING | DIRECT_CODEX_RECORDED_AFTER_CODE |

Khi phát prompt: tạo file prompt có ID tại thư mục này, cập nhật dòng log và 07-status.md **trước khi** gửi cho Antigravity. Prompt ghi scope, allowed files, artifact versions, base revision, workspace fingerprint, required checks và evidence cần trả. Sau khi nhận kết quả, nối raw report ở evidence/ và review record ở reviews/. Mỗi correction prompt là file và dòng log riêng, dẫn về Prompt ID gốc. Không ghi trạng thái SENT/COMPLETED nếu chưa có thao tác và evidence thật.
