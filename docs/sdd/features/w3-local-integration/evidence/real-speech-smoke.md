# W3 — Local ASR/VAD smoke độc lập

Reviewer/executor: Codex root, 02/10/2026. Source revision `03e2c5d`, speech code correction `98e70da` (origin af5dc8a). Đây là smoke kỹ thuật trên hai audio local được người dùng xác nhận quyền sử dụng; tên file không là nhãn CEFR đã kiểm chứng. Không có ground truth transcript hoặc đánh giá giảng viên cho phép đo WER/accuracy.

Command: `PYTHONPATH=src HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=1 /tmp/aicefr-w3-venv/bin/python /tmp/aicefr-w3-real-smoke.py`. Exit 0; marker `LOCAL_ADAPTER_SMOKE_PASS`. Script reviewer nằm /tmp, đọc actual AsrService → FasterWhisperEngine → FeatureExtractor/Silero → RidgeScorer; không injection transcript/score kiểm thử. [Raw log](local-adapter-smoke.log) chỉ chứa aggregate metadata; không chứa transcript, audio, credentials hay model bytes.

| Sample | SHA256 | Duration | ASR | Words | Features | VAD | Assessment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| p3_b2.wav | 5bb09620a28f6935902f1cab9180ce81960a2109b823897313bdc859a936609f | 41.145s | OK; 18.483s gồm cold load | 137 | 18/18 có giá trị | silero6.2.1 | ESTIMATED |
| p4_exam_preparation.mp3 | fc786f387eebcd5a0121028f0a23f17be2fcc01289f252da8a1d617aca600314 | 54.312s | OK; 21.632s | 140 | 18/18 có giá trị | silero6.2.1 | ESTIMATED; codec warnings |

QC là `demo-qc-v1`, cả hai PASS. Whisper là canonical `whisper-small`, package faster-whisper1.2.1/CTranslate2 4.8.2, `test_only=false`, English + word timestamps. Silero6.2.1 dùng torch/torchaudio2.11.0+cpu, threshold0.5, min_silence150ms. Feature timings tương ứng 1.602s/0.591s trên máy local này; không phải benchmark tổng quát.

Model files được chuẩn bị trước runtime ở `/tmp/aicefr-w3-models/faster-whisper-small`, revision ghim `536b0662742c02347bc0e980a01041f333bce120`; cả bốn SHA256 đối chiếu [M03-EV-001](../../../modules/m03-asr/evidence/evidence-manifest.md) và được adapter kiểm lại trước load. Ridge artifact ngoài Git SHA256 `7cdeb2a04aa0db770d52d6ff20b49cc371b9cb690f0ace89e5233b5d65bb521a`, unit một response, calibration `chua-hieu-chuan`.

## Error analysis và giới hạn

MP3 phát native mpg123 warnings `part2_3_length ... too large for available bit count` khi libsndfile1.2.2 đọc. Decoder không ném exception; smoke đo được waveform/ASR/features nhưng không kết luận chất lượng decode sạch. Kiểm độc lập bằng PyAV/FFmpeg decode được 2263 frames, 54.312s, exit0 ([metadata](mp3-independent-decode.log)); `ffmpeg -v error -i <same local mp3> -f null -` cũng exit0, stderr rỗng. Hai kiểm tra này không chứng minh waveform libsndfile hoàn toàn tương đương. WAV là mẫu smoke không có warning này; MP3 limitation được giữ trong review/evidence.

WER: `NOT_MEASURED`; CEFR accuracy/calibration: `NOT_MEASURED`. ESTIMATED chỉ xác nhận inference có thể chạy với provenance đúng. Không dùng filename/band dự đoán để claim chất lượng học thuật hoặc validation trên người học. Model/audio/transcript không commit vào Git; runtime offline flags đang bật, không gửi audio tới dịch vụ ngoài.

Full pipeline persistence và browser cần final integration verification riêng; kết quả adapter này không thay final user acceptance.
