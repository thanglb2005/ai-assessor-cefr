# M03 — ASR

| Metadata | Giá trị |
| --- | --- |
| SCOPE ID / TYPE | M03 / module |
| SCOPE ROOT | `docs/sdd/modules/m03-asr/` |
| OWNER | Sang (đề xuất W2–W3) |
| LIFECYCLE | proposed |
| PHASE 01 | DRAFT — chờ người dùng duyệt |
| RESEARCH MODE | Đề xuất `RUN`; người dùng quyết định trong Phase 01 |
| TARGET | W2 |
| RELATED SCOPES | M02 `PASS/REVIEW`, model local nếu được phép |
| SOURCE BASIS | [Tài liệu nguồn do nhóm tạo](../../../sources/README.md), [báo cáo W1](../../../reports/week-01/bao-cao-tuan-01.docx); quyết định W2 là bản mới, không kế thừa code/approval cũ |
| CODE TARGET | `src/aicefr/asr/` — đề xuất, chưa tạo |

## Requirement (Yêu cầu)

**Mục tiêu:** Chép lời bài nói có metadata và mức bất định đủ để các module sau sử dụng an toàn.

**Trong phạm vi:** `AsrEngine` test double chỉ cho kiểm thử và adapter local cho smoke; transcript, timestamp nếu có, model/config version; phát hiện lỗi và nghi ngờ ASR.

**Ngoài phạm vi W2–W3:** Tải model/người học lên cloud; xem bản fake là kết quả thật; cam kết word timestamp nếu engine không cung cấp.

| ID | Functional Requirement (Yêu cầu chức năng) |
| --- | --- |
| M03-FR-001 | Adapter ASR trả transcript có provenance; thiếu timestamp/confidence được biểu diễn rõ bằng status/null/reason. |
| M03-FR-002 | ASR lỗi hoặc nghi hallucination không được biến thành transcript hợp lệ hay score. |

## Acceptance Criteria (Tiêu chí chấp nhận)

| ID | Bằng chứng phải kiểm tra |
| --- | --- |
| M03-AC-001 | Test double cho output tất định và đánh dấu dữ liệu kiểm thử; failure fixture trả `ASR_FAILED`. |
| M03-AC-002 | Nếu chạy local thật, có smoke evidence về model/version và không có network mặc định; nếu chưa có evidence, trạng thái chỉ là pending. |

## W2 scope note (Ranh giới tuần 2)

W2 cần thử local ASR trên audio có quyền sử dụng và ghi model/version/môi trường; adapter tất định chỉ phục vụ unit/integration test, không thay kết quả ASR thật.

## Điều kiện chung và câu hỏi mở

- Unit test dùng fixture tạo bởi nhóm; smoke/integration chỉ dùng audio có quyền sử dụng. Fixture kiểm thử không là số liệu thực nghiệm; không log audio, transcript hoặc PII.
- ID, enum, schema/API xuyên module phải được cả owner liên quan review; mọi feature code chỉ bắt đầu sau khi Phase 01, 03, 04 và 05 của **module này** được người dùng duyệt theo thứ tự.
- Chủ dự án đã chọn 5 tiêu chí độc thoại làm bản nháp W2; rubric học thuật vẫn cần xác minh. Giữ field `Interaction=null` cùng lý do `insufficient_evidence` cho độc thoại. Dữ liệu/model và lịch 3 tuần xem [roadmap](../../../plan/three-week-roadmap.md).

