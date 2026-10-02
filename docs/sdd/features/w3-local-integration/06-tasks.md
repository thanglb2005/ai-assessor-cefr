# W3 — Tasks

Ngày cập nhật: 02/10/2026. Nhánh tích hợp: `feat/W3-local-integration`.

| Task ID | Owner / executor | AC / Test | Kết quả triển khai và technical check |
| --- | --- | --- | --- |
| W3-TASK-001 | Thắng / gpt-6-luna pipeline | AC-001 / TEST-001–003 | IMPLEMENTED — coordinator; QC/refusal/failure và grounded evidence PASS |
| W3-TASK-002 | Thắng / gpt-6-luna pipeline | AC-002 / TEST-004 | IMPLEMENTED — SQLite report/migration, CAS, restart và rollback PASS |
| W3-TASK-003 | Thắng / gpt-6-luna app | AC-003 / TEST-005 | IMPLEMENTED — factory/CLI, auth/logout/current consent và quyền truy cập PASS |
| W3-TASK-004 | Thắng / gpt-6-luna app | AC-003/005 / TEST-005,008 | IMPLEMENTED — student/teacher UI, authorized audio và hướng dẫn local PASS |
| W3-TASK-005 | Thắng / gpt-6-luna speech | AC-004 / TEST-003,006 | IMPLEMENTED — offline ASR/VAD, pin/hash/provenance; actual WAV smoke PASS |
| W3-TASK-006 | Thắng / gpt-6-luna speech | AC-005 / TEST-008 | IMPLEMENTED — artifact validation, log privacy, CI config và regression PASS |
| W3-TASK-007 | Thắng / gpt-6-luna app | AC-003 / TEST-007 | IMPLEMENTED — reusable Chromium QA; Codex rerun desktop/mobile PASS |
| W3-TASK-008 | Thắng / Codex reviewer | AC-001–005 / final checks | IMPLEMENTED — review/corrections, independent verification, docs/manifest/AI log PASS |

Evidence chung: [Final Verification](08-final-verification.md), [Review](reviews/review-01.md), [Acceptance package](09-acceptance.md). Mỗi hàng đã có technical evidence; task acceptance và trạng thái `Verified` vẫn **PENDING user verdict**. Task IDs là local traceability, chưa có Jira key. Không suy ra giờ công hoặc nghiệm thu các module W2.
