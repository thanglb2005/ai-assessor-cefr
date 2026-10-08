# PARITY-001 — Verification và bàn giao local

Ngày 08/10/2026. Base `e2e7fead2df0cec266bcb5802e78d54c2c214d81`, nhánh
`feat/PARITY-001-runtime-completeness`; thay đổi code đang ở workspace.
Chủ dự án trực tiếp yêu cầu bổ sung đầy đủ chức năng còn thiếu, gồm quản trị và
thống kê. Đây là technical verification; owner review và user acceptance PENDING.

## Kết quả và phạm vi

Có lịch sử/tiến độ/profile/export của sinh viên, registry đề theo version, ghi âm
micro/preview/upload progress, audio playback và evidence seek cho báo cáo mới.
Teacher/admin xem toàn bộ bài, thống kê band AI và teacher final riêng, audit
trước/sau, nhận/trả bài, claim TTL 15 phút và mở lại quyết định bằng revision/lý do.
Admin có accounts, khóa/disable, audit, QC CAS/version, model registry/pinned
activation, research opt-in export, erasure preview/confirm và maintenance.

Có worker nền với connection SQLite riêng, hàng đợi giới hạn, lease một server,
khôi phục trạng thái job gián đoạn, health/readiness/counters/request IDs,
rate limits, CLI score/accounts/maintenance, backup SQLite+blobs và cleanup intents.
Bài dài dùng cửa sổ không chồng lấn; chỉ tổng hợp nếu tất cả cửa sổ chấm được;
luôn gửi teacher review. Band thresholds và checksum pins giữ nguyên.

## Phép đo thực tế

Evidence raw lưu ngoài Git tại
`../ai-assessor-cefr-runtime/evidence/parity-001/`; không chứa model/audio/credential
trong repository. Fixture audio public có source/license và hash ở runtime.

| Kiểm tra | Kết quả | Evidence raw |
| --- | --- | --- |
| Pytest toàn repo, không gồm smoke marker | 320 passed, 0 failed/skip | `pytest.log`, `coverage.json` |
| Browser portal và ghi âm WebM | 45 checks PASS; desktop 1280/mobile 390; console/failed/external requests = 0 | `browser/result.json`, screenshots |
| Browser regression W3 | 11 checks PASS | `w3-browser/`, `w3-browser.log` |
| Whisper-small + Silero + Ridge thật | Fixture 40s: COMPLETED/ESTIMATED, 96 comments, 0 invalid evidence; fixture 70s: REVIEW_REQUIRED/SCORE_AGGREGATED, hai cửa sổ 35s | `real-model/result.json` |
| Model smoke restart | Report/session được đọc lại, logout thu hồi session | `real-model/result.json` |
| SQLite migration 3 → 4 | Ba report JSON giữ nguyên SHA-256; counts cũ giữ nguyên trước khi thêm admin | `migration.json`, backup manifest |
| CLI account/backup/score và data controls | Tests bằng fixture PASS; delete rollback/cleanup retry, CAS, consent/export và claim contention được kiểm tra | `pytest.log` |
| Ruff, Markdown links, forbidden-files, pip check, wheel | PASS | logs tương ứng trong runtime |
| App chính sau restart | 18 checks PASS; HTTP Range 206 và evidence seek desktop/mobile; readiness tất cả model/DB/worker PASS | `live-ui.json` |

Score ở fixture chỉ kiểm hoạt động kỹ thuật, không phải nhãn chuẩn hoặc độ chính
xác CEFR. Window policy là thử nghiệm chưa validation; luôn teacher review.
Không dùng 5 điểm tiêu chí giả hoặc gán điểm overall cho từng tiêu chí.
Coverage từ `coverage.json`: lines 88.83% (3808/4287), branches 74.21% (889/1198), combined 85.63%. Không tuyên bố đạt gate W2 thay owner.

Live UI kiểm tra audio không có lỗi playback, console hay request ngoài. Chromium
hủy hai GET audio cũ bằng `net::ERR_ABORTED` khi seek/chuyển trang; các cancellation
này được ghi riêng trong `media_cancelled_requests`, không coi là lỗi tải audio.

Prompt và phạm vi ở sheet `Thắng`, dòng 14–15 trong
[AI Prompt Log W04](tc2-3-ai-usage/AI%20Prompt%20Log%20-%20W04%20-%202026-10-05_2026-10-11.xlsx)
sau khi tách workbook theo tuần (trước đó là dòng 39–40 trong bản tổng hợp).

## Bàn giao

Mở <http://127.0.0.1:8000/login>. Tài khoản fixture student/teacher/admin và mật khẩu
ngẫu nhiên ở file local `../ai-assessor-cefr-runtime/demo-accounts.json` (0600).
Startup: `../ai-assessor-cefr-runtime/start.sh`. Model, venv, config và data không
phụ thuộc thư mục tham chiếu; bản backup trước migration ở
`../ai-assessor-cefr-runtime/backups/before-parity-001/`.

Ridge v1 và v3 được giữ ngoài Git để kiểm tra; registry đánh dấu không tương thích
với pin hiện hành. Active Ridge v2, Whisper-small và Silero đều đã chạy thật.
Code, tests và hướng dẫn hiện tại không tự tải model hay dùng ASR giả.

Cập nhật 08/10/2026: người dùng đã yêu cầu xóa `ai-assessor-cefr-thamchie` và cache pip; đã hoàn tất sau khi kiểm tra bản sao lưu ngoài Git. Tham chiếu hiện tại là `../ai-assessor-cefr-sang` (`ThanhSangLouis/ai-assessor-cefr`). Xem [minh chứng dọn thư mục](cleanup-2026-10-08.md).
Không push/deploy hoặc tự ghi user acceptance.

## Giới hạn kỹ thuật được giữ rõ

- Chỉ local, fixture accounts; chưa nghiệm thu TLS/public hosting, dữ liệu người
  học thật, policy retention hay CEFR accuracy/WER/calibration.
- Endpoint/framework của dự án tiếp tục WSGI/SQLite; không cam kết compatibility
  URL `/api/v1` hoặc giao diện FastAPI của hồ sơ kỹ thuật nội bộ.
- HTML cũ vẫn hiển thị report đã lưu; report cũ không có refs chỉ được nghe toàn
  audio, không tạo timestamp chưa xác minh. Report mới lưu refs đã validation.
- Training notebooks/tools phụ thuộc `sandi-work/features_resp.py` và dataset ngoài
  source tham chiếu; Docker public hosting và các model khác đơn vị suy luận được
  ghi disposition trong [đối chiếu](../sources/capability-comparison-2026-10-08.md),
  không sao chép thành runtime giả đã chạy.
