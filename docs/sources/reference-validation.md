# Xác minh bản tham chiếu hiện tại — 25/09/2026

**Nguồn:** `../ai-assessor-cefr-thamchie/` do nhóm phát triển. Kiểm tra tại chỗ theo yêu cầu chủ dự án sau khi thư mục tham chiếu được cập nhật. Đây là kết quả của **bản tham chiếu**, không phải test/coverage của `ai-assessor-cefr` dựng lại.

| Check | Lệnh/điều kiện | Kết quả quan sát |
| --- | --- | --- |
| Định dạng | `.venv/bin/ruff format --check src tests` | Exit 0; 72 file đã đúng format |
| Lint | `.venv/bin/ruff check --no-cache src tests` | Exit 0; `All checks passed!` |
| Test | `PYTHONPATH=<thư mục tham chiếu>/src PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE=/tmp/aicefr-reference-coverage-20260925 .venv/bin/python -m pytest -q -p no:cacheprovider tests` | Exit 0; không có fail/skip trong output. `pytest --collect-only` xác nhận 442 test. Coverage tổng 89% (2.587 statement, 292 miss). |

Môi trường `.venv` còn editable package hướng tới một đường dẫn cũ, nên lần gọi pytest đầu tiên không có `PYTHONPATH` dừng ở `ModuleNotFoundError: aicefr` trước khi collect. Chạy lại với source path hiện tại đã qua toàn bộ test. Điều này là vấn đề đường dẫn môi trường sau khi dời thư mục, không phải kết quả test thất bại của source hiện tại.

**Giới hạn:** suite dùng fixture/test double cho nhiều boundary; lần này không chạy server live qua trình duyệt, không tải Whisper và không đo chất lượng ASR trên audio thật. Những điều đó cần smoke riêng nếu muốn ghi claim runtime thực tế. `.git` trong thư mục tham chiếu hiện thiếu HEAD/config, nên không lấy được revision; [scoring audit](scoring-audit.md) dùng SHA-256 cho file quan trọng.
