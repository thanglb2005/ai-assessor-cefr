# Prompt Log — chỉ mục

Prompt và evidence chính thức thuộc scope root của từng module. File này chỉ dẫn đường, không thay log/Status local. Hiện chưa có prompt Antigravity nào được phát hành.

| Module | Prompt Log | Evidence Manifest | Status |
| --- | --- | --- | --- |
| M01 | [prompts/M01](modules/m01-intake-student/prompts/prompt-log.md) | [evidence/M01](modules/m01-intake-student/evidence/evidence-manifest.md) | [status/M01](modules/m01-intake-student/07-status.md) |
| M02 | [prompts/M02](modules/m02-audio-qc/prompts/prompt-log.md) | [evidence/M02](modules/m02-audio-qc/evidence/evidence-manifest.md) | [status/M02](modules/m02-audio-qc/07-status.md) |
| M03 | [prompts/M03](modules/m03-asr/prompts/prompt-log.md) | [evidence/M03](modules/m03-asr/evidence/evidence-manifest.md) | [status/M03](modules/m03-asr/07-status.md) |
| M04 | [prompts/M04](modules/m04-features/prompts/prompt-log.md) | [evidence/M04](modules/m04-features/evidence/evidence-manifest.md) | [status/M04](modules/m04-features/07-status.md) |
| M05 | [prompts/M05](modules/m05-scoring/prompts/prompt-log.md) | [evidence/M05](modules/m05-scoring/evidence/evidence-manifest.md) | [status/M05](modules/m05-scoring/07-status.md) |
| M06 | [prompts/M06](modules/m06-diagnostic-report/prompts/prompt-log.md) | [evidence/M06](modules/m06-diagnostic-report/evidence/evidence-manifest.md) | [status/M06](modules/m06-diagnostic-report/07-status.md) |
| M07 | [prompts/M07](modules/m07-teacher-review/prompts/prompt-log.md) | [evidence/M07](modules/m07-teacher-review/evidence/evidence-manifest.md) | [status/M07](modules/m07-teacher-review/07-status.md) |
| M08 | [prompts/M08](modules/m08-identity-storage-admin/prompts/prompt-log.md) | [evidence/M08](modules/m08-identity-storage-admin/evidence/evidence-manifest.md) | [status/M08](modules/m08-identity-storage-admin/07-status.md) |

Quy trình: Phase 05 APPROVED → lưu prompt file và log trong module → xác minh fingerprint → bàn giao Antigravity → lưu raw report và evidence trong module → Codex review actual diff → cập nhật Status. Bản chat đơn thuần không tự tạo file prompt hoặc evidence.
