# Quy tắc chung cho nhóm và AI agents

**Áp dụng cho toàn bộ repo.** Thắng, Sang, Nguyên và mọi phiên làm việc Codex/Antigravity đọc file này cùng [skill SDD dùng chung](.agents/skills/sdd-antigravity-orchestrator/SKILL.md) trước khi làm W2. Bản trong repo là phiên bản nhóm dùng; nếu máy cá nhân có bản khác, dùng bản trong repo. Khi sửa quy trình, cập nhật một bản này qua Git và báo cả nhóm.

## Nguồn quyết định và trạng thái

1. Chỉ dẫn mới nhất của chủ dự án và các quyết định đã được họ xác nhận.
2. Requirement, Research (nếu chọn RUN), Specification, Test Plan, Plan/Tasks đã được duyệt trong `docs/sdd/modules/<module>/`.
3. File quy tắc này và skill SDD. `AI_CONTEXT.md` là bản đồ ngắn, không thay Specification.
4. Tài liệu ở `docs/sources/` và repo `../ai-assessor-cefr-thamchie` là nguồn tham khảo do nhóm tạo; không tự chuyển code, số đo, trạng thái test hoặc approval cũ sang repo mới.

W1 (14–18/09/2026) **DONE theo chủ dự án**; minh chứng lịch sử vẫn có mục cần bổ sung. Các SDD W2 hiện là **DRAFT, Phase 01 PENDING**. Việc chia người đọc/review tài liệu được thực hiện ngay; prompt triển khai cho Antigravity chỉ phát khi module có Phase 01, 03, 04 và 05 `APPROVED` theo đúng thứ tự. Không ghi `APPROVED`, `PASS`, `DONE` thay chủ dự án hoặc từ kết quả dự kiến.

## Một quy trình SDD cho cả ba người

- Mỗi module M01–M08 sở hữu `01-requirement.md`, Research khi được chọn, `03-specification.md`, `04-test-plan.md`, `05-plan.md`, `06-tasks.md`, `07-status.md` và `prompts/`, `evidence/`, `reviews/` riêng. Đọc `07-status.md` trước khi sửa scope. Thay đổi contract liên module phải nêu impact, thống nhất với owner liên quan và duyệt lại phase bị ảnh hưởng.
- Người phụ trách module chuẩn bị nội dung và kiểm tra nguồn; Codex viết prompt, điều phối checkpoint và review actual diff/evidence; Antigravity triển khai và chạy test/browser QA theo prompt đã duyệt; chủ dự án quyết định verdict. Các thành viên có thể dùng phiên Codex riêng cho module của mình, nhưng cùng skill và cùng quy tắc này.
- Mỗi task chỉ có một owner, vùng file được sửa và dependency rõ trong `docs/plan/week-02.md`/SDD. Trước khi sửa source chung, thông báo owner module liên quan; không để hai phiên AI cùng sửa một vùng source tại một thời điểm. Dùng branch/commit riêng có Task ID, review diff trước khi gộp. Không đưa thay đổi ngoài task vào commit.
- Prompt Antigravity phải được lưu tại `docs/sdd/modules/<module>/prompts/` và ghi Prompt ID, Task ID, base revision/fingerprint vào log local **trước khi gửi**. Antigravity trả raw report, diff/commit và lệnh/kết quả kiểm tra; lưu tại `evidence/` local, review tại `reviews/`, cập nhật `07-status.md`. Bản chat hay lời nhắc “dùng skill” không tự lưu prompt/evidence.

## Minh chứng, dữ liệu và chất lượng

- Mỗi người ghi **mọi lần dùng AI** vào sheet mang tên mình trong `docs/evidence/tc2-3-ai-usage/AI Prompt Log.xlsx`: ngày, người, công cụ, công việc, prompt, link minh chứng. Sheet `Tổng hợp` cộng cả ba sheet. Prompt triển khai còn phải có bản file/log tại module. `docs/evidence/` là hồ sơ nộp theo rubric, dẫn về bằng chứng gốc trong module; tránh nhân bản file và claim.
- Chỉ dùng số liệu đo được trên **repo mới** và revision ghi rõ. Kiểm thử, coverage, ASR/model version, consent và nguồn audio phải có evidence truy cập được. Ghi `NOT_RUN`/`NOT_EVALUATED` khi chưa có; không biến fixture hoặc metric của phiên bản trước thành kết quả CEFR thực nghiệm mới.
- Bản nháp sản phẩm dùng 5 tiêu chí Range, Accuracy, Fluency, Coherence, Phonology; chỉ hiển thị overall score/band và coverage/evidence của từng tiêu chí. `Interaction=null` với `insufficient_evidence` cho bài độc thoại. Không sao chép overall thành năm điểm tiêu chí. Mọi thay đổi rubric/band mapping phải quay về SDD M05 và được duyệt.
- Không commit secret, audio hoặc dữ liệu cá nhân thật, model weights không có quyền phân phối. Tuân thủ `.gitignore`; manifest ghi nơi giữ bằng chứng bị hạn chế truy cập. Không push, deploy, gửi dữ liệu ra dịch vụ ngoài hoặc thay đổi production nếu chưa có quyền rõ từ chủ dự án.

## Bắt đầu W2

Đọc [kế hoạch W2](docs/plan/week-02.md), [bản đồ tài liệu](docs/README.md), module được giao và Status của nó. Gửi review/đề xuất sửa SDD theo FR/AC/Test/Task ID. Chỉ sau verdict Phase 05 mới tạo prompt triển khai với helper `scripts/workspace_fingerprint.py` trong skill chung. Nếu thông tin quan trọng còn thiếu, ghi câu hỏi/blocker ở module và hỏi chủ dự án; không tự điền dữ liệu giả như kết quả thật.
