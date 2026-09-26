# M05 — Evidence Manifest (danh mục bằng chứng)

**Hiện trạng:** có evidence Phase 06 của M05-TASK-002 (M05-EV-001) và M05-TASK-001 (M05-EV-002); chưa qua Phase 07 review. Báo cáo và hình W1 cấp dự án nằm ở docs/reports/week-01/ và docs/design/week-01/.

| Evidence ID | Prompt ID / Task ID | Phase | Base/Head revision, fingerprint | Loại / file hoặc link | Check và kết quả thực tế | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| M05-EV-001 | M05-TASK-002 (Jira SCRUM-27); Claude implement theo yêu cầu chủ dự án, không qua prompt Antigravity | 06 | base `9884170` trên `main` | PR `[SCRUM-27]`, xem mục dưới | Test ID 005–007, 015–019 chạy thật; coverage `aicefr.scoring` 100 % line/branch | RECORDED — chờ Phase 07 |
| M05-EV-002 | M05-TASK-001 (Jira SCRUM-28); Claude implement theo yêu cầu chủ dự án | 06 | trên nhánh của M05-EV-001 | `scoring/scorer.py`, `scoring/coverage.py`, `tests/scoring/test_scorer.py` | Test ID 001–004, 008–014, 020, 021 chạy thật; coverage `aicefr.scoring` 100 % line/branch | RECORDED — chờ Phase 07 |

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

## M05-EV-002 — M05-TASK-001 scorer 8 bước + coverage 5 tiêu chí

| Lệnh | Kết quả |
| --- | --- |
| `env -u AICEFR_MODEL_DIR python -m pytest -q -m "not smoke" --cov=aicefr.scoring --cov-branch` (giống CI) | 52 passed, 9 skipped; `artifact.py`, `coverage.py`, `ridge.py`, `scorer.py` đều 100 % line/branch |
| `AICEFR_MODEL_DIR=<thư mục artifact> python -m pytest -q -m "not smoke" --cov=aicefr --cov-branch` | 61 passed; toàn repo 98 % |
| `ruff check src tests` · `ruff format --check src tests` | sạch |

| Test ID | Test | Kết quả |
| --- | --- | --- |
| M05-TEST-001 | `test_golden_vectors_on_real_artifact` ×3 (mean 3,9465 B2 REVIEW; lo 2,2575 A2 REVIEW; hi 4,9414 B2 ESTIMATED) + provenance đọc từ artifact | PASS (ART-REAL) |
| M05-TEST-002 | `test_score_is_deterministic_apart_from_timestamp` | PASS |
| M05-TEST-003 | `test_full_features_give_full_coverage_without_scores` (fluency = 1,0) | PASS (ART-REAL) |
| M05-TEST-004 | `test_every_assessment_has_insufficient_evidence_interaction` | PASS |
| M05-TEST-008 | `test_transcript_not_ok_is_not_evaluated_and_keeps_m03_reason` | PASS |
| M05-TEST-009/010/012/013 | `test_provenance_mismatch_is_not_evaluated` ×7 (thêm vad_threshold, vad_min_silence_ms, feature_version) | PASS |
| M05-TEST-011 | `test_swapped_feature_order_is_not_evaluated` | PASS |
| M05-TEST-014 | `test_missing_feature_is_not_evaluated_with_null_coverage` | PASS |
| M05-TEST-020 | `test_coverage_with_one_missing_fluency_feature` (0,80) | PASS |
| M05-TEST-021 | `test_log_has_ids_and_status_but_no_feature_values` | PASS |

**Thay đổi contract (phần M05):** thêm `OutOfRangeFeature` và `Assessment.out_of_range` để trả chi tiết OOD như Spec bước 6 yêu cầu; M06 dùng để báo giới hạn cho người học. Test chạy được trên CI nhờ fixture ART-FAKE18 có đúng 18 tên đặc trưng của Ridge v2.
