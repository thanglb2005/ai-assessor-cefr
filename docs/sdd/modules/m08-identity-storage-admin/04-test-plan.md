# M08 — 04 Test Plan (Kế hoạch kiểm thử)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M08 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

Test ở đây là **ca dự kiến**, chưa được chạy. Fixture tạo bởi nhóm chỉ kiểm tra logic; không thay âm thanh người dùng hoặc dữ liệu kiểm định CEFR.

| Test ID | FR/AC | Level | Tình huống | Kỳ vọng |
| --- | --- | --- | --- | --- |
| M08-TEST-001 | M08-FR-001 / M08-AC-001 | API integration | Student đọc response của actor khác | Không trả dữ liệu/đường dẫn blob |
| M08-TEST-002 | M08-FR-001 / M08-AC-001 | Integration | Consent withdrawn rồi submit | Nộp mới bị chặn; existing data xử lý theo policy |
| M08-TEST-003 | M08-FR-002 / M08-AC-002 | Integration | Restart local sau save Response/audit | Đọc lại đúng checksum/status/audit |
| M08-TEST-004 | M08-FR-001 / M08-AC-001 | API/security | Client tự khai role teacher/admin hoặc session hết hạn | Không nâng quyền hoặc xem queue |
| M08-TEST-005 | M08-FR-002 / M08-AC-002 | Security check | Scan repo/config/log sau test | Không có secret/PII/audio/transcript thật trong Git/log |

## Chính sách chạy và bằng chứng

- Tạo test cùng task triển khai; ưu tiên unit test cho logic thuần, integration test cho boundary I/O, và kiểm tra UI/API khi hành vi nhìn thấy được.
- Lệnh dự kiến sau khi repo dự án có `pyproject.toml`: `python3 -m pytest -q tests/` và `python3 -m pytest --cov=aicefr --cov-report=term-missing`; tên test/path cuối cùng ghi trong task đã duyệt. **Hiện trạng: NOT_RUN**, vì repo dự án chưa có mã nguồn/test.
- Coverage là chỉ báo để tìm nhánh quan trọng chưa được kiểm thử. Chính sách threshold/no-regression chỉ được chốt ở Phase 04/05 sau khi có stack và baseline đo được.
- Bằng chứng Phase 06/08: command, thời điểm, exit code, số test, phần skipped/fail, coverage report nếu áp dụng, revision/fingerprint, file trong `evidence/`. Browser QA nếu có phải ghi môi trường và ảnh/trạng thái thực.
- Test với audio có quyền sử dụng là smoke/integration riêng; không đưa audio, transcript chứa PII hoặc secret vào Git/log. Chưa có data/consent/approval thì đánh dấu `NOT_RUN` thay vì tạo kết quả thay thế.

**CODEX CHECK RESULT:** DRAFT — mỗi AC có ca kiểm tra; lệnh và coverage policy còn chờ stack. **User verdict Phase 04:** PENDING.
