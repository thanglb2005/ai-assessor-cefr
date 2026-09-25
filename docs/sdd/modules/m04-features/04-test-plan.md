# M04 — 04 Test Plan (Kế hoạch kiểm thử)

> **BẢN NHÁP W2 (v0.1, 25/09/2026).** Chuẩn bị theo yêu cầu chủ dự án; Phase 01 của M04 vẫn `DRAFT/PENDING`. Nội dung dưới đây chưa là Specification/Plan được duyệt và không cấp quyền phát prompt triển khai.

Test ở đây là **ca dự kiến**, chưa được chạy. Fixture tạo bởi nhóm chỉ kiểm tra logic; không thay âm thanh người dùng hoặc dữ liệu kiểm định CEFR.

| Test ID | FR/AC | Level | Tình huống | Kỳ vọng |
| --- | --- | --- | --- | --- |
| M04-TEST-001 | M04-FR-001 / M04-AC-001 | Unit | Transcript OK và QC duration hợp lệ | Word count/duration/rate theo công thức đã duyệt |
| M04-TEST-002 | M04-FR-002 / M04-AC-001 | Unit | Thiếu timestamp/duration cho rate | Rate null và missing_reason |
| M04-TEST-003 | M04-FR-002 / M04-AC-002 | Unit | ASR_FAILED hoặc transcript rỗng | Không sinh feature text như đã đo |
| M04-TEST-004 | M04-FR-001 / M04-AC-002 | Unit | Input hash/version lệch | FeatureSet bị từ chối, không dùng stale data |
| M04-TEST-005 | M04-FR-002 / M04-AC-002 | Privacy check | Transcript chứa chuỗi nhận dạng trong fixture | FeatureSet/log không lộ chuỗi đó |

## Chính sách chạy và bằng chứng

- Tạo test cùng task triển khai; ưu tiên unit test cho logic thuần, integration test cho boundary I/O, và kiểm tra UI/API khi hành vi nhìn thấy được.
- Lệnh dự kiến sau khi repo mới có `pyproject.toml`: `python3 -m pytest -q tests/` và `python3 -m pytest --cov=aicefr --cov-report=term-missing`; tên test/path cuối cùng ghi trong task đã duyệt. **Hiện trạng: NOT_RUN**, vì repo mới chưa có mã nguồn/test.
- Coverage là chỉ báo để xem nhánh quan trọng chưa kiểm; không gán phần trăm đạt giả. Chính sách threshold/no-regression sẽ được chốt ở Phase 04/05 sau khi có stack và baseline đo được.
- Bằng chứng Phase 06/08: command, thời điểm, exit code, số test, phần skipped/fail, coverage report nếu áp dụng, revision/fingerprint, file trong `evidence/`. Browser QA nếu có phải ghi môi trường và ảnh/trạng thái thực.
- Test với audio có quyền sử dụng là smoke/integration riêng; không đưa audio, transcript chứa PII hoặc secret vào Git/log. Chưa có data/consent/approval thì đánh dấu `NOT_RUN` thay vì tạo kết quả thay thế.

**CODEX CHECK RESULT:** DRAFT — mỗi AC có ca kiểm tra; lệnh và coverage policy còn chờ stack. **User verdict Phase 04:** PENDING.
