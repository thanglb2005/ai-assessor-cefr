# M02 — 04 Test Plan (Kế hoạch kiểm thử)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M02 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

Test ở đây là **ca dự kiến**, chưa được chạy. Fixture tạo bởi nhóm chỉ kiểm tra logic; không thay âm thanh người dùng hoặc dữ liệu kiểm định CEFR.

| Test ID | FR/AC | Level | Tình huống | Kỳ vọng |
| --- | --- | --- | --- | --- |
| M02-TEST-001 | M02-FR-001 / M02-AC-001 | Unit | Input rỗng hoặc bytes hỏng | REJECT; decoder/ASR sau không gọi |
| M02-TEST-002 | M02-FR-001 / M02-AC-001 | Unit | Audio ngắn dưới ngưỡng test config | Reason đúng, không tạo score/transcript |
| M02-TEST-003 | M02-FR-002 / M02-AC-002 | Unit | Audio test có duration/silence/clipping biết trước | Measured fields có unit và config version |
| M02-TEST-004 | M02-FR-002 / M02-AC-002 | Unit | Cùng input và config chạy hai lần | Các số đo tất định khớp trong sai số đo đã ghi |
| M02-TEST-005 | M02-FR-001 / M02-AC-001 | Boundary/integration | Extension không khớp nội dung file hoặc decoder timeout | Không đi tiếp M03; reason an toàn |

## Chính sách chạy và bằng chứng

- Tạo test cùng task triển khai; ưu tiên unit test cho logic thuần, integration test cho boundary I/O, và kiểm tra UI/API khi hành vi nhìn thấy được.
- Lệnh dự kiến sau khi repo dự án có `pyproject.toml`: `python3 -m pytest -q tests/` và `python3 -m pytest --cov=aicefr --cov-report=term-missing`; tên test/path cuối cùng ghi trong task đã duyệt. **Hiện trạng: NOT_RUN**, vì repo dự án chưa có mã nguồn/test.
- Coverage là chỉ báo để tìm nhánh quan trọng chưa được kiểm thử. Chính sách threshold/no-regression chỉ được chốt ở Phase 04/05 sau khi có stack và baseline đo được.
- Bằng chứng Phase 06/08: command, thời điểm, exit code, số test, phần skipped/fail, coverage report nếu áp dụng, revision/fingerprint, file trong `evidence/`. Browser QA nếu có phải ghi môi trường và ảnh/trạng thái thực.
- Test với audio có quyền sử dụng là smoke/integration riêng; không đưa audio, transcript chứa PII hoặc secret vào Git/log. Chưa có data/consent/approval thì đánh dấu `NOT_RUN` thay vì tạo kết quả thay thế.

**CODEX CHECK RESULT:** DRAFT — mỗi AC có ca kiểm tra; lệnh và coverage policy còn chờ stack. **User verdict Phase 04:** PENDING.
