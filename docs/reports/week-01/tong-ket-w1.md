# Tổng kết tuần 1 — 14–18/09/2026

**Trạng thái:** DONE theo xác nhận của người dùng. Đây là bản tóm tắt bổ sung cho báo cáo Word gốc, không sửa số liệu hay nội dung trong báo cáo gốc.

## Phân công và kết quả

| Thành viên | Phần việc W1 do người dùng xác nhận | Minh chứng hiện có trong thư mục dự án |
| --- | --- | --- |
| Thắng | Tạo repo; phân chia module; lên plan; dựng quy trình SDD | Cây 8 module SDD và kế hoạch hiện tại phản ánh phần việc; link/commit repo W1 chưa được cung cấp; Git của thư mục dự án được khởi tạo ngày 25/09/2026 |
| Sang | Nghiên cứu rubric; tạo dự án Jira; vẽ diagram; lập rule cho AI | Rubric PDF gốc và hai biến thể ảnh sơ đồ lớp đã có; link Jira và tệp rule AI W1 chưa được cung cấp |
| Nguyên | Nghiên cứu Requirement/Specification; vẽ các sơ đồ use case; viết báo cáo tuần 1 | Báo cáo Word và ba ảnh use case nhúng đã có |

Các tệp hình nhúng trong Word được xác minh bằng hash: ba use case và một sơ đồ lớp. Hai ảnh sơ đồ lớp bổ sung của nhóm nằm ở `docs/design/week-01/` và khác hình lớp nhúng trong Word. Việc ai tạo từng biến thể hình chưa được xác định chỉ từ tên file.

## Số liệu ước tính cho bảng tiến độ

**Giả định lập kế hoạch, chưa phải timesheet đo thực:** mỗi thành viên làm 4 giờ/ngày trong 5 ngày, tương đương 20 giờ/người và 60 giờ công của nhóm. Phân rã sau chỉ để ước lượng khối lượng W1; người thực hiện có thể thay bằng giờ thực tế.

| Thành viên | Phân rã giờ giả định | Tổng |
| --- | --- | ---: |
| Thắng | Repo và chia module: 6 giờ; plan: 6 giờ; quy trình SDD: 8 giờ | 20 giờ |
| Sang | Rubric: 5 giờ; Jira: 3 giờ; diagram: 8 giờ; AI rules: 4 giờ | 20 giờ |
| Nguyên | Requirement/Specification: 8 giờ; use case: 6 giờ; báo cáo: 6 giờ | 20 giờ |
| **Nhóm** | **3 người × 5 ngày × 4 giờ/ngày** | **60 giờ** |

**Số lượng artifact kiểm thấy tại chỗ:** 1 báo cáo Word, 3 ảnh use case, 2 biến thể ảnh sơ đồ lớp do nhóm cung cấp. Số lượng đề xuất cho cấu trúc dự án: 8 module SDD. **Theo lời xác nhận của người dùng:** 1 repo, 1 dự án Jira và bộ AI rules đã được tạo; chưa có URL/commit/tệp rule W1 trong thư mục dự án để kiểm tra độc lập.

Mức hoàn thành công việc W1 được ghi là **100% theo xác nhận của người dùng**, không suy từ số giờ giả định. Không đưa ra phần trăm test coverage, độ chính xác CEFR hoặc số người tham gia thử nghiệm cho W1 vì chưa có phép đo tương ứng.

## Chuyển tiếp W2

W1 đóng ở cấp báo cáo tiến độ. Requirement, Specification, Test Plan và Plan/Tasks theo skill SDD của từng module trong repo dự án vẫn cần checkpoint riêng trước khi implement; việc này thuộc W2.
