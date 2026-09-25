# M03 — 02 Research (khảo sát ASR)

> **DRAFT v0.1 · 25/09/2026.** Phase 01 còn PENDING; `RESEARCH MODE: RUN` mới là đề xuất. File này là khảo sát để chủ dự án quyết định, chưa khóa engine/model hoặc Phase 03.

## Câu hỏi nghiên cứu W2

1. Engine/model local nào chạy được trên máy triển khai của nhóm, có quyền dùng và không tự gửi audio ra mạng?
2. Engine đó trả segment/word timestamp với định nghĩa và độ ổn định nào?
3. Khi không có model, audio hợp lệ hoặc transcript đáng tin, pipeline biểu diễn `NOT_RUN/UNRELIABLE/ASR_FAILED` thế nào để M04/M05 không suy tiếp?

## Nguồn đã xem

| Nguồn | Fact có thể dùng | Giới hạn |
| --- | --- | --- |
| [Đề cương và báo cáo W1 của nhóm](../../../sources/README.md) | Dự án cần transcript có provenance phục vụ chẩn đoán bài nói | Không phải phép đo WER hoặc quyết định model của repo mới |
| [Tài liệu chính thức faster-whisper](https://github.com/SYSTRAN/faster-whisper/blob/master/README.md) | Có tùy chọn word timestamps và ví dụ CPU/GPU; inference bắt đầu khi duyệt generator segment | Chưa xác nhận model, license weight, RAM/tốc độ trên máy nhóm; không khẳng định phù hợp trước smoke |
| Khảo sát read-only repo tiền nhiệm, xem [code survey](../../../sources/code-survey.md) | Trước đây có ASR adapter và test; giúp nhận diện boundary/failure cần test | Không mang code/config/model hoặc kết quả cũ sang |

## Adaptation Map

| Hạng mục | Quyết định bản nháp | Lý do |
| --- | --- | --- |
| Adapter/port local ASR | ADAPT ý tưởng boundary, viết implementation mới | Dễ thay engine và test failure path; không phụ thuộc cấu trúc cũ |
| Word timestamps | OPEN | Chỉ dùng nếu output engine thực có; M06 có thể dùng segment-level theo contract được duyệt |
| Model tải tự động | REJECT làm mặc định | Cần quyền, license, checksum và kiểm soát đường mạng |
| Test double | ADOPT cho unit test duy nhất | Không là bằng chứng ASR hay điểm CEFR |

## Evidence cần thu trước quyết định

- Cấu hình máy W2: OS, CPU/GPU, RAM, dung lượng trống; không ghi serial/PII.
- Engine/model version, nguồn tải/license, checksum, cách đặt local, command chạy offline và output smoke từ audio có quyền sử dụng.
- Nếu có bản chép tay được phép: đánh giá WER chỉ theo protocol/đơn vị phù hợp; không suy kết quả từ một smoke case.

**CODEX CHECK RESULT:** nguồn kỹ thuật đã xác định, điều kiện runtime/model còn `OPEN`. **User decision Research mode và Phase 03:** PENDING.
