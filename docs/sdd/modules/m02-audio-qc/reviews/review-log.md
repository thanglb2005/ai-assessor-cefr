# M02 — Review Records

**Hiện trạng:** SCRUM-46/47 diffs reviewed by Codex; Sang cross-owner review and user merge verdict remain pending.

| Review ID | Prompt ID / Task ID | Base/Head revision | Diff/evidence đã kiểm tra | Finding và resolution | User verdict |
| --- | --- | --- | --- | --- | --- |
| M02-REV-001 | M02-PROMPT-001 / SCRUM-46 | Base `55d8952`; code `a6da59a` | Decoder/config/contract/tests/docs; evidence/M02-EVID-001-SCRUM-46.md | PASS: declared-vs-detected format, resource caps, 16 kHz PCM, safe reasons, no raw audio commit; task tests and coverage PASS. Sang shared-contract review PENDING. | PENDING |
| M02-REV-002 | M02-PROMPT-002 / SCRUM-47 | Base `078d90f`; candidate diff | QC policy, pipeline gate, synthetic tests, evidence/M02-EVID-002-SCRUM-47.md | PASS: versioned thresholds, missing metrics safe REJECT, PASS-only ASR call, REVIEW pending, REJECT blocked; regression/coverage/Ruff PASS. Sang boundary review PENDING. | PENDING |

Codex lưu Phase 07 review record tại đây sau khi kiểm tra actual diff, test và evidence. Phase 08 final verification nằm trong evidence/ trên final revision. Chỉ người dùng ghi verdict phê duyệt.
