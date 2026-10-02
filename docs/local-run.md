# Chạy W3 local

Ứng dụng WSGI chạy một process trên loopback với tài khoản fixture do người chạy tạo. SQLite, audio và model nằm ngoài repository. Cấu hình demo dành cho dữ liệu kiểm thử do nhóm tạo; chưa có nghiệm thu vận hành dữ liệu người học thật hay validation độ chính xác CEFR.

## Cài đặt và chạy demo

Từ thư mục repository, dùng Python >=3.11:

```bash
python3 -m venv /tmp/aicefr-local-venv
source /tmp/aicefr-local-venv/bin/activate
python -m pip install -e '.[dev]'
python -m aicefr.local init-demo --data-dir /tmp/aicefr-local-data --actor-id fixture-student --role student
python -m aicefr.local init-demo --data-dir /tmp/aicefr-local-data --actor-id fixture-teacher --role teacher
python -m aicefr.local serve --data-dir /tmp/aicefr-local-data --demo --port 8000
```

CLI hỏi mật khẩu bằng `getpass`; không có mật khẩu mặc định. ID phải bắt đầu `fixture-`. Có thể dùng `--password-stdin` trong automation local, không đặt mật khẩu trong command argument hay Git. Mở `http://127.0.0.1:8000/login`. Student đồng ý phiên bản `demo-v1`, rồi nộp bài `demo-speaking`, phiên bản `1`. Nếu không cấu hình ASR/model, report không đưa band AI. Teacher đăng nhập tài khoản riêng, mở hàng đợi, xem report/nghe audio và ghi quyết định; overall AI giữ nguyên.

Tạo một WAV kiểm thử 3 giây, có khoảng lặng để đi nhánh QC REVIEW mà không cần ASR:

```bash
python - <<'PY'
from pathlib import Path
import numpy as np
import soundfile as sf
path = Path('/tmp/aicefr-local-fixture.wav')
samples = np.zeros(48000, dtype=np.float32)
t = np.arange(14400) / 16000
samples[:14400] = 0.15 * np.sin(2 * np.pi * 220 * t)
sf.write(path, samples, 16000, subtype='PCM_16')
print(path)
PY
```

Đây là audio kiểm thử kỹ thuật, không có lời nói và không dùng để chứng minh chất lượng ASR/CEFR. Teacher override trên bài này chỉ chứng minh luồng lưu quyết định.

## Cấu hình model local

Whisper dùng đúng Systran/faster-whisper-small revision `536b0662742c02347bc0e980a01041f333bce120`, đã ghim tại [M03 model provenance](sdd/modules/m03-asr/evidence/evidence-manifest.md). Chuẩn bị model ngoài Git trước khi chạy; runtime chỉ đọc file local và kiểm checksum. Ridge dùng `ridge_resp_v2.json`, SHA256 `7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a`; đặt `model_artifact` trong config hoặc `AICEFR_MODEL_DIR` trỏ thư mục chứa artifact. Không giảm pin hoặc thay band mapping để ép có điểm.

Cài optional extras cho ASR/VAD. Với máy CPU, cài torch và torchaudio **cùng phiên bản** từ CPU index trước để tránh tải dependencies GPU. Sau đó cài extras của repo:

```bash
python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e '.[dev,asr,vad]'
```

W3 đã kiểm tra với faster-whisper1.2.1, CTranslate2 4.8.2, Silero6.2.1 và torch/torchaudio2.11.0+cpu. Nguồn cài CPU: [PyTorch](https://pytorch.org/get-started/locally/). Kiểm lại phiên bản torch/torchaudio nếu resolver chọn hai phiên bản khác nhau.

Tạo `/tmp/aicefr-local-config.json` theo mẫu dưới đây và thay hai đường dẫn model bằng đường dẫn thực. Đây vẫn là cấu hình demo, QC chưa được xem là ngưỡng vận hành đã nghiệm thu:

```json
{
  "demo": true,
  "consent_version": "demo-v1",
  "model_artifact": "/absolute/path/ridge_resp_v2.json",
  "asr_model_dir": "/absolute/path/faster-whisper-small",
  "asr_weight_name": "small",
  "asr_device": "cpu",
  "asr_compute_type": "int8",
  "vad_enabled": true,
  "vad_threshold": 0.5,
  "vad_min_silence_ms": 150,
  "allowed_media_types": ["audio/wav", "audio/flac", "audio/ogg", "audio/mpeg"],
  "tasks": [{"task_id": "demo-speaking", "task_version": "1"}],
  "qc": {
    "version": "demo-qc-v1",
    "accepted_formats": ["wav", "flac", "ogg", "mp3"],
    "max_input_bytes": 20000000,
    "min_duration_s": 1.0,
    "max_duration_s": 180.0,
    "max_input_sample_rate_hz": 48000,
    "silence_threshold": 0.01,
    "clipping_threshold": 0.99,
    "review_silence_ratio": 0.5,
    "reject_silence_ratio": 0.95,
    "review_clipping_ratio": 0.1,
    "reject_clipping_ratio": 0.5
  }
}
```

```bash
python -m aicefr.local serve --data-dir /tmp/aicefr-local-data --config /tmp/aicefr-local-config.json
```

ASR chạy English với word timestamps; Silero dùng model đi kèm package, không `torch.hub` tải mạng. Artifact chỉ cho inference trên một response. Provenance mismatch, VAD/ASR lỗi, OOD hoặc thiếu feature đều giữ reason và overall `null`; không thay bằng transcript/score kiểm thử.

## Kiểm thử và khởi động lại

```bash
python -m pytest -q -m 'not smoke'
ruff check src tests scripts
python scripts/ci/check_md_links.py
python scripts/ci/check_forbidden_files.py
```

Các tests cần Ridge thật chỉ chạy khi `AICEFR_MODEL_DIR` có artifact đúng pin; kết quả skip phải được ghi rõ. Browser QA có [evidence theo scope W3](sdd/features/w3-local-integration/evidence/evidence-manifest.md). Chạy server lại với cùng data-dir sẽ giữ accounts, consent, report và quyết định giảng viên. Logout thu hồi session phía server; rút consent chặn bài nộp mới. `Ctrl+C` dừng server và đóng SQLite. Không dùng nhiều workers/process cùng composition root local hiện tại.
