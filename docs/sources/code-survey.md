# Khảo sát chức năng bản tham chiếu hiện tại

**Ngày kiểm tra lại:** 25/09/2026. Bản do nhóm phát triển hiện nằm tại `../ai-assessor-cefr-thamchie/`; chỉ dùng để xác định chức năng và ranh giới khi viết lại. `.git` của thư mục tham chiếu hiện thiếu HEAD/config, nên không lấy được commit; fingerprint của các file scoring nằm trong [scoring-audit.md](scoring-audit.md).

| Quan sát trực tiếp | Tác động cho bản dựng mới |
| --- | --- |
| [`pyproject.toml`](../../../ai-assessor-cefr-thamchie/pyproject.toml) và `src/aicefr/` có API, auth, audio/QC, ASR, features, scoring, report, review, storage, pipeline cùng tests. README có lệnh web và Docker; test/lint được định nghĩa trong `kiemtra.sh`. | M01–M08 phản ánh đúng miền nghiệp vụ đã có. SDD định nghĩa lại contract và code mới theo module; khả năng bản trước đã chạy được được ghi nhận, không coi là test của repo mới. |
| [`api/main.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/api/main.py) 1.442 dòng, [`storage/repository.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/storage/repository.py) 839 dòng, [`contracts.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/contracts.py) 277 dòng tại lần kiểm tra này. | Đề xuất tách route, aggregate và contract owner/consumer để dễ review. Số dòng chỉ là quan sát cấu trúc, không là kết luận chất lượng từng hàm. |
| [`pipeline.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/pipeline.py) nối QC → ASR → feature → score → report/review. | Giữ các boundary và trạng thái xử lý có provenance trong hợp đồng mới. |
| [`scorer.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/scoring/scorer.py) dùng Ridge v2 làm mặc định, có overall score/band cho một response, OOD refusal và năm `CriterionScore` gán cùng overall; xem [kiểm tra model](scoring-audit.md). | M05 ưu tiên dựng lại overall path từ model do nhóm đã huấn luyện. Cách hiển thị năm dòng tiêu chí cần quyết định riêng vì code hiện tại không có năm model/năm nhãn riêng. |
| [`report/comments.py`](../../../ai-assessor-cefr-thamchie/src/aicefr/report/comments.py) dùng template gắn evidence từ feature. | M06 yêu cầu mỗi nhận xét truy lại được evidence và phiên bản nguồn. |

**Giới hạn:** [kết quả lint/test tham chiếu](reference-validation.md) đã được ghi riêng; chúng không thay bằng chứng implementation W2. Tài liệu này là khảo sát để soạn SDD, không phải yêu cầu phải giữ nguyên cấu trúc file của bản cũ.
