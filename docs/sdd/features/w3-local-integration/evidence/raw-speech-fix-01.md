# Raw report — W3 speech correction FIX-01

- Prompt: `W3-PROMPT-003-FIX-01`
- Tasks: `W3-TASK-005`, `W3-TASK-006`
- Base code: `dfac63af857e954acc16de7b22e9ef78ea9f183d`
- Base HEAD: `92474e04bb129691da7e01adcd64c871d54f8c90`
- Source commit: `af5dc8a1e72f01be45e66ef39e1d56afa3058a2f`
- Source commit tree: `2efbd37e6d90f3f44da48a3d39b35c44f173889f`
- Branch: `feat/W3-speech`
- Final acceptance: `PENDING`.

## Đã sửa

1. Adapter Faster-Whisper chỉ yêu cầu đúng bốn file model CTranslate2 trong M03-EV-001: `model.bin`, `config.json`, `tokenizer.json`, `vocabulary.txt`. `preprocessor_config.json` là tùy chọn theo upstream implementation; runtime vẫn truyền `local_files_only=True` và không tải model.
2. Với `weight_name="small"`, adapter tính SHA-256 của cả bốn file so với pin M03 trước khi import/khởi tạo engine. File thiếu, không đọc được hoặc digest không khớp gây `ModelUnavailableError` có thông báo ổn định. Model được hash và khởi tạo một lần rồi tái sử dụng. Các identity khác không qua pin `small`, giữ tên cụ thể để M03 resolver phát `ASR_VERSION_MISMATCH`, không nhận nhầm alias.
3. Silero unit tests mock trực tiếp `silero_vad` import, không chạy model đi kèm package. Thiếu metadata phiên bản được biểu diễn thành `version="unavailable"` và từ chối chạy; `min_silence_ms` chỉ chấp nhận kiểu `int` dương, từ chối cả bool và float.

Các SHA-256 thực đo trên `/tmp/aicefr-w3-models/faster-whisper-small` khớp pin M03-EV-001:

| File | SHA-256 | Kết quả |
| --- | --- | --- |
| `model.bin` | `3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671` | PASS |
| `config.json` | `b55496ac7940a7ae47d2c01eab40edfd8701feec1229d9cce3b40014383fb828` | PASS |
| `tokenizer.json` | `fb7b63191e9bb045082c79fd742a3106a12c99513ab30df4a0d47fa6cb6fd0ab` | PASS |
| `vocabulary.txt` | `34ce3fe1c5041027b3f8d42912270993f986dbc4bb34cf27f951e34a1e453913` | PASS |

Nguồn provenance nội bộ: [M03-EV-001](../../../modules/m03-asr/evidence/evidence-manifest.md#m03-ev-001--weight-whisper-small-ctranslate2). Faster-Whisper source xác nhận thư mục model local được nạp trực tiếp, `local_files_only` áp dụng cho đường tải theo ID, và thiếu preprocessor config dùng cấu hình extractor mặc định: [official upstream implementation](https://raw.githubusercontent.com/SYSTRAN/faster-whisper/master/faster_whisper/transcribe.py). Word timestamps/API cũng được ghi trong [upstream README](https://github.com/SYSTRAN/faster-whisper). Silero API dùng trong adapter được mô tả ở [official repository](https://github.com/snakers4/silero-vad), [timestamps implementation](https://raw.githubusercontent.com/snakers4/silero-vad/master/src/silero_vad/utils_vad.py), và [bundled local model loader](https://raw.githubusercontent.com/snakers4/silero-vad/master/src/silero_vad/model.py).

## Kiểm tra

Lệnh chạy trong `/tmp/aicefr-w3-speech`, import source bằng `PYTHONPATH=src`, dùng venv đã có sẵn. Không cài package trong lane và không gọi model smoke.

| Lệnh | Exit | Kết quả |
| --- | ---: | --- |
| `sha256sum /tmp/aicefr-w3-models/faster-whisper-small/model.bin /tmp/aicefr-w3-models/faster-whisper-small/config.json /tmp/aicefr-w3-models/faster-whisper-small/tokenizer.json /tmp/aicefr-w3-models/faster-whisper-small/vocabulary.txt` | 0 | **PASS**, cả bốn hash khớp pin ở trên. |
| `AICEFR_MODEL_DIR=/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src/aicefr/scoring/models PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python -m pytest -q -m 'not smoke' --cov=aicefr.asr.local --cov=aicefr.features.local --cov=aicefr.asr.service --cov=aicefr.features.extractor --cov=aicefr.scoring.artifact --cov=aicefr.scoring.scorer --cov-branch --cov-report=term-missing --cov-report=json:/tmp/aicefr-w3-speech-fix01-coverage.json` | 0 | **PASS**, 225 passed, 0 skipped; measured package coverage 95% line / 93% branch. |
| `/tmp/aicefr-w3-venv/bin/ruff check src tests scripts` | 0 | **PASS** |
| `python3 scripts/ci/check_md_links.py` | 0 | **PASS**, 143 Markdown files; 16 existing external links skipped, no broken in-repo links. |
| `python3 scripts/ci/check_forbidden_files.py` | 0 | **PASS**, 251 files. |
| `git diff --check` | 0 | **PASS** |
| Real ASR/VAD smoke | — | **NOT_RUN in this lane**. Root will run independently after integrating this correction; no inference/accuracy claim is made here. |

Coverage theo package: ASR local adapter 81% line / 86% branch; VAD local adapter 87% / 79%; ASR service 100% / 100%; feature extractor 100% / 100%; scoring artifact 98% / 96%; scorer 96% / 93%. `/tmp/aicefr-w3-speech-fix01-coverage.json` lưu báo cáo chi tiết. Các nhánh còn thiếu tập trung ở lỗi package/model thật, lỗi filesystem khi đọc hash và các ngoại lệ khởi tạo/inference. Tests mới mock ranh giới hash/import/engine để kiểm soát lỗi và không cần tải model.
