# Raw implementation report — W3 app lane

PROMPT ID: W3-PROMPT-002
TASK IDS: W3-TASK-003, W3-TASK-004
BASE REVISION: `7bb327b655c67d8eb5aafc4cd8ec9481fabdff28`
BASE SOURCE REVISION: `2b428ceea9e4459f3235d4ce67f10bab31585ebf`
STARTING WORKSPACE FINGERPRINT: `7b2ec2c41aca165ee429b50e0e1afd1158066055616d602f7ec7ed8c6626678c`
SOURCE COMMIT: `6415e117109ccfd2dda57284e9e9e1933779b6a3`
SOURCE TREE: `14adf3a16308759a640562d8ff9dad35cdeba8ff`
POST-SOURCE WORKSPACE FINGERPRINT: `82124769e99bebc7294ea69d57490ac0906e62682d4fffed2420171c212fe266`
ALGORITHM: `sdd-workspace-v2`; metadata file: `prompts/W3-PROMPT-002-app.md`; no exclusions.
FINAL USER VERDICT: PENDING.

## Thay đổi đã triển khai

- Thêm `python -m aicefr.local` với `init-demo` tạo account fixture bằng `getpass` hoặc stdin và `serve` bind loopback. Lệnh serve yêu cầu `--config` hoặc lựa chọn `--demo` tường minh. Cấu hình QC demo chỉ được tạo từ cờ `--demo`, UI ghi rõ local/synthetic.
- Composition root lắp SQLite, blob, auth/session, consent, response, report, review và student services. Adapter ASR/VAD được nạp lười; không có đường tải model. Scorer tiếp tục gọi loader SHA-256 đang có. Khi thiếu model/adapter, các service M03/M04/M05 hiện hành quyết định trạng thái chưa đánh giá; app không cấp transcript hoặc điểm mẫu.
- Thêm login/logout, cookie `HttpOnly; SameSite=Lax; Path=/`, thu hồi session server-side, consent accept/withdraw và kiểm Origin loopback cho POST dùng cookie. Bearer token hiện có vẫn dùng được cho API.
- Form upload chuyển hướng tới trang status; route JSON `POST /api/student/responses` giữ response JSON. Teacher queue mở report/candidate detail, nghe audio chỉ khi response có candidate, và gửi approve/override/reject qua service review hiện có. Error của browser được giới hạn và không đưa path, input hay stack trace vào response.
- Test fixture xác nhận session tồn tại qua lần mở lại SQLite, logout thu hồi token, CSRF/Origin, rút consent chặn lưu blob, student bị từ chối audio và teacher mở được audio/report. Test CLI provisioning xác nhận mật khẩu stdin không xuất hiện trong output.

## Lệnh và kết quả

| Lệnh | Exit | Kết quả |
| --- | ---: | --- |
| `PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python -m pytest -q -m 'not smoke'` | 0 | PASS — 194 passed, 10 skipped. 10 test scoring/features được skip vì thiếu `AICEFR_MODEL_DIR`; không tải model. |
| `PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python -m pytest tests/local tests/api/test_local_sessions.py tests/api/test_student.py --cov=aicefr.local --cov=aicefr.api.wsgi --cov=aicefr.api.templates --cov=aicefr.auth.service --cov-branch --cov-report=term-missing --cov-report=json:/tmp/aicefr-w3-app-coverage.json -q` | 0 | PASS — 19 passed. Line/branch tổng các package đo: 68% line. Chi tiết dưới đây. |
| `/tmp/aicefr-w3-venv/bin/ruff check src tests` | 0 | PASS. |
| `PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python -m aicefr.local --help` | 0 | PASS — CLI hiển thị `init-demo`, `serve`. |
| `git diff --check` | 0 | PASS trước khi commit source. |
| Browser QA W3-TEST-007 | — | NOT_RUN — pipeline/report repository và các lane tích hợp chưa có trong base worktree; server end-to-end chưa thể khởi chạy từ commit lane độc lập này. |
| ASR/VAD thật | — | NOT_RUN — không có artifact ASR/audio được cấp cho smoke; adapter speech thuộc lane khác. |

Coverage từ báo cáo `/tmp/aicefr-w3-app-coverage.json`:

| Package/file | Line coverage | `BrPart` từ báo cáo nhánh coverage.py |
| --- | ---: | ---: |
| `aicefr.api.templates` | 85% | 7 partial branches |
| `aicefr.api.wsgi` | 72% | 43 partial branches |
| `aicefr.auth.service` | 87% | 5 partial branches |
| `aicefr.local.__main__` | 49% | 3 partial branches |
| `aicefr.local.app` | 38% | 0 branch executed |
| Tổng phạm vi đo | 68% | 58 partial branches |

Các nhánh quan trọng còn chưa được đo là composition factory và server/browser startup trong `local.app`/`local.__main__`, do import contract `aicefr.report.sqlite.SQLiteReportRepository` chưa có ở baseline app worktree. WSGI còn nhiều nhánh API teacher/student ngoài các đường được chạy. Coverage ở đây không phải tiêu chí pass/fail toàn repo; không đặt threshold mới.

## Giới hạn và phụ thuộc tích hợp

`create_runtime` dùng đúng public contract đã chốt: `PipelineCoordinator(*, responses, reports, reviews, qc_config, asr, extractor, scorer)` và `SQLiteReportRepository(store)`. Hai import này không tồn tại trong base worktree tại thời điểm triển khai; report lane/root cần tích hợp chúng trước khi chạy server end-to-end. Import `aicefr.report.sqlite` là bắt buộc để mở runtime vì báo cáo bền vững là yêu cầu; lỗi startup được CLI trả dưới thông báo chung. Không thêm fallback memory/fake cho production composition.

Mục tiêu và contract được đối chiếu tại `01-requirement.md`, `03-specification.md`, `04-test-plan.md` và `06-tasks.md` trong scope W3. Prompt đầy đủ được lưu ở `prompts/W3-PROMPT-002-app.md`. Không chỉnh workbook, prompt-log, source lane khác, SDD status hoặc README; chúng còn là thay đổi ngoài phạm vi worktree này.
