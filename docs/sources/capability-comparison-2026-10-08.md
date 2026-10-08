# PARITY-001 — Đối chiếu chức năng và bổ sung code

Cập nhật lưu trữ 08/10/2026: thư mục tham chiếu cũ đã được xóa theo yêu cầu; source, tài liệu và dữ liệu local được giữ tại `../ai-assessor-cefr-runtime/backups/ai-assessor-cefr-thamchie-before-cleanup-2026-10-08` (không gồm `.venv`). Các đường dẫn/lệnh khảo sát cũ bên dưới là lịch sử; checksum và kết quả khảo sát không đổi.

Ngày: 08/10/2026. Repo dự án: `e2e7fead2df0cec266bcb5802e78d54c2c214d81`.
Nguồn khảo sát: cây `src/aicefr`, tests và tools trong hồ sơ kỹ thuật nội bộ
`../ai-assessor-cefr-thamchie`; metadata Git của nguồn chưa hợp lệ nên dùng file/hash.
Chủ dự án trực tiếp yêu cầu bổ sung code và chọn đầy đủ chức năng, gồm quản trị/thống kê.
Thực hiện trên `feat/PARITY-001-runtime-completeness`; user acceptance PENDING.

## Requirement và quyết định triển khai

Giữ pipeline và hợp đồng hiện hành; bổ sung các use case còn thiếu theo kiến trúc
WSGI/SQLite của dự án. Không đổi band thresholds, không lặp overall thành năm điểm,
không tự bật research consent, không dùng ASR giả khi thiếu model.
Đây là mở rộng sau W3 theo chỉ dẫn trực tiếp, không ghi đè verdict các phase W2/W3.
Impact: M01 (history/tasks), M06 (presentation/export), M07 (claim/history/stats),
M08 (admin/auth/storage/maintenance), pipeline (long-response support).
Owner review Nguyên/Sang và user acceptance chưa được tuyên bố APPROVED.

| Nhóm | Quan sát ở dự án trước bổ sung | Phạm vi code cần bổ sung |
| --- | --- | --- |
| QC/ASR/VAD/Ridge/consent/review | Đã có, 269 tests PASS | Giữ regression và provenance |
| Lịch sử và tiến độ sinh viên | Chỉ tra cứu khi biết response ID | Danh sách có paging/filter, tiến độ overall, audio, export/profile |
| Báo cáo bằng chứng | Service có comments nhưng HTML chưa hiển thị | Feedback, reasons, limitations, provenance và audio |
| Bài tập | Allowlist trong config, form nhập thủ công | Registry có version, danh sách đề/prompt và quản lý trạng thái |
| Thống kê giảng viên/quản trị | Chưa có route/UI | Tổng hợp trạng thái/band, phân biệt AI và teacher final |
| Quản trị | ActorRole.ADMIN có trong schema, chưa có portal | Accounts, trạng thái khóa/disable, audit, config/model status |
| Auth | Session TTL/logout có; chưa lockout | Lockout bền vững, khóa tài khoản thu hồi session, không lộ credential |
| Review | CAS revision có; claim chưa giữ owner | Owner của claim, release claim và history |
| Export/xóa | Chưa có | Owner export/delete; research opt-in riêng; erasure preview/confirm |
| Vận hành | Chưa có health/metrics/CLI | Liveness/readiness, counters, CLI account/score/maintenance |
| Backup/retention/orphans | Có orphan discovery thấp tầng | SQLite snapshot + blobs, dry-run mặc định, fixture-only execution |
| Bài nói dài | Scorer từ chối duration OOD | Window planning/inference, mọi tổng hợp đều teacher review và có provenance |

## Specification và kiểm tra

- Student chỉ xem/export/xóa bài của mình; absent và foreign resource đều 404.
- Teacher/admin xem cohort/history; quản trị account/config/export chỉ admin.
- Mọi mutation dùng same-origin/Bearer kiểm tra hiện hành, validation, CAS khi có
  revision, và audit cùng transaction. Không expose hash/password/session/path qua API.
- Task versions đã có bài nộp được giữ; cập nhật wording tạo version mới.
- Config chỉ sửa QC và dùng version mới; report đã lưu giữ provenance cũ.
- Model activation chỉ nhận artifact tương thích và đúng pin; model chưa có xác minh
  không được kích hoạt bằng cách bỏ checksum hoặc đổi band mapping.
- Research export cần opt-in đang active; số/coverage không được gọi là năm score.
- Delete/retention phải có preview/confirmation hoặc explicit apply, xử lý rollback,
  giữ append-only audit; không thực thi trên dữ liệu live trong lượt bổ sung code.
- Readiness kiểm model/file và DB; liveness không tiết lộ cấu hình. Metrics không có
  response IDs, actor IDs, transcript hoặc đường dẫn trong labels.
- Tests: migration preserve reports; authorization/CSRF/lockout/revocation;
  task versioning; statistics use teacher final separately; exports and withdrawal;
  transactional delete/retention/backup; review contention; long-audio evidence;
  full regression/lint/build và browser QA trên fixture.

Progress và phép đo cuối ghi ở hồ sơ verification của PARITY-001. Không coi số
lượng file hay dung lượng venv là phép đo đủ/thiếu chức năng.

## Đối chiếu sau triển khai

Inventory 80 file source (`.py/.js/.html/.json` trong `src/` và tools) được hash vào
`reference-inventory.json` ngoài Git. Chức năng được tích hợp theo module hiện hành;
không lấy chênh lệch số file làm bằng chứng thiếu code.

| Source ở hồ sơ kỹ thuật nội bộ | Code/chức năng tương ứng trong dự án |
| --- | --- |
| `api/main.py`, `api/web.py`, templates/static history/progress/stats/admin | `portal/router.py`, `portal/templates.py`, `portal/service.py`; UI và API có quyền theo role/owner |
| `storage/task_repository.py` | `portal/tasks.py`; create/version/close, CAS, giữ wording khi có bài nộp |
| `auth/passwords.py`, `auth_repository.py`, sessions, accounts CLI | `auth/service.py`, `storage/sqlite.py`, portal accounts và local commands; lockout/disable/session revoke |
| consent repository + research/owner export | `ConsentRecord.research_allowed`, portal export/profile/research, data control erasure |
| review lock/unlock/history/score correction | `review/service.py`, `review/sqlite.py`, portal history/reopen; owner/TTL, revision, before/after và audit |
| report comments/evidence + audio seek | `report/contracts.py`, `report/service.py`, `api/templates.py`, `api/static/report.js`; refs đã validation và seek timestamp tuyệt đối |
| browser recorder, compressed decoder, upload progress | `api/static/recorder.js`, `audio/recordings.py`, decoder; WebM/MP4, nghe lại và original blob immutable |
| `infra/queues.py`, `infra/limits.py`, startup job recovery | `local/worker.py`, `local/lock.py`, `limits.py`; worker riêng connection, durable pending, capacity, rate limits và interrupted audit |
| observability + health/metrics | `observability.py`, `portal/control.py`, WSGI request ID; admin operations view |
| `config.py`, QC/model admin | `portal/control.py`; QC version/CAS, registry compatibility và pin activation, report cũ không reattribute |
| retention + maintenance CLI | `portal/data.py`, `local/commands.py`; dry-run, xác nhận, cleanup intents, backup SQLite+verified blobs |
| `scoring/windows.py` | `scoring/windows.py` + pipeline; median candidate, toàn bộ cửa sổ phải chấm được, luôn review |
| CLI chấm audio | `python -m aicefr.local score`; xác thực fixture, pipeline thật, không fake fallback |
| Ridge artifact v1/v2/v3 | Được giữ độc lập ngoài Git; chỉ v2 đúng pin/unit được active |

Core QC/ASR/VAD/features/Ridge/report/review/storage đã có trước bổ sung; regression
được chạy tiếp. Research scripts `train_scorer.py`, `derive_model_v2.py`, notebook
và experiments không phải runtime chức năng còn thiếu: chúng cần dataset/feature
builder ngoài cây tham chiếu, hoặc thay calibration/model/unit. Không tự huấn luyện
hay kích hoạt model chưa được M05 review. DeBERTa/Whisper khác provenance, fake-ASR,
proxy criterion scores và overall lặp 5 lần không được đưa vào sản phẩm.

Docker/uvicorn trong hồ sơ hướng tới public deployment; phạm vi hiện tại là
loopback fixture app với wheel/CLI đã build. Không đưa cấu hình fake-ASR hoặc public
hosting của hồ sơ vào cấu hình chạy chính. Research/tool/deployment disposition
này không phải claim các artifact ấy đã chạy trên dự án.

Kết quả và nguồn evidence: [verification PARITY-001](../evidence/parity-001-verification-2026-10-08.md).
Review hợp đồng liên module và user acceptance vẫn PENDING. Không đổi các phase
W2/W3 sang APPROVED/DONE theo kết quả kỹ thuật của lượt này.
