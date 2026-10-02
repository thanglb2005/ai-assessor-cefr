# W3 — Implementation Review, attempt 01

Reviewer: Codex lead. Date: 02/10/2026. User verdict: `PENDING`.
Method: đọc actual source/tests/diff và independently run integrated regression; không chỉ dùng raw report của agents.

Initial source commits: pipeline `66d23d4`, app `6415e11`, speech `dfac63a`; root integrated tại `80c6707`. Có 236 tests PASS, 0 skip với pinned external Ridge artifact. Kết quả này là intermediate, không thay final rerun.

| Finding | Severity | Evidence và tác động | Correction |
| --- | --- | --- | --- |
| W3-RV-001 | MAJOR | ASR local yêu cầu preprocessor_config.json mà revision M03 ghim không có; model hợp lệ bị từ chối | W3-PROMPT-003-FIX-01; af5dc8a sửa về bốn file M03 |
| W3-RV-002 | MAJOR | Nhãn small lấy từ config không kiểm bytes model; provenance có thể sai | af5dc8a kiểm SHA256 cả bốn file trước canonical small; labels khác giữ mismatch |
| W3-RV-003 | MAJOR | Missing-Silero test không mock import; khi optional package thật được cài sẽ không deterministic | af5dc8a mock import/version boundaries; root môi trường đã cài optional deps |
| W3-RV-004 | MAJOR | Coordinator integration chưa test SQLite thật khi report/candidate/decision lỗi; coverage critical rollback thiếu | W3-PROMPT-001-FIX-01 đang triển khai |
| W3-RV-005 | MAJOR | Unexpected pipeline lỗi bị gắn ASR_FAILED; artifact thiếu có thể che refusal ASR | W3-PROMPT-001-FIX-01 đang triển khai |
| W3-RV-006 | MAJOR | Public coordinator constructor không có type hints, unused protocol và unit-of-work port không rõ | W3-PROMPT-001-FIX-01 đang triển khai |
| W3-RV-007 | MAJOR | Logout protocol yêu cầu delete_session nhưng repositories chính chưa implement | W3-PROMPT-002-FIX-01 đang triển khai |
| W3-RV-008 | MAJOR | Local config nâng consent version nhưng submit có thể chọn old version | W3-PROMPT-002-FIX-01 đang triển khai |
| W3-RV-009 | MAJOR | App factory mới chưa kiểm chứng với các services đã tích hợp; browser journey chưa chạy | W3-PROMPT-002-FIX-01 đang triển khai |
| W3-RV-010 | MINOR | Teacher detail nhúng full report HTML; một số pages thiếu viewport/demo label | Bundle trong W3-PROMPT-002-FIX-01 |

Speech correction re-review: đọc source diff af5dc8a và tests mock pin/refusal/cache/package version. Hash M03 đối chiếu với actual local files. Canonical small chỉ nhận đúng bytes; alias chưa duyệt không được AsrService coi là small. Chưa dùng fixture tests để claim smoke thật.

Clean Code checklist: kiểm dependency boundaries/type hints, private data không có trong exception logs, deterministic test mocks, transaction ownership, migration compatibility, no duplicated band/feature mapping, no fake default inference và allowed-file isolation. Findings còn mở được đánh giá lại sau source correction; final recommendation chưa phát hành.
