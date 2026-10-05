# W3-USER-002 — Xác nhận quyền dùng audio

Ngày: 02/10/2026. Người trả lời: Thắng. Nguồn: reply của request_user_input_async trong hội thoại này.

Câu hỏi đã gửi: “Để chạy smoke ASR thật của W3, model Whisper local và audio có quyền sử dụng đang ở đường dẫn nào trên máy bạn? Đường dẫn cũ `~/models/faster-whisper-small/` hiện không tồn tại. Mình vẫn tiếp tục triển khai và kiểm thử bằng fixture trong lúc chờ thông tin.”

Trả lời nguyên văn: “có quyền”.

Diễn giải áp dụng: xác nhận quyền sử dụng audio cho smoke local. Người dùng chưa cung cấp đường dẫn; Codex kiểm tra và dùng hai audio sẵn có trong kho kỹ thuật nội bộ, giữ model/audio/transcript ngoài Git, không gửi audio tới dịch vụ ngoài. Đây không phải xác nhận ground truth, calibration/accuracy hoặc nghiệm thu W3. Không tự ghi verdict APPROVED.
