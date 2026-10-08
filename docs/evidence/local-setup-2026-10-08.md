# Cài đặt và xác minh local repo chính — 08/10/2026

Người yêu cầu: Thắng. Executor: Codex. Nhánh `main`, revision
`e2e7fead2df0cec266bcb5802e78d54c2c214d81`.

Yêu cầu: cài toàn bộ dependency và model cần cho pipeline hiện tại; kiểm tra repo
chính hoạt động; giữ thư mục tham chiếu cho đến khi người dùng duyệt việc thay nó.
Yêu cầu khôi phục Git của thư mục tham chiếu đã được người dùng hủy.

## Cài đặt

Python 3.12.3; venv riêng tại `.venv/`. Đã cài core và các extras `dev,asr,vad`,
torch/torchaudio `2.11.0+cpu`, faster-whisper `1.2.1`, CTranslate2 `4.8.2`,
Silero VAD `6.2.1`, Playwright/Chromium và công cụ build.

Model và dữ liệu chạy đặt tại `../ai-assessor-cefr-runtime/`, ngoài Git.
Whisper-small khớp cả bốn hash của adapter, revision
`536b0662742c02347bc0e980a01041f333bce120`. Ridge v2 được sao chép từ hồ sơ nội bộ
và khớp pin SHA-256; Silero dùng JIT bundled trong package.
Config/start script chạy offline, không đọc model từ thư mục tham chiếu.

Hướng dẫn chạy, tài khoản fixture, manifest, raw logs và ảnh:
[Môi trường local](../../../ai-assessor-cefr-runtime/README.md).
Mật khẩu chỉ lưu trong file local quyền `0600`, ngoài repo; không đưa vào báo cáo/Git.

## Kết quả trên revision hiện hành

| Kiểm tra | Kết quả đo |
| --- | --- |
| Toàn bộ pytest không smoke, có Ridge thật | 269 passed; 0 failed; 0 skipped |
| Ruff `src tests scripts` | PASS |
| Link Markdown và file bị cấm | PASS |
| `pip check`, CLI help, wheel build | PASS |
| Browser student/teacher và consent/session | 11 lượt desktop/mobile PASS; 0 console error/request lỗi/request ngoài |
| Pipeline với model thật, audio fixture 40 giây | `COMPLETED/ESTIMATED`; 96 nhận xét có evidence; 0 evidence lỗi; 18,903 giây |
| Lưu/reopen report, session và logout | PASS |
| Giao diện server thật tại localhost:8000 | Báo cáo khớp dữ liệu đã lưu; desktop/mobile PASS |

Fixture lấy từ test upstream [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper/tree/master/tests/data).
License repository upstream được lưu cùng fixture. Đoạn 40–80 giây được chuẩn hóa
âm lượng peak 0,8; hash và derivation nằm trong manifest local. Audio nguyên bản đi
nhánh `QC_SILENCE_REVIEW`; giữ raw log các attempt. Không thay ngưỡng QC/model pin,
không dùng transcript/score kiểm thử cho lần chạy model thật.

## Giới hạn và bước tiếp theo

Đây là xác minh kỹ thuật ở chế độ demo local. WER, CEFR accuracy/calibration:
`NOT_MEASURED`. User verdict: `PENDING`.

Repo chính đã fetch nhánh/tag và fast-forward main đến revision trên. Thư mục tham
chiếu có khoảng 1,7 GB, phần lớn là `.venv` 1,6 GB; Git metadata của nó thiếu
HEAD/config. Người dùng xác nhận repo tham chiếu là
`https://github.com/ThanhSangLouis/ai-assessor-cefr`.

Tại thời điểm setup chưa thay thư mục tham chiếu. Cập nhật sau đó: đã clone Sang riêng; người dùng đã yêu cầu xóa tham chiếu cũ và cache pip. Xem [kết quả dọn thư mục](cleanup-2026-10-08.md).
