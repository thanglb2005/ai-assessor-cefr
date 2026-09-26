# M03 — Evidence Manifest (danh mục bằng chứng)

**Hiện trạng:** chưa có implementation/test evidence của repo dự án. Đã có evidence chuẩn bị môi trường M03-EV-001 (weight ASR). Báo cáo và hình W1 cấp dự án nằm ở docs/reports/week-01/ và docs/design/week-01/.

| Evidence ID | Prompt ID / Task ID | Phase | Base/Head revision, fingerprint | Loại / file hoặc link | Check và kết quả thực tế | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| M03-EV-001 | SCRUM-21 (việc tay M03-O1 / DEP-05) | 05 — chuẩn bị dependency | Không áp dụng (tải ngoài repo, không đổi source) | Weight ASR, xem mục dưới | SHA-256 `model.bin` khớp giá trị LFS chính thức trên Hugging Face | RECORDED |
| M03-EV-002 | M03-TASK-003, 004, 001 (Jira SCRUM-18, 19, 20); Claude implement theo yêu cầu chủ dự án | 06 | base `e92c1cf` trên `main` | `src/aicefr/asr/`, `tests/asr/`, xem mục dưới | Test ID 001–016 chạy thật; coverage `aicefr.asr` ≥ 99 % line/branch | RECORDED — chờ Phase 07 |

Lưu tại đây raw report của Antigravity, command output/test/coverage, ảnh browser QA và final verification khi phát sinh. File lớn có thể lưu ngoài Git nhưng phải có link ổn định, checksum và quyền truy cập cho người review. Mỗi evidence gắn đúng Prompt ID, Task ID, AC/Test ID và revision. Redact secret/PII/audio/transcript thật; không ghi PASS cho lệnh chưa chạy. Cập nhật 07-status.md trỏ tới evidence mới nhất.

## M03-EV-001 — Weight `whisper-small` (CTranslate2)

Tải có chủ đích theo M03-D-001 (`whisper-small`), M03-D-002 (không tự tải khi chạy) và M03-O-001 (faster-whisper). Weight **không** nằm trong Git.

| Mục | Giá trị |
| --- | --- |
| Nguồn | Hugging Face `Systran/faster-whisper-small` |
| Revision ghim | `536b0662742c02347bc0e980a01041f333bce120` |
| License | MIT (khai báo trong model card) |
| Ngày tải | 26/09/2026, máy của Sang (macOS 26.4, Apple M5, 24 GiB RAM) |
| Nơi lưu | `~/models/faster-whisper-small/` — ngoài repo; `.gitignore` bỏ qua `models/` và CI chặn `*.bin` |
| Lệnh | `curl -sSfL https://huggingface.co/Systran/faster-whisper-small/resolve/<revision>/<file>` cho từng file, rồi `shasum -a 256` |

| File | Kích thước (byte) | SHA-256 |
| --- | --- | --- |
| `model.bin` | 483 546 902 | `3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671` |
| `config.json` | 2 370 | `b55496ac7940a7ae47d2c01eab40edfd8701feec1229d9cce3b40014383fb828` |
| `tokenizer.json` | 2 203 239 | `fb7b63191e9bb045082c79fd742a3106a12c99513ab30df4a0d47fa6cb6fd0ab` |
| `vocabulary.txt` | 459 861 | `34ce3fe1c5041027b3f8d42912270993f986dbc4bb34cf27f951e34a1e453913` |

**Kiểm tra:** SHA-256 của `model.bin` trùng giá trị LFS mà API Hugging Face công bố cho revision trên. Chưa chạy model; smoke M03-TEST-S1/S2 vẫn `NOT_RUN` (chờ audio có quyền dùng và DEP-01..04).

## M03-EV-002 — M03-TASK-003, 004, 001 (bộ phát hiện hallucination, ánh xạ identifier, dịch vụ ASR)

**Môi trường:** macOS 26.4, Python 3.12.14, base `e92c1cf`. Unit test dùng `FakeAsrEngine` (test_only), không import faster-whisper, không cần model hay audio.

| Lệnh | Kết quả |
| --- | --- |
| `python -m pytest -q tests/asr` | 44 passed |
| `python -m pytest -q -m "not smoke" --cov=aicefr --cov-branch` (toàn repo, không artifact) | 122 passed, 10 skipped; `asr/service.py`, `identity.py`, `validation.py` 100 %; `hallucination.py` 99 % |
| `ruff check src tests` · `ruff format --check src tests` | sạch |

| Test ID | Test | Kết quả |
| --- | --- | --- |
| M03-TEST-001 | `test_ok_transcript_keeps_order_filler_and_provenance` | PASS |
| M03-TEST-002 | `test_missing_probability_stays_none` (regression REF-03) | PASS |
| M03-TEST-003 | `test_engine_error_or_timeout_is_asr_failed` ×2 | PASS |
| M03-TEST-004 | `test_invalid_words_are_asr_failed_without_words` ×5, `test_invalid_timestamps_are_reported` ×4 | PASS |
| M03-TEST-005 | `test_qc_reject_does_not_call_engine` | PASS |
| M03-TEST-006 | `test_missing_model_is_not_run_without_download` | PASS |
| M03-TEST-007 | `test_empty_transcript_is_unreliable` ×2 | PASS |
| M03-TEST-008 | `test_consecutive_token_repeats` (6 / 7) | PASS |
| M03-TEST-009 | `test_single_token_share` (21/60, 22/60, 59 từ) | PASS |
| M03-TEST-010 | `test_phrase_repeated_back_to_back` (2 / 3) | PASS |
| M03-TEST-011 | `test_low_probability_tail` (4 / 5) | PASS |
| M03-TEST-012 | `test_stalled_clock` (3 / 4) | PASS |
| M03-TEST-013 | `test_mapped_weight_resolves_to_canonical_id`, `test_matching_weight_has_no_mismatch` | PASS |
| M03-TEST-014 | `test_unmapped_weight_is_none_and_mismatch` ×3, `test_english_only_weight_is_mismatch_but_status_unchanged` (regression F-04) | PASS |
| M03-TEST-015 | `test_custom_map_and_other_model_mismatch`, `test_other_model_is_mismatch_but_status_unchanged` | PASS |
| M03-TEST-016 | `test_log_does_not_contain_transcript_text` | PASS |

**Cách hiểu cần owner xác nhận ở Phase 07:** luật "cụm 3–10 từ lặp ≥ 3 lần" được hiện thực là lặp **liền nhau** (như "i like it i like it i like it"). Đếm cả lặp rời rạc sẽ gắn cờ nhầm lời nói bình thường ("i think that" xuất hiện 3 lần trong 60 giây).
