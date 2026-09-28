# M02 — 04 Test Plan (Kế hoạch kiểm thử)

> **W2 v0.2 · 28/09/2026 · Phase 04 APPROVED by Thắng.** Specification v0.3 đã được user duyệt Phase 03. Test chưa chạy; Phase 04 đã được duyệt, Phase 05 vẫn pending trước khi triển khai.

Mọi ca dùng signal/audio bytes tổng hợp do nhóm tạo, QCConfig versioned có giá trị tường minh và temporary files. Không dùng audio người học, không gửi mạng và không ghi raw audio vào log.

| Test ID | FR/AC | Level | Tình huống | Kỳ vọng | Test file dự kiến |
| --- | --- | --- | --- | --- | --- |
| M02-TEST-001 | M02-FR-001 / M02-AC-001 | Unit | Bytes rỗng, sai/corrupt, unsupported subtype | REJECT với reason ổn định; không có samples được chuyển tiếp | `tests/audio/test_decoder.py` |
| M02-TEST-002 | M02-FR-001 / M02-AC-001 | Unit/boundary | Vượt max bytes, input rate hoặc frame/duration cap trong QCConfig | Vượt bất kỳ hard resource cap nào trả REJECT với reason xác định; dừng đọc tại frame cap, không cấp phát payload không giới hạn; không tạo transcript/score | `tests/audio/test_decoder.py` |
| M02-TEST-003 | M02-FR-002 / M02-AC-002 | Unit | Signal tổng hợp có đoạn im lặng và sample clipped với ngưỡng test config biết trước | Duration (s), silence ratio và clipped ratio khớp phép tính sample-level; value/unit/missing reason đúng; gắn config version | `tests/qc/test_measurements.py` |
| M02-TEST-004 | M02-FR-002 / M02-AC-002 | Unit | Decode signal mono và resample từ input rate hợp lệ hai lần với cùng config | PCM 1-D `float32`, 16 kHz, duration/hash đúng; kết quả xác định trong tolerance ghi tại assertion | `tests/audio/test_decoder.py` |
| M02-TEST-005 | M02-FR-001 / M02-AC-001 | Boundary | Extension/declared format không khớp bytes thực | REJECT với safe reason; không leak decoder message | `tests/audio/test_decoder.py` |
| M02-TEST-006 | M02-FR-001/002 / M02-AC-001/002 | Unit | WAV PCM, FLAC, OGG/Vorbis và MP3 trong whitelist; mono/stereo và >2 channels | Format được duyệt giải mã thành contract PCM; stereo dùng arithmetic mean; trên 2 channels REJECT | `tests/audio/test_decoder.py` |
| M02-TEST-007 | M02-FR-001/002 / M02-AC-001/002 | Unit | Min-duration/metric policy config đặt signal vào từng outcome | PASS/REVIEW/REJECT và reason/measurement/version đúng config; không có implicit production default | `tests/qc/test_policy.py` |
| M02-TEST-008 | M02-FR-001 / M02-AC-001 | Pipeline boundary | Chạy pipeline với từng QCStatus và ASR spy | PASS gọi ASR đúng một lần; REVIEW chờ explicit review, REJECT không gọi; non-PASS không tạo transcript/score | `tests/audio/test_pipeline.py` |

## Mapping và lệnh dự kiến

| Mục | Lệnh / phạm vi |
| --- | --- |
| Cài môi trường dev | `python3 -m pip install -e '.[dev]'` |
| Unit + boundary | `python3 -m pytest -q -m "not smoke" tests/audio tests/qc` |
| Coverage branch | `python3 -m pytest -q -m "not smoke" --cov=aicefr.audio --cov=aicefr.qc --cov-branch --cov-report=term-missing tests/audio tests/qc` |
| Shared contract | `python3 -m pytest -q tests/test_contracts.py` |
| Coverage đề xuất | Line ≥ 90% và branch ≥ 85% trên logic thuần `aicefr.audio`/`aicefr.qc`; mọi nhánh format/resource/QC/pipeline gate cần assertion. TP-D-001 hiện chỉ áp dụng M03/M04/M05; đề xuất mở rộng ngưỡng tương tự cho M02. |
| Smoke/browser | N/A cho W2: không có audio thật được duyệt hoặc UI/API; mọi test dùng fixture tổng hợp. |

## Bằng chứng Phase 06/08

Ghi lệnh, thời gian, exit code, pass/fail/skip, line/branch coverage, revision/fingerprint và evidence path. Không báo test format PASS nếu libsndfile build không hỗ trợ; nếu target runtime thiếu format bắt buộc, đây là FAIL cần sửa dependency/package, không chuyển thành skip im lặng.

**CODEX CHECK RESULT:** PASS — cả hai AC được ánh xạ; command tương thích pytest/pytest-cov hiện có; coverage target được duyệt. **User verdict Phase 04:** APPROVED theo đề xuất · 28/09/2026.
