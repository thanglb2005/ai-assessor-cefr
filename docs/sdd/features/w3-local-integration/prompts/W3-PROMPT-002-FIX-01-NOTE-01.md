# W3-PROMPT-002-FIX-01-NOTE-01 — QA observations trong correction đang chạy

Parent prompt: W3-PROMPT-002-FIX-01. Task: W3-TASK-007, same correction attempt; không mở scope/attempt mới. Repo /tmp/aicefr-w3-app-review. Authorization/vai trò/allowed files giữ nguyên.

Root đã đọc harness hiện tại trước source commit và có ba observations để đối chiếu khi debug: sau POST consent withdrawn bị deny, render_notice chỉ có link login, không có form logout; phải quay lại một trang authenticated có logout rồi kiểm revocation. Invalid revoked token qua AuthService bị AuthorizationError và WSGI controlled403, trong khi missing token là401; QA cần assert đúng boundary thay vì sửa production để hợp assertion sai. Student truy cập teacher route là role denial, hãy kiểm actual403/body ACCESS_DENIED, không hardcode foreign-owner404 message cho role denial.

Không bỏ console/network observations để ép PASS. Expected negative request status có thể kiểm bằng context.request hoặc ghi allowlist hẹp gắn request/case; console/application errors ngoài expected scenarios phải fail.

Test test_mobile_css_keeps_controls_within_viewport_and_visible_focus chỉ assert CSS strings, mirror implementation và không chứng minh layout. Bỏ test này (DOM regression test single document còn cần thiết) và dùng actual browser viewport/width/focus checks theo parent prompt. Không cần viết test mirror cho reversible CSS change.

Root sẽ re-run QA harness sau integration. Lưu correction source/evidence và mô tả fail/debug thật, không fake PASS hoặc ảnh.
