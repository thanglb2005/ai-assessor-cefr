# Khảo sát nền tảng kỹ thuật nội bộ của nhóm

Cập nhật lưu trữ 08/10/2026: thư mục tham chiếu cũ đã được xóa theo yêu cầu; source, tài liệu và dữ liệu local được giữ tại `../ai-assessor-cefr-runtime/backups/ai-assessor-cefr-thamchie-before-cleanup-2026-10-08` (không gồm `.venv`). Các đường dẫn/lệnh khảo sát cũ bên dưới là lịch sử; checksum và kết quả khảo sát không đổi.

**Ngày khảo sát:** 25/09/2026. Nền tảng do nhóm phát triển trong giai đoạn hình thành đề tài được lưu tại `../ai-assessor-cefr-thamchie/`. Khảo sát này xác định miền nghiệp vụ, provenance của model và các boundary kỹ thuật cho SDD hiện hành. `.git` của thư mục lưu trữ thiếu HEAD/config, nên provenance được ghi bằng đường dẫn và fingerprint trong [scoring-audit.md](scoring-audit.md).

| Quan sát trực tiếp | Giá trị sử dụng trong dự án |
| --- | --- |
| [`pyproject.toml`](../../../ai-assessor-cefr-runtime/backups/ai-assessor-cefr-thamchie-before-cleanup-2026-10-08/pyproject.toml) và `src/aicefr/` có API, auth, audio/QC, ASR, features, scoring, report, review, storage, pipeline cùng tests. README có lệnh web và Docker; test/lint được định nghĩa trong `kiemtra.sh`. | M01–M08 phản ánh đầy đủ miền nghiệp vụ đã khảo sát. SDD hiện hành xác lập contract và phạm vi triển khai theo module; test của dự án được đo trên revision tương ứng. |
| [`api/main.py`](../../../ai-assessor-cefr-runtime/backups/ai-assessor-cefr-thamchie-before-cleanup-2026-10-08/src/aicefr/api/main.py) 1.442 dòng, [`storage/repository.py`](../../../ai-assessor-cefr-runtime/backups/ai-assessor-cefr-thamchie-before-cleanup-2026-10-08/src/aicefr/storage/repository.py) 839 dòng, [`contracts.py`](../../../ai-assessor-cefr-runtime/backups/ai-assessor-cefr-thamchie-before-cleanup-2026-10-08/src/aicefr/contracts.py) 277 dòng tại lần kiểm tra này. | Đề xuất tách route, aggregate và contract owner/consumer để dễ review. Số dòng chỉ là quan sát cấu trúc, không là kết luận chất lượng từng hàm. |
| [`pipeline.py`](../../../ai-assessor-cefr-runtime/backups/ai-assessor-cefr-thamchie-before-cleanup-2026-10-08/src/aicefr/pipeline.py) nối QC → ASR → feature → score → report/review. | Đưa các boundary và trạng thái xử lý có provenance vào contract liên module. |
| [`scorer.py`](../../../ai-assessor-cefr-runtime/backups/ai-assessor-cefr-thamchie-before-cleanup-2026-10-08/src/aicefr/scoring/scorer.py) dùng Ridge v2 làm mặc định, có overall score/band cho một response, OOD refusal và năm `CriterionScore` gán cùng overall; xem [kiểm tra model](scoring-audit.md). | M05 triển khai đường overall từ model do nhóm huấn luyện, sau khi kiểm tra contract và provenance. Sản phẩm chỉ hiển thị overall + coverage theo quyết định chủ dự án. |
| [`report/comments.py`](../../../ai-assessor-cefr-runtime/backups/ai-assessor-cefr-thamchie-before-cleanup-2026-10-08/src/aicefr/report/comments.py) dùng template gắn evidence từ feature. | M06 yêu cầu mỗi nhận xét truy lại được evidence và phiên bản nguồn. |

## Kiểm tra chạy tại chỗ

| Check | Lệnh/điều kiện | Kết quả quan sát |
| --- | --- | --- |
| Định dạng | `.venv/bin/ruff format --check src tests` | Exit 0; 72 file đã đúng format |
| Lint | `.venv/bin/ruff check --no-cache src tests` | Exit 0; `All checks passed!` |
| Test | `PYTHONPATH=/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src PYTHONDONTWRITEBYTECODE=1 COVERAGE_FILE=/tmp/aicefr-reference-coverage-20260925 .venv/bin/python -m pytest -q -p no:cacheprovider tests` | Exit 0; không có fail/skip trong output. `pytest --collect-only` xác nhận 442 test. Coverage tổng 89% (2.587 statement, 292 miss). |

Môi trường `.venv` còn editable package hướng tới một đường dẫn cũ, nên lần gọi pytest đầu tiên không có `PYTHONPATH` dừng ở `ModuleNotFoundError: aicefr` trước khi collect. Chạy lại với source path hiện tại đã qua toàn bộ test. Đây là vấn đề đường dẫn môi trường sau khi dời thư mục, không phải kết quả test thất bại của source hiện tại.

**Giới hạn:** số liệu trên là kết quả khảo sát nền tảng kỹ thuật nội bộ tại đường dẫn đã nêu. Suite dùng fixture/test double cho nhiều boundary; lần khảo sát này chưa chạy server live qua trình duyệt, chưa tải Whisper và chưa đo chất lượng ASR trên audio thật. Test/coverage của dự án được chạy riêng theo SDD trên revision hiện hành.
