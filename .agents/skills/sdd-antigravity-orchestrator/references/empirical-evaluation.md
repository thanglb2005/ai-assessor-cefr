# Đánh giá thực nghiệm và cải tiến Skill

Đọc reference này chỉ khi tạo/sửa/audit chính `sdd-antigravity-orchestrator` và cần đánh giá hành vi bằng nhiều lượt chạy. Mục tiêu là chứng minh Skill tạo kết quả tốt hơn baseline mà không tối ưu quá mức cho vài prompt mẫu.

## 1. Khi nào cần chạy

Chạy eval thực nghiệm khi:

- Thay đổi description hoặc trigger routing.
- Thêm/bớt mode, phase/checkpoint hoặc invariant quan trọng.
- Một lỗi hành vi đã lặp lại và cần regression test.
- Người dùng yêu cầu benchmark, so sánh phiên bản hoặc đánh giá độ ổn định.

Thay đổi tài liệu nhỏ có thể chỉ cần structural validation và targeted forward-test. Không tự chạy nhiều model/subagent, tiêu tốn quota hoặc mở UI bên ngoài nếu người dùng chưa yêu cầu và môi trường chưa cho phép. Khi independent runs không khả dụng, validate bộ eval, thực hiện sanity check nội tuyến và ghi `EMPIRICAL BENCHMARK: PENDING`; không giả lập số liệu.

## 2. Nguồn test chuẩn

- `evals/evals.json`: prompt hành vi end-to-end cùng expectations có thể chấm bằng evidence.
- `evals/trigger-evals.json`: prompt nên/không nên kích hoạt, gồm near-miss thực tế.
- `references/skill-evaluation.md`: bộ case chi tiết và invariant dùng để giải thích expectation.
- `scripts/aggregate_eval_results.py`: tổng hợp grading/timing current–baseline thành benchmark JSON và Markdown.

Trước mọi lượt chạy:

```text
python3 <skill-root>/scripts/validate_evals.py --skill-root <skill-root>
```

Không sửa expectation sau khi nhìn thấy output chỉ để làm phiên bản mới pass. Khi requirement thực sự thay đổi, ghi lý do và coi đó là một eval-set version mới.

## 3. Baseline và workspace

Đặt kết quả ngoài thư mục Skill để không làm bẩn package:

```text
<skill-name>-workspace/
├── skill-baseline/                 # snapshot bất biến trước khi sửa
└── iteration-<N>/
    ├── eval-<ID>/
    │   ├── current/outputs/
    │   ├── baseline/outputs/
    │   ├── grading-current.json
    │   ├── grading-baseline.json
    │   └── timing.json
    ├── benchmark.json
    └── evaluation-report.md
```

Với Skill có sẵn, baseline mặc định là snapshot trước thay đổi; không so với “không có Skill” nếu mục tiêu là chứng minh bản nâng cấp tốt hơn bản cũ. Với Skill mới, baseline có thể là cùng prompt nhưng không nạp Skill.

Current và baseline phải dùng cùng model, tool availability, quyền, fixture và prompt. Không để một bên có thêm context hoặc quyền external action.

## 4. Vòng eval hành vi

1. Chọn 3–7 case đại diện từ `evals/evals.json`; gồm happy path, edge/risk path và ít nhất một case dễ nhầm mode.
2. Nếu independent agent/delegation được phép, chạy current và baseline độc lập, cùng lượt khi có thể. Nếu không được phép, không tự mở rộng quyền; ghi giới hạn.
3. Lưu final output, artifact, transcript tóm tắt, tool errors, duration và token nếu hệ thống cung cấp.
4. Chấm từng expectation bằng `PASS | FAIL | NOT_VERIFIABLE` và trích evidence cụ thể. Không chấm theo việc output có chứa đúng từ khóa.
5. Những tiêu chí chủ quan như độ dễ hiểu hoặc prompt ergonomics cần người dùng review; không ép thành assertion giả khách quan.
6. Phân tích transcript để phát hiện bước lặp, reference bị đọc thừa, tool call vô ích hoặc instruction gây hiểu sai.

Mẫu grading tối thiểu:

```json
{
  "eval_set_version": "2026-09-07.1",
  "expectations": [
    {
      "id": "eval-1-phase05-approval",
      "text": "Task không được phát hành trước Phase 05 APPROVED",
      "passed": true,
      "evidence": "Output dừng ở Definition of Ready và nêu decision còn thiếu"
    }
  ],
  "summary": {"passed": 1, "failed": 0, "not_verifiable": 0},
  "limits": []
}
```

Mỗi expectation có `id` ổn định, gán một lần khi chốt eval set và dùng chung cho current/baseline. Mọi grading file trong iteration phải ghi cùng `eval_set_version`; mỗi cặp cùng case phải có cùng tập ID và cùng nội dung tiêu chí, không phụ thuộc thứ tự. `passed` bắt buộc là `true`, `false` hoặc `null` (`NOT_VERIFIABLE`); không bỏ field để thay cho chưa xác minh. Script từ chối dữ liệu thiếu/lệch contract trước khi tính delta. Grading cũ thiếu metadata phải được đối chiếu với eval set/evidence gốc rồi bổ sung hoặc chấm lại, không đoán version/ID để ép hợp lệ.

Mỗi thư mục eval có thể ghi timing theo schema sau; để `null` khi runner không cung cấp thay vì tự ước lượng:

```json
{
  "current": {"duration_ms": 1200, "total_tokens": 3400},
  "baseline": {"duration_ms": 1500, "total_tokens": 3900}
}
```

## 5. Benchmark và phân tích

Khi người dùng cần số liệu đáng tin hơn, chạy mỗi configuration tối thiểu ba lần nếu quota/thời gian cho phép. Báo cáo:

```text
Configuration | Pass rate mean ± stddev | Time mean ± stddev | Tokens mean ± stddev | Errors
Current
Baseline
Delta
```

Sau khi có `grading-current.json`, `grading-baseline.json` và timing tùy chọn trong từng thư mục `eval-*`, chạy:

```text
python3 <skill-root>/scripts/aggregate_eval_results.py <iteration-directory>
```

Script tạo `benchmark.json` (schema version 2, kèm eval-set version và expectation contract) và `benchmark.md`, tính pass rate tổng, mean/stddev theo case, timing/token mean/stddev và delta current–baseline. Đây là phép tổng hợp deterministic; độ tin cậy vẫn phụ thuộc grading evidence và tính độc lập của các run.

Không chọn phiên bản chỉ vì pass rate cao hơn. Phân tích thêm:

- Expectation nào cả current và baseline đều pass: có thể không phân biệt giá trị Skill.
- Case nào dao động lớn: có thể flaky, fixture yếu hoặc prompt mơ hồ.
- Pass rate tăng nhưng token/thời gian tăng mạnh: nêu trade-off.
- Current thắng chỉ trên case đã dùng để sửa: có nguy cơ overfit.
- Instruction nào không ảnh hưởng hành vi: cân nhắc bỏ để Skill gọn hơn.

Chỉ kết luận phiên bản mới tốt hơn khi không làm regression invariant quan trọng và cải thiện có evidence trên nhiều case.

## 6. Eval trigger và description

Dùng `evals/trigger-evals.json` để kiểm tra description ở frontmatter:

1. Giữ tập cân bằng giữa `should_trigger: true` và `false`.
2. Negative case ưu tiên near-miss có chung từ như SDD, review, UI, Chrome hoặc code nhưng không cần workflow này.
3. Có cách nói chính thức, đời thường, viết tắt và typo giống người dùng thật.
4. Tách một phần case làm held-out; không chỉnh description trực tiếp theo toàn bộ tập test.
5. Nếu có khả năng chạy lặp, mỗi query chạy nhiều lần để đo trigger rate thay vì tin một lần.
6. Chỉ cập nhật description khi failure có pattern; không thêm mọi keyword nhìn thấy vào frontmatter.

Mục tiêu là kích hoạt đúng hai mode phức tạp mà không hút các tác vụ review/code đơn giản. Sau khi sửa description, chạy lại toàn bộ negative near-miss.

## 7. Cải tiến từ kết quả

Ưu tiên sửa hẹp theo nguyên nhân:

- Trigger sai → sửa description hoặc routing, không nhồi workflow vào frontmatter.
- Bỏ phase/checkpoint/invariant → làm rõ lý do và điểm quyết định trong reference liên quan.
- Nhiều case tự tạo cùng helper → cân nhắc đóng gói script deterministic.
- Model đọc quá nhiều context → cải thiện progressive disclosure/routing.
- Assertion không phân biệt current/baseline → sửa eval, không sửa Skill để chiều assertion.

Giải thích `why` cho invariant quan trọng thay vì tích lũy `ALWAYS/NEVER` thiếu ngữ cảnh. Mọi thay đổi phải khái quát được ngoài prompt đã test.

## 8. Điều kiện dừng và báo cáo

Dừng iteration khi một trong các điều kiện xảy ra:

- Người dùng chấp nhận kết quả.
- Toàn bộ invariant bắt buộc đạt và feedback không còn issue cụ thể.
- Hai vòng liên tiếp không tạo cải thiện có ý nghĩa.
- Cần thêm quyền, quota, fixture hoặc quyết định của người dùng.

`evaluation-report.md` tối thiểu ghi:

```text
Skill/baseline revision:
Model/environment/tool access:
Eval-set version và case đã chạy:
Pass/fail/not-verifiable:
Timing/token/error nếu có:
Regression/variance/near-miss:
User feedback:
Thay đổi được evidence hỗ trợ:
Giới hạn và bước tiếp theo:
```

Không tuyên bố “đã benchmark” khi mới chỉ validate JSON hoặc tự đọc Skill. Structural validation, forward-test và empirical benchmark là ba mức evidence khác nhau.

## 9. Cơ sở tham khảo

- [Anthropic skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md): draft → eval → human/quantitative review → iterate; so sánh current với baseline và tối ưu trigger bằng near-miss.
- [Claude custom skills documentation](https://claude.com/docs/skills/how-to): cấu trúc Skill, progressive disclosure, scripts/references và yêu cầu test trước khi tin cậy.

Workflow này chỉ tiếp thu nguyên tắc đánh giá; không phụ thuộc Claude CLI, viewer hoặc schema nội bộ của một nền tảng cụ thể.
