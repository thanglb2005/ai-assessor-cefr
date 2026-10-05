# AI Usage Log — Võ Thanh Sang (W1–W3)

**Phụ trách:** M03 Nhận dạng giọng nói, M04 Trích đặc trưng, M05 Chấm điểm.
**Nguồn chuẩn:** Google Sheet [AI Prompt Log](https://docs.google.com/spreadsheets/d/1CxQkn5DaPVDHiWztkcvAdlL1kD1P6JRxtN2zTIeMhOU), ba tab của Sang: `Sang(Week 1)`, `Sang` (W2), `Sang(Week 3)`.
**Bản xuất:** 04/10/2026.

| Tuần | Tab | Số dòng |
| --- | --- | ---: |
| W1 (14–20/09) | [`Sang(Week 1)`](https://docs.google.com/spreadsheets/d/1CxQkn5DaPVDHiWztkcvAdlL1kD1P6JRxtN2zTIeMhOU/edit#gid=187665897) | 14 |
| W2 (21–27/09) | [`Sang`](https://docs.google.com/spreadsheets/d/1CxQkn5DaPVDHiWztkcvAdlL1kD1P6JRxtN2zTIeMhOU/edit#gid=1592849438) | 17 |
| W3 (28/09–04/10) | [`Sang(Week 3)`](https://docs.google.com/spreadsheets/d/1CxQkn5DaPVDHiWztkcvAdlL1kD1P6JRxtN2zTIeMhOU/edit#gid=1773459286) | 24 |
| **Tổng** | | **55** |

- **Bản đầy đủ:** [ai-usage-log-sang-W1-W3.csv](ai-usage-log-sang-W1-W3.csv), đủ 9 cột theo mẫu: ngày, người tạo, công cụ, phiên bản model, công việc, prompt, minh chứng, nội dung AI tạo ra, phần Sang sửa hoặc hoàn thiện.
- **Dòng 28/09:** có ở cả tab `Sang` lẫn `Sang(Week 3)`; trong bản xuất chỉ tính một lần, vào W3.
- **Công cụ:** cả ba tuần chỉ dùng **Claude** (Claude Opus 5.5 qua Claude Code, ứng dụng desktop). Không dùng Antigravity cho phần của Sang.

**Đối chiếu với Git (quy tắc chặn G4):** mỗi dòng có minh chứng là PR, commit hoặc tệp.
- W1: repo lưu trữ `Nguyneee/ai-assessor-cefr`, PR #4–#7, #9–#30 và các commit use case ngày 20/09. PR #8 là của Thắng, không tính.
- W2 và W3: repo này `thanglb2005/ai-assessor-cefr` (PR #1–#10, #25–#28) và repo gốc `ThanhSangLouis/ai-assessor-cefr` (PR #1–#4).
- Hai repo `Nguyneee/…` và `ThanhSangLouis/…` đang **private**. Cần cấp quyền đọc cho GVHD và hội đồng để kiểm tra (quy tắc chặn G8).

**Che số liệu:** 2 ô có số liệu suy ra từ corpus Speak & Improve đã được che trong bản public này, vì giấy phép corpus cấm công bố khi chưa được CUP&A cho phép. Bản đầy đủ nằm ở Google Sheet (giới hạn quyền truy cập).


## W1 (14–20/09) — tab `Sang(Week 1)`

| # | Ngày | Công việc | Minh chứng |
| ---: | --- | --- | --- |
| 1 | 9/14/2026 | Sản phẩm web — chấm được bài nói dài, hai màn hình tổng hợp, sửa lỗi giao diện | <https://github.com/Nguyneee/ai-assessor-cefr/pull/4> |
| 2 | 9/14/2026 | Tài liệu — đồng bộ SRS/SDD với mã nguồn và tài liệu Google Docs | <https://github.com/Nguyneee/ai-assessor-cefr/pull/5> |
| 3 | 9/14/2026 | Sản phẩm web — báo chưa ký đồng thuận trước khi ghi âm | <https://github.com/Nguyneee/ai-assessor-cefr/pull/6> |
| 4 | 9/14/2026 | M03 ASR — nửa sau bài nói dài không chấm được | <https://github.com/Nguyneee/ai-assessor-cefr/pull/7> |
| 5 | 9/19/2026 | Kế hoạch — cập nhật tài liệu sau fine-tune DeBERTa, phân công W5–W15 | <https://github.com/Nguyneee/ai-assessor-cefr/pull/9>, <https://github.com/Nguyneee/ai-assessor-cefr/pull/10> |
| 6 | 9/19/2026 | Nghiên cứu — hướng phát triển tiếp ngoài spec hiện tại | <https://github.com/Nguyneee/ai-assessor-cefr/pull/11> |
| 7 | 9/19/2026 | CI — bật lại pipeline gọn nhưng đủ cho rubric | <https://github.com/Nguyneee/ai-assessor-cefr/pull/12> |
| 8 | 9/19/2026 | Thiết kế — một sơ đồ lớp chuẩn hướng đối tượng | <https://github.com/Nguyneee/ai-assessor-cefr/pull/13>, #14, #15; <https://app.diagrams.net/#G14Yt7sDxBX-t8wUy2cNQigj8AGnZFW2_H> |
| 9 | 9/19/2026 | Thiết kế — tinh chỉnh lớp và kiểu dữ liệu trên sơ đồ lớp | <https://github.com/Nguyneee/ai-assessor-cefr/pull/16>, #17, #18, #19 |
| 10 | 9/19/2026 | Thiết kế — gọn lại ReasonCode và đưa bộ sinh sơ đồ vào repo | <https://github.com/Nguyneee/ai-assessor-cefr/pull/20>, #22, #23, #24 |
| 11 | 9/19/2026 | Báo cáo tuần 1 — đối chiếu rubric và viết đầy đủ các mục | <https://github.com/Nguyneee/ai-assessor-cefr/pull/21> |
| 12 | 9/20/2026 | Thiết kế — ký hiệu UML: bội số, thuộc tính tham chiếu, không để kiểu mồ côi | <https://github.com/Nguyneee/ai-assessor-cefr/pull/25>, #26, #27, #28, #29 |
| 13 | 9/20/2026 | Thiết kế — thay Map bằng lớp giá trị Feature, sắp lại đường nối | <https://github.com/Nguyneee/ai-assessor-cefr/pull/30>; <https://app.diagrams.net/#G14Yt7sDxBX-t8wUy2cNQigj8AGnZFW2_H> |
| 14 | 9/20/2026 | Use case và repo — vẽ lại ba sơ đồ use case, tạo lại repo sạch | Commit bcc3c47 → c9118c3 trên repo cũ; <https://github.com/ThanhSangLouis/ai-assessor-cefr> (commit a038aab) |

## W2 (21–27/09) — tab `Sang`

| # | Ngày | Công việc | Minh chứng |
| ---: | --- | --- | --- |
| 1 | 9/26/2026 | M03 ASR, M04 Features, M05 Scoring — Phase 01: rà soát Requirement v0.1 của ba module do Sang phụ trách, đối chiếu với model chấm điểm Ridge v2 của nhóm | <https://github.com/thanglb2005/ai-assessor-cefr/pull/1> |
| 2 | 9/26/2026 | M03/M04/M05 — soạn Requirement v0.2 theo quyết định của owner và ghi verdict Phase 01 | <https://github.com/thanglb2005/ai-assessor-cefr/pull/1> (commit a11f03a) |
| 3 | 9/26/2026 | M03/M04/M05 — Phase 03: khảo sát code tham chiếu (Research) và viết Specification v0.2 | <https://github.com/thanglb2005/ai-assessor-cefr/pull/7> (PR #2 đã gộp vào #7) |
| 4 | 9/26/2026 | M03/M04/M05 — chốt 5 quyết định mở, ghi verdict Phase 03 và soạn Test Plan v0.2 (Phase 04) | <https://github.com/thanglb2005/ai-assessor-cefr/pull/7> (PR #3 đã gộp vào #7) |
| 5 | 9/26/2026 | M03/M04/M05 — chốt chính sách coverage, ghi verdict Phase 04 và soạn Plan & Tasks v0.2 (Phase 05) | <https://github.com/thanglb2005/ai-assessor-cefr/pull/7> (PR #4 đã gộp vào #7) |
| 6 | 9/26/2026 | M05 — quyết định nơi đặt artifact model ridge_resp_v2.json (P05-D-001) | <https://github.com/thanglb2005/ai-assessor-cefr/pull/7> (PR #4 đã gộp vào #7) |
| 7 | 9/26/2026 | Quản lý dự án — soạn tin nhắn dependency gửi Thắng và lập backlog Jira cho cả nhóm (vai Scrum Master) | <https://vothanhsangdev.atlassian.net/jira/software/projects/SCRUM/boards/1> |
| 8 | 9/26/2026 | Quản lý dự án — rà soát chất lượng backlog Jira (vai QA senior) và liên kết Jira với GitHub | <https://vothanhsangdev.atlassian.net/jira/software/projects/SCRUM/boards/1> |
| 9 | 9/26/2026 | M03 + nền tảng — liên kết Jira với GitHub, dựng CI tối thiểu, tải weight whisper-small (SCRUM-17, SCRUM-21) | <https://github.com/thanglb2005/ai-assessor-cefr/pull/5> |
| 10 | 9/26/2026 | Nền tảng — dựng khung repo Python và contract dữ liệu dùng chung cho M03–M05 (SCRUM-14, SCRUM-15) | <https://github.com/thanglb2005/ai-assessor-cefr/pull/6> |
| 11 | 9/26/2026 | M05 Scoring — M05-TASK-002: loader artifact có hash ghim và toán chấm Ridge (SCRUM-27); ghi verdict Phase 05 | <https://github.com/thanglb2005/ai-assessor-cefr/pull/7> |
| 12 | 9/26/2026 | M03/M04/M05 — đưa các PR qua CI để merge, kiểm lại Definition of Ready Phase 05, gộp PR tài liệu | <https://github.com/thanglb2005/ai-assessor-cefr/pull/7> (PR #2–#4 đã gộp vào #7) |
| 13 | 9/26/2026 | M05 Scoring — M05-TASK-001: scorer 8 bước fail-closed và coverage 5 tiêu chí (SCRUM-28); gộp toàn bộ phần của Sang vào một PR | <https://github.com/thanglb2005/ai-assessor-cefr/pull/7> |
| 14 | 9/26/2026 | M03 ASR + M04 Features — task W2: AsrService, phát hiện hallucination, ánh xạ identifier; 18 công thức đặc trưng, FeatureExtractor (SCRUM-18, 19, 20, 24, 25) | <https://github.com/thanglb2005/ai-assessor-cefr/pull/8> |
| 15 | 9/26/2026 | M03/M04/M05 — Phase 07 Implementation Review cho 7 task W2 đã merge, sửa finding | <https://github.com/thanglb2005/ai-assessor-cefr/pull/9> |
| 16 | 9/27/2026 | M03/M04/M05 — ghi verdict Phase 07, đưa follow-up lên Jira, chạy Phase 08 Final Verification trên main | <https://github.com/thanglb2005/ai-assessor-cefr/pull/10> |
| 17 | 9/27/2026 | M03/M04/M05 — ghi verdict Phase 08, hồ sơ và verdict Phase 09 Acceptance, gom vào một PR cuối | <https://github.com/thanglb2005/ai-assessor-cefr/pull/10> |

## W3 (28/09–04/10) — tab `Sang(Week 3)`

| # | Ngày | Công việc | Minh chứng |
| ---: | --- | --- | --- |
| 1 | 9/28/2026 | Quản lý dự án — thiết lập Jira Automation cho project AI Assessor CEFR (vai Scrum Master) | <https://vothanhsangdev.atlassian.net/jira/software/projects/SCRUM/settings/automate> |
| 2 | 10/2/2026 | Thiết kế — rà soát sơ đồ lớp (class diagram) của dự án trên draw.io theo chuẩn UML và hướng đối tượng | <https://app.diagrams.net/#G14Yt7sDxBX-t8wUy2cNQigj8AGnZFW2_H> |
| 3 | 10/2/2026 | Thiết kế — tạo trang bản hoàn thiện của sơ đồ lớp trên draw.io | <https://app.diagrams.net/#G14Yt7sDxBX-t8wUy2cNQigj8AGnZFW2_H> |
| 4 | 10/2/2026 | Nghiên cứu — kiến trúc và tính năng nâng cấp khóa luận (W4–W15) | Tệp _bao-cao/ke-hoach-nang-cap-khoa-luan.md (lưu nội bộ vì có số liệu suy ra từ S&I) |
| 5 | 10/2/2026 | Thiết kế ↔ code — đối chiếu code repo nộp bài với sơ đồ lớp bản hoàn thiện | Tệp _bao-cao/doi-chieu-thiet-ke-code.md và phụ lục (lưu nội bộ) |
| 6 | 10/2/2026 | Bảo trì — kiểm tra repo gốc và sao lưu toàn bộ dự án trước khi phát triển tiếp | Tệp _backup/ai-assessor-backup-2026-10-02.zip và _backup/KHOI_PHUC.md (lưu máy cá nhân) |
| 7 | 10/2/2026 | Thiết kế — chốt D1–D9, sinh sơ đồ lớp thiết kế đích v3 và commit vào repo gốc | <https://github.com/ThanhSangLouis/ai-assessor-cefr/pull/1> |
| 8 | 10/3/2026 | Tính năng bứt phá D022 — Trust Layer CV+, lá chắn ngôn ngữ và lạc đề, chỉ báo theo tiêu chí, kiểm thử hành vi (repo gốc) | <https://github.com/ThanhSangLouis/ai-assessor-cefr/pull/2> |
| 9 | 10/3/2026 | Kiểm thử — tự test giao diện trên localhost, sửa lỗi và viết hướng dẫn test lại | <https://github.com/ThanhSangLouis/ai-assessor-cefr/pull/2> (commit 2b32c4f, 1975211); tệp _bao-cao/huong-dan-test-ui.md |
| 10 | 10/3/2026 | Review code — rà soát toàn bộ repo gốc, sửa nhóm lỗi critical và high | <https://github.com/ThanhSangLouis/ai-assessor-cefr/pull/3> (commit 97ed74a); tệp _bao-cao/review-code-repo-goc.md |
| 11 | 10/3/2026 | Review code — sửa 11 lỗi mức medium | <https://github.com/ThanhSangLouis/ai-assessor-cefr/pull/4> (commit df71196) |
| 12 | 10/3/2026 | CI — xử lý bước quét lộ khóa (gitleaks) báo đỏ ở PR #3 và #4 | <https://github.com/ThanhSangLouis/ai-assessor-cefr/pull/3> (commit e09a725); <https://github.com/ThanhSangLouis/ai-assessor-cefr/pull/4> (commit 18b1896) |
| 13 | 10/3/2026 | Quản lý dự án — đánh giá hiện trạng code repo nộp bài và lập kế hoạch W4 cho cả nhóm | Tệp _bao-cao/ke-hoach-week-04.md (giao Thắng commit thành docs/plan/week-04.md) |
| 14 | 10/3/2026 | Chuẩn bị trình bày — tài liệu học bài sơ đồ lớp theo hướng đối tượng | Tệp _bao-cao/hoc-bai-so-do-lop.md |
| 15 | 10/3/2026 | M05 — M05-TASK-004 test tích hợp M04 → M05 và cập nhật trạng thái SDD M03–M05 (SCRUM-29) | <https://github.com/thanglb2005/ai-assessor-cefr/pull/25> (commit c801d3b, f493612) |
| 16 | 10/3/2026 | Quản lý dự án — rà toàn bộ task của Sang trên repo nộp bài và cập nhật Jira | <https://vothanhsangdev.atlassian.net/jira/software/projects/SCRUM/boards/1> |
| 17 | 10/3/2026 | M03 — follow-up 07-A1-03: chép lý do QC sang Transcript khi QC REJECT (SCRUM-50) | <https://github.com/thanglb2005/ai-assessor-cefr/pull/26> (commit c06e997) |
| 18 | 10/3/2026 | M05 — error analysis bộ chấm, kéo vào sprint W3 (SCRUM-53) | <https://github.com/thanglb2005/ai-assessor-cefr/pull/27> (commit 3c98a00); báo cáo chi tiết lưu nội bộ |
| 19 | 10/3/2026 | M03/M05 — merge PR W3 và lập hồ sơ Phase 07–09 đợt A2 | <https://github.com/thanglb2005/ai-assessor-cefr/pull/28> (commit 21cfbd4) |
| 20 | 10/3/2026 | Repo gốc — merge chuỗi PR #1 → #4 | <https://github.com/ThanhSangLouis/ai-assessor-cefr/pull/1> → #4 (merge commit 00968bf, 45efe67, 57f8c96, 6784d7d) |
| 21 | 10/3/2026 | Nghiên cứu — mô tả pipeline fine-tune các mô hình của đồ án | Tệp _bao-cao/pipeline-finetune.md (lưu nội bộ) |
| 22 | 10/3/2026 | Chuẩn bị trình bày — nhật ký AI tuần 3 và bộ slide sơ đồ lớp cho giảng viên hướng dẫn | <https://claude.ai/artifact/LSpMy9C45E9XKjLEiFgJkx> |
| 23 | 10/4/2026 | Quản lý dự án — đọc email bộ môn và Rubric V2-1, soạn báo cáo tiến độ nộp bù W1–W3 | Tệp _bao-cao/bao-cao-tien-do-W1-W3-Sang.md (lưu nội bộ); Rubric V2-1: <https://docs.google.com/document/d/1pm4i8QKyQGpcG0xYNuwMi21oZoUkc2Jk> |
| 24 | 10/4/2026 | AI log — bổ sung tab Sang(Week 1) và đưa AI log W1–W3 vào evidence của repo | <https://github.com/thanglb2005/ai-assessor-cefr/pull/29> (commit 4a15e19) |


## Lỗi của AI đã tự phát hiện và sửa (TC2.3)

| # | Tuần | Lỗi do AI tạo ra | Ai phát hiện, bằng cách nào | Nguyên nhân | Commit / PR sửa |
| ---: | --- | --- | --- | --- | --- |
| 1 | W1 | Vẽ "hệ thống" như một tác nhân trong sơ đồ use case; quan hệ extend sai chiều; use case mở rộng nối thẳng tác nhân | Sang đọc lại sơ đồ đối chiếu ký hiệu UML use case | AI nhầm ký hiệu: hệ thống là ranh giới, không phải actor; extend đi từ use case mở rộng tới use case gốc | `Nguyneee/ai-assessor-cefr` b5f9e66, c21f3bc, d9642eb |
| 2 | W1 | Ghi bội số `[0..1]` ngay trong thuộc tính entity; dùng `Map<str, float>` làm kiểu trên sơ đồ lớp | Sang chất vấn "có đúng bản chất OOP không" | AI chép cách viết kiểu Python sang ký hiệu UML | `Nguyneee/ai-assessor-cefr` PR #27, #30 |
| 3 | W2 | Cấu hình test khiến lệnh `pytest` chạy trơn lỗi thu thập test, chỉ `python -m pytest` chạy được | Review Phase 07, chạy lại đúng lệnh mà thành viên khác sẽ dùng | AI chỉ kiểm bằng một cách chạy | `thanglb2005/ai-assessor-cefr` PR #9 (FINDING-07-A1-01) |
| 4 | W3 | Sau khi app đọc biến `AICEFR_DB`, test có thể ghi vào CSDL thật khi máy có đặt biến này | Tự review sau khi sửa lỗi giao diện | Thay đổi của AI không cách ly môi trường test | `ThanhSangLouis/ai-assessor-cefr` 1975211 |
| 5 | W3 | Lần dựng lại mô hình đầu tiên để hiệu chỉnh khoảng tin cậy cho dự đoán lệch so với mô hình đang chạy | Script tự kiểm "dựng lại phải khớp artifact" báo lệch và dừng | AI học thẳng trên 18 đặc trưng, trong khi mô hình gốc học 19 rồi mới bỏ một đặc trưng | `ThanhSangLouis/ai-assessor-cefr` 3a66f14 |
| 6 | W3 | Test ghi mật khẩu thử thẳng vào JSON, làm job quét lộ khoá (gitleaks) báo đỏ | CI báo đỏ; chạy gitleaks trên máy để tìm đúng 2 vị trí | AI không theo quy ước hằng `PASSWORD` của các test cũ | `ThanhSangLouis/ai-assessor-cefr` e09a725, 18b1896 |
| 7 | W3 | Mô tả PR nhắc mã ticket của người khác, làm automation Jira tự chuyển ticket SCRUM-45 của Thắng sang In Review | Kiểm lịch sử thay đổi của ticket trên Jira | AI không tính tới rule automation đọc mã ticket trong mô tả PR | Sửa mô tả PR #26, trả ticket về To Do, comment giải thích |

## Quy trình kiểm soát đầu ra AI đang áp dụng

1. **Thiết kế trước, code sau** theo SDD. Mỗi phase có verdict do Sang duyệt; AI chỉ đề xuất.
2. **Trước khi push, chạy đúng các bước của CI trên máy:** định dạng, lint, test kèm độ phủ, gitleaks. Không để CI là nơi phát hiện lỗi đầu tiên.
3. **Test mới phải đỏ khi bỏ thay đổi:** kiểm để chắc test thật sự bắt được lỗi, ví dụ PR #26.
4. **Review Phase 07 ghi rõ người review là Claude, cũng là tác nhân đã implement.** Verdict do Sang quyết; cần thêm một thành viên khác approve trên GitHub.
5. **Dữ liệu và giấy phép:**
   - Không đưa audio, transcript, model hay số liệu suy ra từ S&I vào repo public.
   - Prompt không chứa dữ liệu cá nhân.
6. **AI log đối chiếu với Git:** mỗi dòng log có PR hoặc commit; tác giả commit chỉ ghi Sang.
