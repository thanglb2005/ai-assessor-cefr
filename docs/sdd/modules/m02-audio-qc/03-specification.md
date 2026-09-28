# M02 — 03 Specification (Đặc tả)

> W2 v0.3 · 28/09/2026. Requirement v0.2 và Specification v0.3 đã được user duyệt Phase 01/03. Phase 04 Test Plan v0.2 đã được duyệt; Phase 05 còn chờ owner review và user verdict.

Owner: Thắng. Mục tiêu W2: giải mã audio được phép, chuẩn hóa thành PCM float32 mono 16 kHz, đo QC kỹ thuật có config version và chặn đầu vào không dùng được trước ASR.

## Boundary và hợp đồng đầu vào/đầu ra

| Artifact | Trường/invariant | Owner → consumer |
| --- | --- | --- |
| AudioInput | audio_ref, content hash, declared format, task/response ID; không mang tên người học; M02 lấy bytes qua M08 | M01/M08 → M02 |
| DecodedAudio | samples là NumPy 1-D float32; sample_rate_hz luôn 16000; duration_s; audio_sha256 của raw bytes | M02 → M03/M04 |
| QCMeasurement | name, value (number hoặc null), unit, missing_reason khi null; đề xuất thêm type dùng chung | M02 → M03/M01 |
| QCResult | status PASS/REVIEW/REJECT, measurements, reason codes, qc_config_version | M02 → M03/M01 |
| QCConfig | version; accepted formats; max bytes/min+max duration/input rate; max channels = 2; resampling/downmix; silence/clipping and policy limits; không có implicit default | M02 deployment config → M02 |

## Decoder, resampling và measurement

- Selected: pin SoundFile 0.14.0 và SoXR 1.1.0 (LGPL); dùng libsndfile của wheel đã pin để decode và SoXR HQ để resample đến 16 kHz. Không tự fallback sang decoder khác.
- Whitelist đã duyệt: WAV PCM, FLAC, OGG/Vorbis và MP3 theo libsndfile build đã pin. Kiểm tra container/subtype thực tế; reject nếu extension/declared format không khớp bytes hoặc subtype ngoài whitelist.
- Input chỉ nhận authorized bytes, không nhận filesystem path từ caller. QCConfig versioned phải cung cấp max_input_bytes, min_duration_s, max_duration_s, max_input_sample_rate_hz và metric/policy limits; không có default ngầm hoặc production threshold chưa hiệu chuẩn. Kiểm tra bytes trước decode và đọc theo block để dừng tại frame cap, tránh cấp phát theo độ dài không giới hạn.
- Mono input giữ nguyên; stereo downmix bằng arithmetic mean trước resampling; trên hai channel REJECT.
- Resample to 16 kHz using SoXR HQ; algorithm/library version belongs to the processing provenance/config version. Preserve raw blob and compute SHA-256 before decode.
- Đo duration (s), silence ratio và clipped-sample ratio trên PCM mono sau resampling. Silence ratio = tỷ lệ sample có `abs(sample) <= silence_threshold`; clipped ratio = tỷ lệ có `abs(sample) >= clipping_threshold`. Cả hai thresholds và policy limits là trường bắt buộc của QCConfig versioned; không phát hành production defaults.
- QCConfig has stable version. A config change that changes status/measured result must use a new version.

## QC and M03 boundary

- Structural failures (empty/corrupt/unsupported/mismatch/resource limit) return REJECT with safe reason code and no samples forwarded.
- Policy failures may return REVIEW or REJECT according to explicit QCConfig; missing measurement is null plus reason, never zero.
- M03 contract hiện cho phép PASS/REVIEW và AsrService chỉ chặn REJECT. M02 pipeline gate đã duyệt chỉ tự dispatch PASS; REVIEW ở trạng thái pending explicit owner review, REJECT không gọi ASR. Không thêm đường override tự động. M03 owner cần duyệt semantics trước Phase 05.
- QC does not infer CEFR level, pronunciation, accent or speaker quality.
- Shared contract change: thêm typed QCMeasurement và measurements tuple vào QCResult, cùng M02 reason codes. Vì `src/aicefr/contracts.py` là contract liên module, Sang (M03/M04 owner) cần review trước Phase 05.

## Privacy, failure and recovery

- No logs contain raw audio, transcript, PII, credentials or full paths; logs may include response ID, status, reason codes, QC config version and elapsed time.
- Đã duyệt bounded in-process decoding cho W2: giới hạn bytes/sample rate/channels/frames qua QCConfig; không có hard wall-clock timeout hoặc worker isolation. Bắt exception decoder/resampler thành REJECT với reason an toàn; không lộ stack trace hoặc chuỗi lỗi thư viện.
- Raw audio is immutable; derived PCM is temporary/in-memory and not persisted unless a separately approved workflow requires it.
- No sample is sent to network services.

## Trace Requirement → AC

| Requirement | Acceptance Criteria | Observation |
| --- | --- | --- |
| M02-FR-001 | M02-AC-001 | Invalid/too-short fixtures have deterministic reasons; REJECT path does not invoke ASR or create score/transcript. |
| M02-FR-002 | M02-AC-002 | PCM shape/dtype/rate and measured metadata/config version; repeatable metrics for same fixture/config. |

## Phase 03 decisions — APPROVED 28/09/2026

- Dùng SoundFile 0.14.0 + SoXR 1.1.0, LGPL, whitelist WAV PCM/FLAC/OGG-Vorbis/MP3. Mono giữ nguyên; stereo lấy trung bình; trên hai channel REJECT.
- Mọi resource cap, metric threshold và policy limit phải có trong QCConfig versioned; không có default ngầm hoặc production thresholds trước calibration. Fixture test dùng config tổng hợp rõ giá trị.
- Silence/clipped ratio tính trên PCM mono sample-level theo ngưỡng cấu hình.
- Bounded in-process decode; không cam kết hard timeout/process isolation trong W2.
- PASS tự dispatch ASR; REVIEW chờ explicit owner review; REJECT không gọi ASR.

**CODEX CHECK RESULT:** PASS về trace FR/AC, success/invalid/failure/recovery và privacy boundary. **User verdict Phase 03:** APPROVED theo đề xuất · 28/09/2026.

**Phase 05 dependency:** Sang (M03/M04 owner) review additive `QCResult`/`QCMeasurement` contract và PASS-only dispatch semantics trước khi duyệt Plan/Tasks.

## Lịch sử phiên bản

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 25/09/2026 | Draft ban đầu |
| v0.2 | 28/09/2026 | Requirement Phase 01 approved; bổ sung output 16 kHz mono và Research findings |
| v0.3 | 28/09/2026 | Phase 03 decisions approved by Thắng |
