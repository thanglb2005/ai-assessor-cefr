# Bản đồ tài liệu

| Nơi lưu | Nội dung | Quy tắc |
| --- | --- | --- |
| `plan/three-week-roadmap.md` | Tổng quan 3 tuần và các quyết định còn mở | Dẫn tới ba kế hoạch tuần riêng |
| `plan/week-01.md`, `week-02.md`, `week-03.md` | Kế hoạch/record theo tuần | W1 DONE; W2 chưa xác minh; W3 DRAFT |
| `sdd/modules/<slug>/` | SDD độc lập theo 8 module M01–M08 | Mỗi module có Prompt Log, Evidence Manifest, Review Records và Status local |
| `sdd/prompt-log.md` | Chỉ mục log prompt của 8 module | Prompt thật nằm trong prompts/ của từng module |
| `evidence/` | Hồ sơ minh chứng theo rubric và checklist 12 mục | Dẫn tới artifact gốc, không nhân đôi số liệu |
| `design/week-01/` | Hai bản hình sơ đồ lớp do nhóm đưa vào | Dùng bản sáng để review; bản tối là biến thể trình bày |
| `reports/week-01/` | Tổng kết W1, báo cáo Word gốc và 4 hình nhúng đối chiếu với bản tiền nhiệm do nhóm làm | Giữ Word nguyên bản; hình lưu riêng để dẫn chiếu |
| `rubric/` | PDF rubric gốc và text trích xuất để tìm kiếm | PDF là bản đối chiếu chính; text chỉ hỗ trợ tra cứu |
| `sources/` | Hai đề cương DOCX gốc của nhóm, checksum và code survey read-only | Nguồn học thuật/lịch sử; không chuyển mã nguồn cũ |

## Nguồn và tình trạng

- `reports/week-01/bao-cao-tuan-01.docx` là tài liệu **đã có trước** khi khởi tạo cấu trúc này, chưa được mình sửa nội dung hay xác nhận các claim trong đó.
- `reports/week-01/figures/01a_usecase_sinhvien.png`, `01b_usecase_giangvien.png`, `01c_usecase_quantri.png`, `02_class.png` là bản sao byte-for-byte từ `../aiassessor-cefr/docs/sdd/images/`. SHA-256 khớp với bốn ảnh nhúng trong báo cáo Word theo thứ tự image1–image4.
- `design/week-01/class-diagram-light.png` và `class-diagram-dark.png` là hai ảnh có sẵn ở root dự án mới, chỉ đổi nơi lưu/tên. Chúng **khác** hình `reports/week-01/figures/02_class.png` nhúng trong Word; không tự nhận file `.drawio` của phiên bản trước do nhóm thực hiện là nguồn sửa của hai ảnh mới.
- `rubric/Rubric_Do_An_Mon_Hoc_CNPM_sinhvien.docx.pdf` và `rubric/rubric_text_trich_xuat.txt` được chép từ `../aiassessor-cefr/docs/rubric/`.

## Tài liệu cũ cần quyết định trước khi chép thêm

Đề xuất **không chuyển nguyên bộ** `markdown/`, `artifacts/derived/`, notebook, các roadmap 7/10/12/15 tuần và bản SRS/SDD cũ. Chúng có nhiều phiên bản, mốc thời gian khác và claim chưa kiểm định; SDD mới phải theo từng module. Khi cần đối chiếu một quyết định hay hình cụ thể, dẫn chiếu file gốc do nhóm tạo trong `../aiassessor-cefr/` và đưa phần đã chọn vào Requirement/Research của module tương ứng. Quyết định giữ thêm SRS/SDD cũ hoặc đề cương cần người dùng xác nhận.

Trước khi sử dụng báo cáo tuần 1 làm căn cứ nghiệm thu, cần rà soát các ví dụ số đo/ca sử dụng, tuyên bố pháp lý, độ chính xác mô hình và trạng thái phê duyệt. Tài liệu cũ có chỗ mô tả 6 tiêu chí/Task C, trong khi báo cáo mới mô tả độc thoại 5 tiêu chí. Xem câu hỏi mở trong kế hoạch.

## Danh mục tài liệu cũ đề xuất giữ hoặc bỏ

| Nguồn trong phiên bản trước | Đề xuất | Lý do |
| --- | --- | --- |
| docs/rubric/ | Đã chép PDF + text tra cứu | Tiêu chí đánh giá của đồ án |
| docs/sdd/images/01a*, 01b*, 01c*, 02_class.png | Đã chép 4 hình vào reports/week-01/figures/ | Bốn hình nhúng thật trong báo cáo Word mới, đã kiểm tra hash |
| docs/srs/SRS.md, docs/sdd/SDD.md | Chưa chép; tham khảo khi soạn module | Bản cũ có 41 FR/12 tuần và approval không áp dụng cho repo mới; nếu cần giữ thì đặt dưới reference/legacy/ có nhãn rõ |
| markdown/week_01/01_glossary.md, 16_data_management_plan.md, 21_week1_decision_log.md | Chưa chép; trích phần được duyệt vào scope mới | Có ích nhưng nhiều quyết định còn PROPOSED hoặc phải chỉnh theo phạm vi độc thoại |
| docs/reports/, markdown/weekly_reports/, docs/ai-usage-log.md | Không chép lịch sử cũ; tạo báo cáo/log mới khi có hoạt động | Tránh dùng tiến độ, metric và nhật ký AI của phiên bản trước do nhóm thực hiện làm minh chứng repo mới |
| docs/plan/, markdown/ còn lại, artifacts/derived/, notebooks/ | Không chép theo mặc định | Trùng phiên bản, khác thời lượng kế hoạch hoặc là artifact dẫn xuất |

## Prompt Antigravity và evidence

Bộ hồ sơ nộp theo rubric nằm tại [docs/evidence/](evidence/README.md); M06 Diagnostic Report là chức năng tạo báo cáo cho một bài nói. Hồ sơ rubric có thư mục riêng cho TC1, TC2.1–TC2.7, TC3–TC6 và hồ sơ quy trình. Skill SDD quy định prompt, raw report, evidence và review thuộc scope module. Xem [chỉ mục Prompt Log](sdd/prompt-log.md), rồi mở prompts/prompt-log.md và evidence/evidence-manifest.md của module tương ứng. Prompt phải được lưu thành file và ghi log trước khi bàn giao; bản chat hoặc lời nhắc dùng skill không tự lưu file. Status module dẫn tới Prompt ID/evidence/review mới nhất. Hiện các module có bộ SDD W2 bản nháp nhưng vẫn ở Phase 01 DRAFT; chưa có prompt triển khai nào được phát hành.
