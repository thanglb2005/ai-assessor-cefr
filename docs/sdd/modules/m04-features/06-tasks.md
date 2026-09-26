# M04 — 06 Tasks

> **v0.2 · 26/09/2026 · chờ Phase 05 verdict.** Theo [Plan v0.2](05-plan.md). Chưa phát prompt. Owner mọi task: **Sang**.

| Task ID | FR / AC | Test ID | Vùng file | Mục tiêu quan sát được | Dependency | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| M04-TASK-001 | FR-001, FR-002 / AC-001, AC-002 | 001, 002, 003, 005, 006, 007, 008, 009 | `features/text.py`, `features/pauses.py`, `tests/features/test_text.py`, `tests/features/test_pauses.py` | 18 công thức khớp bảng kỳ vọng (1e-6); biên 0,30 s / 1,00 s / 10 token đúng; không có `0.0` giả | DEP-01, DEP-02 | BLOCKED |
| M04-TASK-002 | FR-001..004 / AC-001..004 | 004, 010–015, 017, 018 | `features/extractor.py`, `tests/features/test_extractor.py` | FeatureSet 18 tên đúng thứ tự artifact, không `filler_ratio`; bảng dữ liệu thiếu; `FEATURE_VERSION_MISMATCH`, `VAD_VERSION_MISMATCH`; không lộ transcript; tất định | DEP-01, DEP-02, DEP-05, TASK-001 | BLOCKED |
| M04-TASK-003 | FR-004 / AC-004 | 016, S1 | `features/silero_vad.py`, `tests/features/test_silero_vad.py`, `tests/smoke/test_vad_smoke.py` | Silero 0,5 / 150 ms / 16 kHz; lỗi nạp → null, không fallback; smoke offline có evidence | DEP-01..04, DEP-06, TASK-002 | BLOCKED |

**Ghi chú:** TEST-016 là unit (loader giả raise `ImportError`) nên phần unit của TASK-003 không cần Silero thật; chỉ S1 cần DEP-03/04/06.

**Ngoài scope mọi task:** sửa file dùng chung, code M02/M03/M05, thêm hay bớt đặc trưng ngoài `feature_order`.

## Handoff và hoàn tất

Như [M03 Tasks](../m03-asr/06-tasks.md#handoff-và-hoàn-tất).

**Trạng thái:** 3 task `BLOCKED` chờ DEP-01/DEP-02 (Thắng). **Phase 05 verdict:** PENDING.
