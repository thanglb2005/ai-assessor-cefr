# W3 — Local Integration (Tích hợp ứng dụng local)

Version: v0.1 · ngày 02/10/2026 (Asia/Ho_Chi_Minh)
SCOPE ID: W3
SCOPE TYPE: feature
SCOPE ROOT: docs/sdd/features/w3-local-integration/
OWNER: Thắng; Codex điều phối/review; gpt-6-luna triển khai
LIFECYCLE: active
RELATED SCOPES: M01–M08
RESEARCH MODE: RUN — khảo sát revision hiện hành và API chính thức của adapter local; không thay rubric/model.

## Authorization (Quyền triển khai)

Thắng trực tiếp yêu cầu: “bạn hãy promt r gửi cho các subagent luna 6 đi làm task  hết của w3 đi, promt gì thì lưu vào các file theo chuẩn quy trình AI log, bạn là người reviewcode, tạo nhánh rieegn nha”. Đây là quyền triển khai, delegation bằng Luna và local branch/commit cho lượt này, thay executor và giới hạn read-only subagents của skill. Codex giữ vai trò reviewer. Không diễn giải chỉ dẫn thành các verdict APPROVED lịch sử hoặc nghiệm thu; các verdict cuối vẫn PENDING. Không có quyền push/deploy.

## Requirement và Acceptance Criteria

| FR | Hành vi | AC | Bằng chứng |
| --- | --- | --- | --- |
| W3-FR-001 | Nộp bài có owner/consent đi qua QC→ASR→features→scoring→report→review; mỗi thất bại giữ reason, không tạo điểm giả | W3-AC-001 | Integration test cho PASS, REVIEW/REJECT, ASR unavailable, thiếu model/features và scorer refusal |
| W3-FR-002 | Report, review decision/audit và trạng thái tồn tại qua restart; teacher_verified chỉ sau quyết định thật | W3-AC-002 | Restart và rollback test trên SQLite/blob ngoài repo; stale revision bị chặn |
| W3-FR-003 | Có CLI/local entrypoint, login/logout/consent, form nộp bài, report và teacher review/audio với kiểm quyền | W3-AC-003 | HTTP/browser fixture journey; student không đọc bài khác hoặc route teacher/admin; consent withdrawn chặn bài mới |
| W3-FR-004 | ASR/VAD adapter chỉ chạy local, không tự tải model, ghi đúng provenance; thiếu prerequisite hiển thị chưa đánh giá | W3-AC-004 | Unit adapter bằng mocked external boundary; smoke thực hoặc NOT_RUN với nguyên nhân |
| W3-FR-005 | CI, README và evidence dùng revision thực; prompt lưu trước dispatch và ghi Excel sheet Thắng | W3-AC-005 | Required checks, prompt log, raw report, review và final verification inspect được |

## Giới hạn

Giữ overall score/band và 5 coverage rows; Interaction=null/insufficient_evidence. Local demo chỉ dùng fixture/account giả danh. Ngưỡng QC demo phải ghi test/demo-only, cấu hình runtime thật truyền tường minh. Không chọn retention/export/delete policy, encryption, consent hay dữ liệu người học thật; không training/fine-tune, đổi band map, cloud hay production. ASR thật cần weight local + audio có quyền; không tải model/audio tự động.

USER VERDICT (nghiệm thu): PENDING.
