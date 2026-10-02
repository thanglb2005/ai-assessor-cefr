# W3-PROMPT-001-AMEND-01 — affected migration regression

PROMPT ID: W3-PROMPT-001-AMEND-01
TASK IDS: W3-TASK-001, W3-TASK-002
REPO ROOT: /tmp/aicefr-w3-pipeline
BRANCH: feat/W3-pipeline
BASE REVISION: 7bb327b655c67d8eb5aafc4cd8ec9481fabdff28 plus current owned in-progress diff.
AUTHORIZATION: within direct W3 implementation request and existing migration/compatibility AC; Codex extends read/write set for affected regression, no product/spec change.

Cho phép thêm tests/storage/test_sqlite_memory_migration.py vào allowed files để cập nhật assertion schema từ v2 lên SQLiteStore.SCHEMA_VERSION hoặc v3 và kiểm dữ liệu v1→v3. Giữ mọi assertion bảo toàn account/session/consent/response/review/audit; không xóa/skip test hoặc làm yếu verification để ép PASS. Nếu regression test khác hard-code schema version, báo exact path trước sửa. Commit regression cùng source/migration task và ghi amendment ID trong raw-pipeline.md. Tiếp tục implementation/tests/coverage/Ruff và gửi commit SHA; root tự review.
