# W3 model provenance — speech lane

Ngày kiểm tra: 02/10/2026 (Asia/Ho_Chi_Minh). Đây là metadata quan sát được từ artifact nội bộ do nhóm tạo; artifact và weights không được sao chép vào repo dự án.

## Scoring artifact

- Nguồn nội bộ: `../ai-assessor-cefr-thamchie/src/aicefr/scoring/models/ridge_resp_v2.json` (ngoài repo, chỉ đọc).
- SHA-256 đo từ bytes: `7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a`, khớp hằng pin `RIDGE_RESP_V2_SHA256` trong repo dự án.
- Metadata đọc được: `model_version=ridge_resp_v2`, `feature_version=v3`, 18 đặc trưng; `trained_with.asr_model=whisper-small`, `vad_name=silero`, `vad_threshold=0.5`, `vad_min_silence_ms=150`; đơn vị suy luận là một bài nói (một file audio), không phải cả bài thi.
- Artifact không được đưa vào Git. Hash mismatch, schema sai, vector sai hình dạng hoặc số không hữu hạn bị từ chối. `scale <= 0` bị scorer từ chối bằng `MODEL_ARTIFACT_INVALID`; không dùng hệ số 1 thay thế trong scoring.

## ASR/VAD adapters

- Faster-Whisper API được đối chiếu với tài liệu upstream chính thức: [SYSTRAN/faster-whisper README](https://github.com/SYSTRAN/faster-whisper) và [WhisperModel API source](https://raw.githubusercontent.com/SYSTRAN/faster-whisper/master/faster_whisper/transcribe.py). Adapter nạp thư mục đã tồn tại, buộc `local_files_only=True`, yêu cầu các file model/tokenizer cần thiết hiện diện, đặt language English và bật word timestamps. Không tải weights hoặc audio.
- Silero API được đối chiếu với [snakers4/silero-vad README](https://github.com/snakers4/silero-vad), [official VAD utility source](https://raw.githubusercontent.com/snakers4/silero-vad/master/src/silero_vad/utils_vad.py), và [bundled model loader source](https://raw.githubusercontent.com/snakers4/silero-vad/master/src/silero_vad/model.py). Adapter gọi `load_silero_vad(onnx=False)` để dùng model JIT đi kèm package, rồi yêu cầu timestamps theo giây từ mono float32 16 kHz. Không dùng `torch.hub`.
- Package versions được lấy từ metadata của môi trường chạy. Unit tests mock boundary và không khẳng định engine thật đã chạy.

## Giới hạn xác nhận

Không có local Faster-Whisper weights hoặc audio được cho phép dùng làm smoke fixture trong lane này; smoke ASR thật là `NOT_RUN`. Silero package/model cũng không được cài trong venv kiểm thử. Không có phép đo WER, VAD accuracy hoặc CEFR accuracy từ công việc này.
