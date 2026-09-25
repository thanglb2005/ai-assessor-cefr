# Nguồn tài liệu của đề tài

Dự án `ai-assessor-cefr` được **xây lại từ đầu**. Repo `../ai-assessor-cefr-thamchie` là phiên bản trước do chủ dự án thực hiện, không phải một sản phẩm bên thứ ba hay nguồn code được clone vào dự án mới. Hai đề cương DOCX do nhóm sở hữu được lưu nguyên bản dưới `original-documents/`; báo cáo fine-tune lịch sử của Thắng nằm dưới `prior-project-reports/`. Mỗi tài liệu có checksum để đối chiếu xuất xứ. Không chuyển mã nguồn, model artifact hoặc trạng thái phê duyệt sang implementation mới; kết quả test/metric của bản tham chiếu chỉ được ghi có xuất xứ tại đây, không tính là kết quả repo mới.

| ID | Tài liệu nguồn | Vai trò tại dự án mới | Trạng thái sử dụng |
| --- | --- | --- | --- |
| SRC-01 | [Đề cương v3.1](original-documents/De_cuong_AI_Assessor_CEFR_v3.1_ALDM-L.docx) · SHA-256 `cc0b81070dc7af37b153a032094216f3805296ff331734edf9d86c068dafdffe` | Nền tảng nghiên cứu, thuật ngữ, câu hỏi và phạm vi dài hạn | Tài liệu gốc của nhóm; các lựa chọn 10 tuần, 6 tiêu chí và chữ “chốt” trong file không tự áp dụng cho MVP 3 tuần |
| SRC-02 | [Đề cương chi tiết](original-documents/De_cuong_chi_tiet_AI_Assessor_CEFR_A2-B2.docx) · SHA-256 `c17b99aa9d1215d2ac5b9b139d6cc3a069a574eb419b0c814366c1137f51e3f1` | Bối cảnh và phương án ban đầu | Bản trước; dùng để thấy lịch sử hình thành ý tưởng, không làm chuẩn thiết kế hiện hành |
| SRC-03 | [Báo cáo W1](../reports/week-01/bao-cao-tuan-01.docx) và [tổng kết W1](../reports/week-01/tong-ket-w1.md) | Bằng chứng công việc W1 và hướng MVP 3 tuần do nhóm cung cấp | W1 hoàn thành theo chủ dự án; các claim nội dung chưa được xác minh độc lập |
| SRC-04 | [Rubric đồ án](../rubric/Rubric_Do_An_Mon_Hoc_CNPM_sinhvien.docx.pdf) | Yêu cầu hồ sơ/chấm đồ án | Nguồn chuẩn cho `docs/evidence/`, khác với rubric chấm Speaking cần giảng viên bộ môn duyệt |
| SRC-05 | [CEFR Companion Volume 2020, Appendix 3](https://rm.coe.int/cefr-companion-volume-with-new-descriptors-2020/16809ea0d4) | Nguồn chuẩn để khảo sát qualitative features của spoken language | Đã xác định trên website Council of Europe ngày 25/09/2026; nhóm vẫn cần diễn giải/rubric theo task và review học thuật |
| SRC-06 | [Báo cáo fine-tune DeBERTa do Thắng viết](prior-project-reports/deberta_cefr_finetune_thang.md) · SHA-256 `27b17e3519f5a648d9acff354bf1887493904a00bdbdee6b80d255d5f94c0a46` | Bằng chứng lịch sử về nhánh transcript; xem [kiểm tra chấm điểm](scoring-audit.md) | Kết quả dev của phiên bản trước; weight nằm ngoài Git, model chưa tích hợp vào app mới |

[Khảo sát chức năng và kết quả chạy test bản tham chiếu](code-survey.md) cùng [kiểm tra scorer/model hiện tại](scoring-audit.md) ghi nguồn tại một nơi. Chúng không là kết quả test hay yêu cầu sản phẩm của repo mới.

Hai DOCX được lưu byte-for-byte từ `../ai-assessor-cefr-thamchie/artifacts/source/documents/`. File `Dinh_huong_chi_tiet_10_tuan...docx`, `Phan_tich_va_huong_lam...docx`, ba presentation, SRS/SDD cũ và `markdown/` cũ vẫn ở repo tiền nhiệm để tránh nhiều bản gần trùng. Khi cần khảo sát lịch sử, dùng bản gốc tại đó và ghi quyết định áp dụng trong SDD của module; không viện dẫn đường dẫn code cũ làm yêu cầu sản phẩm.

## Quy tắc nguồn và diễn giải

1. Yêu cầu mới nhất của chủ dự án và W1 của repo mới quyết định phạm vi hiện hành. Đề cương gốc hỗ trợ giải thích, không thay các checkpoint SDD của repo mới.
2. Phân biệt `FACT` (nội dung có trong nguồn), `PROPOSED` (phương án của nhóm), `OPEN` (chưa chốt) và `MEASURED` (kết quả có dữ liệu/lệnh kiểm tra của repo mới).
3. Báo cáo kết quả ASR, chấm CEFR, hiệu năng, kiểm thử hoặc nghiên cứu người dùng chỉ xuất hiện sau khi có evidence thực tế tại `docs/sdd/modules/<module>/evidence/` và được dẫn sang `docs/evidence/` theo rubric.
4. Các tài liệu và hình W1 đã được chuyển để lưu trữ/đối chiếu nguồn; việc chuyển asset không có nghĩa chuyển implementation code.
