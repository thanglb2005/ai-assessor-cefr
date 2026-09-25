# Khảo sát read-only phiên bản mã nguồn trước

**Ngày khảo sát:** 25/09/2026. **Mục đích:** nhận diện chức năng, ranh giới và lỗi thiết kế cần tránh khi viết lại `ai-assessor-cefr`; không chuyển mã nguồn hay kết quả cũ vào repo mới. Repo trước `../aiassessor-cefr` do chính chủ dự án phát triển.

| Quan sát trực tiếp | Tác động cho bản dựng mới |
| --- | --- |
| Có package `src/aicefr/` với API, auth, audio/QC, ASR, features, scoring, report, review, storage, pipeline và tests; [`pyproject.toml`](../../../aiassessor-cefr/pyproject.toml) định nghĩa stack Python. | Giữ bản đồ nghiệp vụ M01–M08 nhưng viết code/config/test mới theo SDD của repo này; không xem tên file cũ là contract bắt buộc. |
| [`api/main.py`](../../../aiassessor-cefr/src/aicefr/api/main.py) 1.453 dòng, [`storage/repository.py`](../../../aiassessor-cefr/src/aicefr/storage/repository.py) 852 dòng, [`contracts.py`](../../../aiassessor-cefr/src/aicefr/contracts.py) 628 dòng tại thời điểm khảo sát. | Đề xuất API theo route, repository theo aggregate và contract có owner/consumer rõ; đây là nhận xét cấu trúc, chưa là đánh giá chất lượng từng hàm. |
| [`pipeline.py`](../../../aiassessor-cefr/src/aicefr/pipeline.py) gom QC → ASR → feature → score → report → review; có ghi chú về version mismatch. | Thiết kế orchestration mỏng, từng module trả status/reason và artifact có version. |
| [`scorer.py`](../../../aiassessor-cefr/src/aicefr/scoring/scorer.py) tự ghi nhận rủi ro model huấn luyện theo whole exam nhưng suy luận trên một response; có model JSON và metric trong docstring. | M05 cần khóa `unit_of_inference`, kiểm manifest/model compatibility và từ chối khi thiếu; **không chuyển model JSON, threshold hoặc metric cũ**. |
| [`report/comments.py`](../../../aiassessor-cefr/src/aicefr/report/comments.py) chứa template/ưu tiên gắn với proxy feature. | M06 chỉ phát nhận xét có evidence/ref phù hợp criterion; wording và tính hợp lệ học thuật của từng template cần người có chuyên môn duyệt. |

**Giới hạn khảo sát:** đây là đọc cấu trúc và các boundary nổi bật, không phải code audit hay xác nhận kết quả chạy. Không dùng số dòng, test cũ hoặc comment cũ làm minh chứng hoàn thành W2. Chi tiết quyết định nằm trong SDD của module; bản này chỉ giữ một nơi tham chiếu để tránh lặp đường dẫn `src` cũ ở từng file.
