# TC2.4 — Chất lượng mã nguồn

**Nguồn tiêu chí:** rubric PDF tại docs/rubric/. Trạng thái của folder: PARTIAL — có source/review/lint local, user verdict PENDING.

## Hồ sơ cần có

Git history, coding convention, static analysis, lint/typecheck, secret scan và review record.

## Minh chứng hiện có

| Evidence | Phạm vi | Revision/owner |
| --- | --- | --- |
| [W3 Review](../../sdd/features/w3-local-integration/reviews/review-01.md) | Actual diff/tests, transaction/refusal/provenance/auth/privacy và bundled corrections | Codex, 02/10/2026; commits trong record |
| [Speech correction](../../sdd/features/w3-local-integration/evidence/raw-speech-fix-01.md) | Offline pin, deterministic optional-package mocks, safe logs | af5dc8a, gpt-6-luna |
| [Pipeline correction](../../sdd/features/w3-local-integration/evidence/raw-pipeline-fix-01.md) | SQLite atomicity, CAS/recovery, grounded evidence | 5056d05, gpt-6-luna |
| [W3 Evidence Manifest](../../sdd/features/w3-local-integration/evidence/evidence-manifest.md) | Lint/guards và final verification thực tế | Codex final rerun; không là remote CI |

## Còn thiếu / cần xác minh

Không có static typechecker riêng được cấu hình; type hints được review và Ruff kiểm lint. Forbidden-file guard chỉ kiểm tên/extension. Content review của Codex dùng bốn nhóm credential patterns và actual changed code/logs, không là chứng nhận quét hết PII/secret của binary attachments hay toàn bộ lịch sử Git. Remote CI và user review giữ trạng thái riêng.

Khi có evidence mới, thêm dòng gồm: Evidence ID, nguồn/path hoặc URL, ngày, owner, Prompt/Task/AC nếu áp dụng, revision/checksum và trạng thái xác minh. Chỉ ghi số liệu và trạng thái PASS khi có phép đo cùng evidence tương ứng.
