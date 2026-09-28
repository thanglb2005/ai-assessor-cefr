# M02 — 02 Research

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M02 / module |
| DATE | 28/09/2026 |
| RESEARCH MODE | RUN — được người dùng duyệt trong M02 Phase 01 |
| OBJECTIVE | Chọn hướng decoder/resampling cho M02→M03; xác định rủi ro format, tài nguyên và QC thresholds |

## Sources and findings

| Source | Fact |
| --- | --- |
| python-soundfile 0.14.0 documentation | SoundFile dùng libsndfile, đọc/ghi các format mà libsndfile hỗ trợ; docs hiện có ví dụ MP3 và ghi rõ WAV/FLAC/OGG. read() có dtype float32, trả sample rate và số channel; wheels thông dụng có thể kèm libsndfile. |
| Python-SoXR 1.1.0 documentation | SoXR cung cấp resample() và streaming ResampleStream cho mono/multichannel NumPy arrays; PyPI 1.1.0 có wheels CPython 3.11. scipy.signal.resample_poly là lựa chọn polyphase; scipy 1.17 có wheel Python 3.11 nhưng scipy 1.18 yêu cầu Python >=3.12. |
| PyAV documentation and FFmpeg formats | PyAV mở API cấp thấp của FFmpeg để thao tác container/codec/resampler và hỗ trợ nhiều format; tăng diện tích dependency/native-library và mức phức tạp so với audio-only libsndfile. |
| M03 Specification v0.2 and src/aicefr/contracts.py | M03 nhận PCM float32 mono 16 kHz; shared contract hiện có DecodedAudio nhưng mới giữ sample_rate_hz thực tế, chưa ép bằng 16 kHz. M03 TASK-002 đang chờ owner M02 xác nhận 16 kHz. |
| Project pyproject.toml | Project yêu cầu Python >=3.11, có NumPy; hiện chưa khai báo SoundFile, SoXR hoặc PyAV. scipy 1.18 yêu cầu Python >=3.12 nên không phù hợp với minimum supported version hiện tại. |

## Options

| Option | Điểm mạnh | Rủi ro/chi phí | Kết luận |
| --- | --- | --- | --- |
| SoundFile + SoXR | Hỗ trợ audio sample-based qua libsndfile; API trả NumPy data; sample-rate conversion cho mono/multichannel; phù hợp interface hiện tại và có thể test bằng fixture tạo bởi nhóm. | Hai dependency có native components; SoXR/libsndfile mang LGPL, cần chấp nhận điều kiện phân phối; whitelist phải khớp libsndfile bundled version. | ADAPT — khuyến nghị cho W2 sau khi owner duyệt dependency và format. |
| PyAV/FFmpeg | Khả năng đọc container/codec rộng, có AudioResampler. | Native stack lớn hơn; nhiều lựa chọn format/codec hơn nhu cầu đã xác nhận; cần chốt packaging và licensing. | OPEN — chỉ chọn nếu format user cần không được SoundFile hỗ trợ. |
| Chỉ nhận WAV PCM 16 kHz mono | Dependency ít, boundary hẹp. | Không đáp ứng resampling hay nhiều format; M01 phải enforce whitelist; hạn chế input đáng kể. | OPEN — phương án tối giản nếu W2 chỉ cần fixture WAV. |

## Technical constraints and risks

- Declared extension không đủ để xác nhận format; decoder phải nhận diện nội dung thực và từ chối mismatch/decoder errors.
- Đọc input như bounded bytes/file-like object, giới hạn kích thước trước decode và giới hạn frame/duration trong lúc đọc; không nhận path tùy ý từ HTTP.
- Raw blob bất biến; hash trên raw bytes được gắn vào DecodedAudio.
- Resampling/downmix thay đổi samples; thuật toán và config version phải được ghi. Audio mono 16 kHz là output contract, không phải claim về chất lượng đầu vào.
- Silence và clipping chỉ là đo đạc kỹ thuật. Chưa có dữ liệu hiệu chuẩn nên nghiên cứu không đưa ngưỡng người học hoặc ngưỡng sản phẩm.
- Pass/review/reject numeric thresholds cần là QCConfig explicit/versioned; không có implicit defaults. Fixture tests được phép truyền test config có giá trị tổng hợp.

## Recommendation for Phase 03

- ADAPT SoundFile 0.14.0 + SoXR 1.1.0 cho format whitelist hẹp được owner duyệt; confirm LGPL dependency compatibility before adoption.
- Chỉ hỗ trợ formats cụ thể đã được người dùng phê chuẩn; đề xuất khởi đầu WAV PCM, FLAC, OGG/Vorbis, MP3 theo khả năng libsndfile bundled version.
- Downmix stereo bằng arithmetic mean, reject nhiều hơn 2 channels; cần user duyệt vì có thể triệt tiêu tín hiệu nếu hai channel lệch pha.
- Đo duration, silence ratio và clipped-sample ratio; thresholds bắt buộc truyền trong versioned QCConfig. Test configuration chỉ dùng fixture, không phải cấu hình production.
- M03 spec cho phép REVIEW tiếp tục ASR, nhưng code hiện tại chỉ gate REJECT và không đưa QC reason/config version vào Transcript. Do đó pipeline M02 nên chỉ tự dispatch PASS; giữ REVIEW ở trạng thái chờ quyết định, REJECT chặn ASR. Cần M03 owner review semantics này.

## Decisions required from owner

- Duyệt SoundFile + SoXR (LGPL) hay chọn PyAV/WAV-only; kiểm tra yêu cầu license trước khi đưa dependency vào project.
- Duyệt input whitelist, channel policy và giới hạn file size/duration/sample rate.
- Duyệt metric definitions/threshold config để PASS/REVIEW/REJECT; nếu chưa có calibration, chỉ duyệt test-only config và không phát hành default config.
- Duyệt additive shared-contract changes/reason codes với owner M03/M04 trước Phase 05.

## References

- python-soundfile 0.14.0 documentation: https://python-soundfile.readthedocs.io/en/latest/
- SoXR 1.1.0 documentation: https://python-soxr.readthedocs.io/en/latest/
- SoXR PyPI release/wheels/license: https://pypi.org/project/soxr/
- scipy.signal.resample_poly alternative: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html
- python-soundfile PyPI release/wheels: https://pypi.org/project/soundfile/
- SciPy resample_poly: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html
- FFmpeg formats documentation: https://ffmpeg.org/ffmpeg-formats.html
- PyAV documentation: https://pyav.org/docs/stable/
- M03 Specification: ../m03-asr/03-specification.md
- Existing shared contract: ../../../src/aicefr/contracts.py

## CODEX CHECK RESULT

PASS — research separates documented facts, project observations and recommendations; no numeric QC product threshold was invented. Phase 03 remains pending user review.
