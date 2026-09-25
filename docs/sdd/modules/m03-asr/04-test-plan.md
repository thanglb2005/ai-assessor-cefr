# M03 — 04 Test Plan (Kế hoạch kiểm thử)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M03 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

Test ở đây là **ca dự kiến**, chưa được chạy. Fixture tạo bởi nhóm chỉ kiểm tra logic; không thay âm thanh người dùng hoặc dữ liệu kiểm định CEFR.

| Test ID | FR/AC | Level | Tình huống | Kỳ vọng |
| --- | --- | --- | --- | --- |
| M03-TEST-001 | M03-FR-001 / M03-AC-001 | Unit | Test double tạo transcript từ input kiểm thử | Output tất định, marker test_only và version |
| M03-TEST-002 | M03-FR-002 / M03-AC-001 | Unit | Engine raise exception/timeout | ASR_FAILED, không có transcript OK/score |
| M03-TEST-003 | M03-FR-001 / M03-AC-002 | Integration smoke | Local model + audio có quyền sử dụng | Ghi model/version/config, output và command thực hoặc NOT_RUN |
| M03-TEST-004 | M03-FR-001 / M03-AC-001 | Unit | Engine chỉ trả segment timestamp | Word timestamps null, reason rõ |
| M03-TEST-005 | M03-FR-002 / M03-AC-001 | Boundary | Transcript rỗng/word timing ngoài duration | UNRELIABLE/FAILED, không phát artifact hợp lệ |

## Chính sách chạy và bằng chứng

- Tạo test cùng task triển khai; ưu tiên unit test cho logic thuần, integration test cho boundary I/O, và kiểm tra UI/API khi hành vi nhìn thấy được.
- Lệnh dự kiến sau khi repo mới có `pyproject.toml`: `python3 -m pytest -q tests/` và `python3 -m pytest --cov=aicefr --cov-report=term-missing`; tên test/path cuối cùng ghi trong task đã duyệt. **Hiện trạng: NOT_RUN**, vì repo mới chưa có mã nguồn/test.
- Coverage là chỉ báo để xem nhánh quan trọng chưa kiểm; không gán phần trăm đạt giả. Chính sách threshold/no-regression sẽ được chốt ở Phase 04/05 sau khi có stack và baseline đo được.
- Bằng chứng Phase 06/08: command, thời điểm, exit code, số test, phần skipped/fail, coverage report nếu áp dụng, revision/fingerprint, file trong `evidence/`. Browser QA nếu có phải ghi môi trường và ảnh/trạng thái thực.
- Test với audio có quyền sử dụng là smoke/integration riêng; không đưa audio, transcript chứa PII hoặc secret vào Git/log. Chưa có data/consent/approval thì đánh dấu `NOT_RUN` thay vì tạo kết quả thay thế.

**CODEX CHECK RESULT:** DRAFT — mỗi AC có ca kiểm tra; lệnh và coverage policy còn chờ stack. **User verdict Phase 04:** PENDING.
