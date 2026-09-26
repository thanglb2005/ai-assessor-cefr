# M05 — Evidence Manifest (danh mục bằng chứng)

**Hiện trạng:** có evidence Phase 06 của M05-TASK-002 (M05-EV-001); chưa qua Phase 07 review. Báo cáo và hình W1 cấp dự án nằm ở docs/reports/week-01/ và docs/design/week-01/.

| Evidence ID | Prompt ID / Task ID | Phase | Base/Head revision, fingerprint | Loại / file hoặc link | Check và kết quả thực tế | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| M05-EV-001 | M05-TASK-002 (Jira SCRUM-27); Claude implement theo yêu cầu chủ dự án, không qua prompt Antigravity | 06 | base `9884170` trên `main` | PR `[SCRUM-27]`, xem mục dưới | Test ID 005–007, 015–019 chạy thật; coverage `aicefr.scoring` 100 % line/branch | RECORDED — chờ Phase 07 |

Lưu tại đây raw report của Antigravity, command output/test/coverage, ảnh browser QA và final verification khi phát sinh. File lớn có thể lưu ngoài Git nhưng phải có link ổn định, checksum và quyền truy cập cho người review. Mỗi evidence gắn đúng Prompt ID, Task ID, AC/Test ID và revision. Redact secret/PII/audio/transcript thật; không ghi PASS cho lệnh chưa chạy. Cập nhật 07-status.md trỏ tới evidence mới nhất.

## M05-EV-001 — M05-TASK-002 loader artifact + toán chấm Ridge

**Môi trường:** macOS 26.4, Python 3.12.14 (`.venv` qua uv), base `9884170`. Artifact thật đặt ngoài repo (P05-D-001).

| Lệnh | Kết quả |
| --- | --- |
| `env -u AICEFR_MODEL_DIR python -m pytest -q -m "not smoke"` (giống CI, không có artifact) | 32 passed, 5 skipped (5 test cần ART-REAL báo SKIPPED, không tính PASS) |
| `AICEFR_MODEL_DIR=<thư mục chứa ridge_resp_v2.json> python -m pytest -q -m "not smoke" --cov=aicefr --cov-branch` | 37 passed; `scoring/artifact.py` 100 %, `scoring/ridge.py` 100 % (line và branch) |
| `ruff check .` · `ruff format --check src tests` | sạch |

| Test ID | Test | Kết quả |
| --- | --- | --- |
| M05-TEST-005 | `test_load_artifact_missing_file_reports_model_version_missing` | PASS |
| M05-TEST-006 | `test_load_artifact_one_byte_changed_reports_artifact_invalid` (ART-REAL), `…hash_mismatch_on_fake…` | PASS |
| M05-TEST-007 | `test_load_artifact_wrong_unit_of_inference_is_rejected` ×2, `…missing_unit_field…` | PASS |
| M05-TEST-015 | `test_total_dur_just_below_accepted_high_is_not_ood`, `…above_accepted_high_is_ood_with_detail` (ART-REAL) | PASS |
| M05-TEST-016 | `test_to_band_boundaries` ×4 | PASS |
| M05-TEST-017 | `test_near_boundary_with_margin_half` ×4 | PASS |
| M05-TEST-018 | `test_predict_clips_to_score_range` ×2 | PASS |
| M05-TEST-019 | `test_predict_uses_one_when_scale_is_zero` | PASS |

**Ghi chú triển khai:** artifact ghi `unit_of_inference` không dấu (`mot bai noi …`), nên loader chấp nhận cả "một bài nói" và "mot bai noi". Chuỗi đó cũng chứa "khong phai ca bai thi", vì vậy điều kiện là *có* dấu hiệu một bài nói, không phải *không có* "ca bai thi".
