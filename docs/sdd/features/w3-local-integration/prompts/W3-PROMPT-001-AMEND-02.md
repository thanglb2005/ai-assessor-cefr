# W3-PROMPT-001-AMEND-02 — schema regression expectations

PROMPT ID: W3-PROMPT-001-AMEND-02
TASK IDS: W3-TASK-001, W3-TASK-002
REPO ROOT: /tmp/aicefr-w3-pipeline
BRANCH: feat/W3-pipeline
BASE: current owned implementation after AMEND-01; source baseline 7bb327b.
AUTHORIZATION: affected regression for schema v3 within W3-AC-002, no behavior/scope expansion.

Cho phép sửa tests/storage/test_sqlite_blob_store.py: current version assertion phải xác minh 3/SQLiteStore.SCHEMA_VERSION; unsupported future schema dùng SQLiteStore.SCHEMA_VERSION+1 (không còn dùng 3 vì v3 giờ supported). Giữ mọi restart/checksum/rollback/authorization assertion, không skip hoặc bỏ test. Commit cùng migration + record amendment trong raw-pipeline. Tiếp tục chạy affected/full tests và gửi commit để root review.

