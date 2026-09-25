# Khảo sát và xác minh bản tham chiếu hiện tại

**Ngày kiểm tra lại:** 25/09/2026. Bản do nhóm phát triển hiện nằm tại `../ai-assessor-cefr-thamchie/`; chỉ dùng để xác định chức năng và ranh giới khi viết lại. `.git` của thư mục tham chiếu hiện thiếu HEAD/config, nên không lấy được commit; fingerprint của các file scoring nằm trong [scoring-audit.md](scoring-audit.md).

| Quan sát trực tiếp | Tác động cho bản dựng mới |
| --- | --- |
| [`pyproject.toml`](../../../ai-assessor-cefr-thamchie/pyproject.toml) và `src/aicefr/` có API, auth, audio/QC, ASR, features, scoring, report, review, storage, pipeline cùng tests. README có lệnh web và Docker; test/lint được định nghĩa trong `kiemtra.sh`. | M01–M08 phản ánh đúng miền nghiệp vụ đã có. SDD định nghĩa lại contract và code mới theo module; khả năng bản trước đã chạy được được ghi nhận, không coi là test của repo mới. |
| [`api/main.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/api/main.py) 1.442 dòng, [`storage/repository.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/storage/repository.py) 839 dòng, [`contracts.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/contracts.py) 277 dòng tại lần kiểm tra này. | Đề xuất tách route, aggregate và contract owner/consumer để dễ review. Số dòng chỉ là quan sát cấu trúc, không là kết luận chất lượng từng hàm. |
| [`pipeline.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/pipeline.py) nối QC → ASR → feature → score → report/review. | Giữ các boundary và trạng thái xử lý có provenance trong hợp đồng mới. |
| [`scorer.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/scoring/scorer.py) dùng Ridge v2 làm mặc định, có overall score/band cho một response, OOD refusal và năm `CriterionScore` gán cùng overall; xem [kiểm tra model](scoring-audit.md). | M05 ưu tiên dựng lại overall path từ model do nhóm đã huấn luyện; bản mới chỉ hiển thị overall + coverage theo quyết định chủ dự án. |
| [`report/comments.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/report/comments.py) dùng template gắn evidence từ feature. | M06 yêu cầu mỗi nhận xét truy lại được evidence và phiên bản nguồn. |

## Kiểm tra chạy tại chỗ

| Check | Lệnh/điều kiện | Kết quả quan sát |
| --- | --- | --- |
| Định dạng | `.venv/bin/ruff format --check src tests` | Exit 0; 72 file đã đúng format |
| Lint | `.venv/bin/ruff check --no-cache src tests` | Exit 0; `All checks passed!` |
| Test | `PYTHONPATH=/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE=/tmp/aicefr-reference-coverage-20260925 .venv/bin/python -m pytest -q -p no:cacheprovider tests` | Exit 0; không có fail/skip trong output. `pytest --collect-only` xác nhận 442 test. Coverage tổng 89% (2.587 statement, 292 miss). |

Môi trường `.venv` còn editable package hướng tới một đường dẫn cũ, nên lần gọi pytest đầu tiên không có `PYTHONPATH` dừng ở `ModuleNotFoundError: aicefr` trước khi collect. Chạy lại với source path hiện tại đã qua toàn bộ test. Đây là vấn đề đường dẫn môi trường sau khi dời thư mục, không phải kết quả test thất bại của source hiện tại.

**Giới hạn:** đây là kết quả của bản tham chiếu, không phải test/coverage của `ai-assessor-cefr` dựng lại. Suite dùng fixture/test double cho nhiều boundary; lần này không chạy server live qua trình duyệt, không tải Whisper và không đo chất lượng ASR trên audio thật. Mã nguồn mới vẫn phải được kiểm tra riêng theo SDD.
