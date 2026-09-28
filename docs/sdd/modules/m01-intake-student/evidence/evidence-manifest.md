# M01 — Evidence Manifest (danh mục bằng chứng)

**Hiện trạng:** có evidence direct implementation theo chỉ dẫn trực tiếp ngày 28/09/2026. Không có prompt Antigravity, commit hay user acceptance; báo cáo và hình W1 cấp dự án vẫn nằm ở docs/reports/week-01/ và docs/design/week-01/.

| Evidence ID | Prompt ID / Task ID | Phase | Base/Head revision, fingerprint | Loại / file hoặc link | Check và kết quả thực tế | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| M01-EVID-DIRECT-20260928 | M01-TASK-001/002/003 | Direct workspace evidence, không phải phase verdict | HEAD `db34379f96d439ace6d504b60c31bc01cab9a902`; fingerprint trong file evidence | [M01-EVID-DIRECT-20260928.md](M01-EVID-DIRECT-20260928.md) | Ruff/selected pytest/compile/diff check có kết quả thực; browser QA `NOT_RUN` | TECHNICAL_EVIDENCE; USER_VERDICT_PENDING |

Lưu tại đây raw report của Antigravity, command output/test/coverage, ảnh browser QA và final verification khi phát sinh. File lớn có thể lưu ngoài Git nhưng phải có link ổn định, checksum và quyền truy cập cho người review. Mỗi evidence gắn đúng Prompt ID, Task ID, AC/Test ID và revision. Redact secret/PII/audio/transcript thật; không ghi PASS cho lệnh chưa chạy. Cập nhật 07-status.md trỏ tới evidence mới nhất.
