# M04 — Evidence Manifest (danh mục bằng chứng)

**Hiện trạng:** có evidence Phase 06 của M04-TASK-001, 002 (M04-EV-001); chưa qua Phase 07 review. Báo cáo và hình W1 cấp dự án nằm ở docs/reports/week-01/ và docs/design/week-01/.

| Evidence ID | Prompt ID / Task ID | Phase | Base/Head revision, fingerprint | Loại / file hoặc link | Check và kết quả thực tế | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| M04-EV-001 | M04-TASK-001, 002 (Jira SCRUM-24, 25); Claude implement theo yêu cầu chủ dự án | 06 | base `e92c1cf` trên `main` | `src/aicefr/features/`, `tests/features/`, xem mục dưới | Test ID 001–015, 017, 018 chạy thật; coverage `aicefr.features` 100 % | RECORDED — chờ Phase 07 |

Lưu tại đây raw report của Antigravity, command output/test/coverage, ảnh browser QA và final verification khi phát sinh. File lớn có thể lưu ngoài Git nhưng phải có link ổn định, checksum và quyền truy cập cho người review. Mỗi evidence gắn đúng Prompt ID, Task ID, AC/Test ID và revision. Redact secret/PII/audio/transcript thật; không ghi PASS cho lệnh chưa chạy. Cập nhật 07-status.md trỏ tới evidence mới nhất.

## M04-EV-001 — M04-TASK-001 (18 công thức) và M04-TASK-002 (FeatureExtractor)

**Môi trường:** macOS 26.4, Python 3.12.14, base `e92c1cf`. Unit test dùng `FakeVad`, không import torch/silero.

| Lệnh | Kết quả |
| --- | --- |
| `python -m pytest -q tests/features` (không artifact) | 26 passed, 1 skipped (M04-TEST-010 cần ART-REAL) |
| `AICEFR_MODEL_DIR=<thư mục artifact> python -m pytest -q -m "not smoke"` (toàn repo) | 132 passed |
| coverage `aicefr.features` | `text.py`, `pauses.py`, `extractor.py` 100 % line/branch |

| Test ID | Test | Kết quả |
| --- | --- | --- |
| M04-TEST-001 | `test_text_features_match_expected_table`, `test_pause_features_match_expected_table`, `test_full_fixture_gives_18_values_with_units` (sai số 1e-6) | PASS |
| M04-TEST-002 | `test_gap_and_tail_of_exactly_030_s_are_not_pauses` | PASS |
| M04-TEST-003 | `test_no_pause_gives_measured_zero_not_missing` | PASS |
| M04-TEST-004, 011 | `test_unreliable_transcript_nulls_transcript_features_only` | PASS |
| M04-TEST-005 | `test_lexical_features_need_ten_tokens` (9 / 10) | PASS |
| M04-TEST-006 | `test_no_probability_gives_missing_confidence_not_zero` | PASS |
| M04-TEST-007 | `test_empty_segments_give_missing_vad_features_not_zero` (regression REF-04) | PASS |
| M04-TEST-008 | `test_zero_duration_nulls_all_18` | PASS |
| M04-TEST-009 | `test_nan_timestamp_propagates_only_to_affected_features`, `test_nan_becomes_none_with_reason` | PASS |
| M04-TEST-010 | `test_order_follows_real_artifact_without_filler_ratio` | PASS (ART-REAL) |
| M04-TEST-012 | `test_unknown_feature_name_is_config_error` | PASS |
| M04-TEST-013 | `test_model_feature_version_mismatch_is_flagged` | PASS |
| M04-TEST-014 | `test_silero_parameters_recorded_without_mismatch` | PASS |
| M04-TEST-015 | `test_other_vad_configuration_is_flagged` ×3 | PASS |
| M04-TEST-017 | `test_feature_set_and_log_do_not_leak_transcript` | PASS |
| M04-TEST-018 | `test_extraction_is_deterministic_and_unrounded` | PASS |

**Khác biệt so với Test Plan, cần owner xác nhận ở Phase 07:**
- M04-TEST-008: contract `DecodedAudio` chặn `duration_s < 0` ngay khi tạo, nên chỉ kiểm được D = 0.
- M04-TEST-009: contract `Word` chặn `prob` NaN, nên NaN được đưa vào qua timestamp segment VAD.
- So ngưỡng 0,30 s và 1,00 s có sai số 1e-9 (timestamp VAD ở mức mili-giây), để khoảng đúng 0,30 s không bị tính là ngừng do lỗi dấu phẩy động.
- M04-TEST-016 thuộc M04-TASK-003 (Silero, BLOCKED), chưa làm.
