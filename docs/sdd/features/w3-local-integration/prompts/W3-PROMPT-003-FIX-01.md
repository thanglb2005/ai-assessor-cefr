# W3-PROMPT-003-FIX-01 — Bundled review correction

PROMPT ID: W3-PROMPT-003-FIX-01
TASK IDS: W3-TASK-005, W3-TASK-006
SCOPE ROOT: docs/sdd/features/w3-local-integration/
REPO ROOT: /tmp/aicefr-w3-speech
BRANCH: feat/W3-speech
BASE CODE: dfac63af857e954acc16de7b22e9ef78ea9f183d
BASE HEAD: 92474e04bb129691da7e01adcd64c871d54f8c90
AUTHORIZATION: chỉ dẫn trực tiếp của Thắng; gpt-6-luna implement, Codex review; user verdict PENDING.

Đọc prompt gốc và correction này. Giữ allowed files/phân vùng của prompt gốc; không sửa workbook/status/root branch, không tự cài dependency shared venv. Commit correction source/tests riêng, sau đó evidence. Verify BASE HEAD trước sửa; các workbook/prompt metadata dirty là baseline của root, để nguyên. Không yêu cầu fingerprint cũ sau implementation.

MAJOR-01: FasterWhisperEngine yêu cầu preprocessor_config.json, nhưng model M03 đã ghim revision 536b0662742c02347bc0e980a01041f333bce120 chỉ gồm model.bin, config.json, tokenizer.json, vocabulary.txt. Root đã tải và verify đủ bốn file vào /tmp/aicefr-w3-models/faster-whisper-small. Sửa requirement theo local CTranslate2 thực tế; preprocessor không bắt buộc. Không auto-download runtime. Primary source: M03-EV-001 và faster-whisper official source.

MAJOR-02: weight_name hiện lấy trực tiếp từ operator để gắn provenance; bất kỳ model khác có thể bị dán nhãn small. Trước khi nhận canonical whisper-small, verify weights bằng SHA256 pin M03 (model.bin 3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671; config b55496ac7940a7ae47d2c01eab40edfd8701feec1229d9cce3b40014383fb828; tokenizer fb7b63191e9bb045082c79fd742a3106a12c99513ab30df4a0d47fa6cb6fd0ab; vocabulary 34ce3fe1c5041027b3f8d42912270993f986dbc4bb34cf27f951e34a1e453913). Không âm thầm nhận model không khớp; controlled ModelUnavailableError. Các identity khác chưa được phê duyệt phải từ chối hoặc giữ mismatch, tuyệt đối không dán small. Unit tests mock pin/hash boundary một cách tường minh để không cần model thật; thêm mismatch/tamper/refusal/cache tests.

MAJOR-03: test_missing_silero_package chỉ mock version, không mock import. Khi Silero thật được cài test sai/không deterministic. Mock import boundary, kiểm tra dependency thiếu mà không chạy bundled model thật trong unit test. Bundle validation min_silence_ms là integer dương (không bool/float bị truncate) và missing package version semantics.

Root đang cài optional ASR/VAD và bộ torch/torchaudio CPU cùng phiên bản; sẽ báo khi sẵn sàng. User đã xác nhận quyền dùng audio local nhưng không gửi path; root tìm thấy audio ở repo nội bộ ngoài Git. Không claim real smoke từ unit mocks. Khi được thông báo môi trường sẵn sàng, hỗ trợ smoke adapter thật nếu cần, chỉ metadata/timing/hash/version/reasons vào evidence; không commit audio/model/transcript. WER/CEFR accuracy chưa có ground truth nên NOT_MEASURED.

Chạy unit/full regression với PYTHONPATH=src và AICEFR_MODEL_DIR=/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src/aicefr/scoring/models; Ruff và coverage các changed adapters. Report coverage/gaps đúng, không đổi thresholds/exclusions. Output evidence/raw-speech-fix-01.md, dẫn source commit và findings đã resolve. Return source/evidence SHA.
