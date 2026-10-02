# W3-PROMPT-002-FIX-01-NOTE-02 — Baseline test dependency update

Parent W3-PROMPT-002-FIX-01, same attempt; W3-TASK-003/004/007. Repo /tmp/aicefr-w3-app-review.

Full suite có một failure ở old Silero missing-package test vì baseline80c6707 vẫn chứa speech code trước FIX-01. Source correction af5dc8a đã được root review/integrate và targeted tests PASS. Root sẽ cherry-pick chỉ code commit này vào worktree app-review, không chạm app dirty changes; actor thực hiện Git operation là root, không phải app agent. Allowed app files giữ nguyên.

Sau root thông báo baseline cập nhật, rerun full suite/coverage và browser nếu source UI/harness thay đổi. Không skip/xóa/hạ assertion test speech để che failure, không sửa speech source thuộc lane C. Raw app report giữ lịch sử 244 passed/1 failed trên old integrated baseline, rồi kết quả mới/source dependency head sau root update; user verdict PENDING. Root sẽ vẫn tự rerun final integration.
