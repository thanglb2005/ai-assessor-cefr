# M03 — Evidence Manifest (danh mục bằng chứng)

**Hiện trạng:** chưa có implementation/test evidence của repo dự án. Đã có evidence chuẩn bị môi trường M03-EV-001 (weight ASR). Báo cáo và hình W1 cấp dự án nằm ở docs/reports/week-01/ và docs/design/week-01/.

| Evidence ID | Prompt ID / Task ID | Phase | Base/Head revision, fingerprint | Loại / file hoặc link | Check và kết quả thực tế | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| M03-EV-001 | SCRUM-21 (việc tay M03-O1 / DEP-05) | 05 — chuẩn bị dependency | Không áp dụng (tải ngoài repo, không đổi source) | Weight ASR, xem mục dưới | SHA-256 `model.bin` khớp giá trị LFS chính thức trên Hugging Face | RECORDED |

Lưu tại đây raw report của Antigravity, command output/test/coverage, ảnh browser QA và final verification khi phát sinh. File lớn có thể lưu ngoài Git nhưng phải có link ổn định, checksum và quyền truy cập cho người review. Mỗi evidence gắn đúng Prompt ID, Task ID, AC/Test ID và revision. Redact secret/PII/audio/transcript thật; không ghi PASS cho lệnh chưa chạy. Cập nhật 07-status.md trỏ tới evidence mới nhất.

## M03-EV-001 — Weight `whisper-small` (CTranslate2)

Tải có chủ đích theo M03-D-001 (`whisper-small`), M03-D-002 (không tự tải khi chạy) và M03-O-001 (faster-whisper). Weight **không** nằm trong Git.

| Mục | Giá trị |
| --- | --- |
| Nguồn | Hugging Face `Systran/faster-whisper-small` |
| Revision ghim | `536b0662742c02347bc0e980a01041f333bce120` |
| License | MIT (khai báo trong model card) |
| Ngày tải | 26/09/2026, máy của Sang (macOS 26.4, Apple M5, 24 GiB RAM) |
| Nơi lưu | `~/models/faster-whisper-small/` — ngoài repo; `.gitignore` bỏ qua `models/` và CI chặn `*.bin` |
| Lệnh | `curl -sSfL https://huggingface.co/Systran/faster-whisper-small/resolve/<revision>/<file>` cho từng file, rồi `shasum -a 256` |

| File | Kích thước (byte) | SHA-256 |
| --- | --- | --- |
| `model.bin` | 483 546 902 | `3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671` |
| `config.json` | 2 370 | `b55496ac7940a7ae47d2c01eab40edfd8701feec1229d9cce3b40014383fb828` |
| `tokenizer.json` | 2 203 239 | `fb7b63191e9bb045082c79fd742a3106a12c99513ab30df4a0d47fa6cb6fd0ab` |
| `vocabulary.txt` | 459 861 | `34ce3fe1c5041027b3f8d42912270993f986dbc4bb34cf27f951e34a1e453913` |

**Kiểm tra:** SHA-256 của `model.bin` trùng giá trị LFS mà API Hugging Face công bố cho revision trên. Chưa chạy model; smoke M03-TEST-S1/S2 vẫn `NOT_RUN` (chờ audio có quyền dùng và DEP-01..04).
