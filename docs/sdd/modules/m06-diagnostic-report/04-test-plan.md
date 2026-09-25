# M06 — 04 Test Plan (Kế hoạch kiểm thử)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M06 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

Test ở đây là **ca dự kiến**, chưa được chạy. Fixture tạo bởi nhóm chỉ kiểm tra logic; không thay âm thanh người dùng hoặc dữ liệu kiểm định CEFR.

| Test ID | FR/AC | Level | Tình huống | Kỳ vọng |
| --- | --- | --- | --- | --- |
| M06-TEST-001 | M06-FR-001 / M06-AC-001 | Unit | Không có evidence hợp lệ | Không sinh comment khẳng định; hiện missing reason |
| M06-TEST-002 | M06-FR-001 / M06-AC-002 | Unit | Pause/word ref hợp lệ từ cùng response | Link mốc và source version đúng |
| M06-TEST-003 | M06-FR-001 / M06-AC-001 | Boundary | Ref khác response/ngoài duration/stale version | Bỏ comment và ghi reason, không bịa ref |
| M06-TEST-004 | M06-FR-002 / M06-AC-002 | Unit + API | Assessment NOT_EVALUATED, không review action | Không có band; teacher_verified false |
| M06-TEST-005 | M06-FR-002 / M06-AC-002 | Integration W3 | M07 ghi review action hợp lệ | Report hiển thị AI result và teacher final/audit ref tách biệt |

## Chính sách chạy và bằng chứng

- Tạo test cùng task triển khai; ưu tiên unit test cho logic thuần, integration test cho boundary I/O, và kiểm tra UI/API khi hành vi nhìn thấy được.
- Lệnh dự kiến sau khi repo mới có `pyproject.toml`: `python3 -m pytest -q tests/` và `python3 -m pytest --cov=aicefr --cov-report=term-missing`; tên test/path cuối cùng ghi trong task đã duyệt. **Hiện trạng: NOT_RUN**, vì repo mới chưa có mã nguồn/test.
- Coverage là chỉ báo để xem nhánh quan trọng chưa kiểm; không gán phần trăm đạt giả. Chính sách threshold/no-regression sẽ được chốt ở Phase 04/05 sau khi có stack và baseline đo được.
- Bằng chứng Phase 06/08: command, thời điểm, exit code, số test, phần skipped/fail, coverage report nếu áp dụng, revision/fingerprint, file trong `evidence/`. Browser QA nếu có phải ghi môi trường và ảnh/trạng thái thực.
- Test với audio có quyền sử dụng là smoke/integration riêng; không đưa audio, transcript chứa PII hoặc secret vào Git/log. Chưa có data/consent/approval thì đánh dấu `NOT_RUN` thay vì tạo kết quả thay thế.

**CODEX CHECK RESULT:** DRAFT — mỗi AC có ca kiểm tra; lệnh và coverage policy còn chờ stack. **User verdict Phase 04:** PENDING.
