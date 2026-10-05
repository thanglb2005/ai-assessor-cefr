# Raw report — W3 speech lane

- Prompt: `W3-PROMPT-003`
- Tasks: `W3-TASK-005`, `W3-TASK-006`
- Starting fingerprint: `077da2ddbf9d18bdd92d48ed0d434619ee942398cbc3656b7400662205490881` (`sdd-workspace-v2`)
- Base revision: `7bb327b655c67d8eb5aafc4cd8ec9481fabdff28`; base source revision: `2b428ceea9e4459f3235d4ce67f10bab31585ebf`
- Code commit: `dfac63af857e954acc16de7b22e9ef78ea9f183d`
- Code commit tree: `01f28e35626908aa096c6302d900a0aed6bc784b`
- Branch: `feat/W3-speech`
- Verdict: implementation evidence only; user acceptance remains `PENDING`.

## Thay đổi

Thêm `FasterWhisperEngine` và `SileroVadEngine` với import lười, không tải model, từ chối khi model/dependency local thiếu; lấy version từ package metadata và giữ nguyên định danh weight không khớp để provenance không được coi tương thích. Input VAD yêu cầu mono float32 16 kHz và timestamps trả về theo giây. Thay logging ngoại lệ của ASR/VAD bằng log status/reason an toàn, không in message hoặc traceback. Artifact/scorer kiểm tra finite, shape, feature order, bounds và scale; `scale <= 0`, nonfinite feature/score và vector sai cấu trúc dừng với `NOT_EVALUATED`, không tạo điểm giả. CI cài `.[dev]` đúng một lần, không fallback, rồi chạy pytest coverage và Ruff.

Artifact/model rubric và pinned hash không đổi. Hash đọc trực tiếp từ artifact nội bộ là `7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a`; provenance metadata được ghi tại [model-provenance.md](model-provenance.md). Adapter API đối chiếu với nguồn upstream chính thức: [Faster-Whisper README](https://github.com/SYSTRAN/faster-whisper), [Faster-Whisper implementation](https://raw.githubusercontent.com/SYSTRAN/faster-whisper/master/faster_whisper/transcribe.py), [Silero VAD README](https://github.com/snakers4/silero-vad), [Silero VAD timestamps implementation](https://raw.githubusercontent.com/snakers4/silero-vad/master/src/silero_vad/utils_vad.py), [Silero bundled model loader](https://raw.githubusercontent.com/snakers4/silero-vad/master/src/silero_vad/model.py).

## Kiểm tra

Lệnh đều chạy trong worktree `/tmp/aicefr-w3-speech`. Python dùng `/tmp/aicefr-w3-venv/bin/python` và `PYTHONPATH=src`; artifact thật chỉ được đọc ngoài repo, không copy vào Git.

| Lệnh | Exit | Kết quả |
| --- | ---: | --- |
| `AICEFR_MODEL_DIR=/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie/src/aicefr/scoring/models PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python -m pytest -q -m 'not smoke' --cov=aicefr.asr.local --cov=aicefr.features.local --cov=aicefr.asr.service --cov=aicefr.features.extractor --cov=aicefr.scoring.artifact --cov=aicefr.scoring.scorer --cov-branch --cov-report=term-missing --cov-report=json:/tmp/aicefr-w3-speech-coverage.json` | 0 | **PASS**, 221 passed, 0 skipped; 96% line, 93% branch overall for measured packages. |
| `/tmp/aicefr-w3-venv/bin/ruff check src tests scripts` | 0 | **PASS** |
| `python3 scripts/ci/check_md_links.py` | 0 | **PASS**, 140 Markdown files; existing 16 external links are reported as skipped, no broken in-repo links. |
| `python3 scripts/ci/check_forbidden_files.py` | 0 | **PASS**, 248 files, no forbidden files. |
| `git diff --check` | 0 | **PASS** |
| Real ASR/VAD local smoke with allowed audio/weights | — | **NOT_RUN**: no permitted local ASR weights/audio were available; Silero VAD package/model was absent from test venv. |
| GitHub Actions CI execution | — | **NOT_RUN**: workflow configuration updated locally; no remote run was triggered. |

Line/branch coverage by changed critical module: ASR adapter 85%/88%; VAD adapter 86%/75%; ASR service 100%/100%; feature extractor 100%/100%; artifact loader 98%/96%; scorer 96%/93%. Uncovered adapter lines include true third-party constructor/inference failures and package-present version paths; VAD model execution and actual ASR remain unmeasured. JSON report: `/tmp/aicefr-w3-speech-coverage.json`.

## Failure scenarios and limits

Missing Faster-Whisper dependency, incomplete local model directory or local model load failure yields controlled `ModelUnavailableError`; service returns an ASR failure/not-run reason without transcript fallback. Missing/broken bundled Silero yields `VadUnavailableError`; feature extraction records missing VAD-derived features instead of zeros or another VAD. Invalid scoring artifact/features refuse evaluation with existing reason codes. Tests mock third-party boundaries and verify refused states/privacy logs; they do not establish recognition, VAD, or CEFR accuracy. This lane made no WER, VAD-quality, or user-study claim.
