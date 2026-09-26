# M05 — 06 Tasks

> **v0.2 · 26/09/2026 · chờ Phase 05 verdict.** Theo [Plan v0.2](05-plan.md). Chưa phát prompt. Owner mọi task: **Sang**.

| Task ID | FR / AC | Test ID | Vùng file | Mục tiêu quan sát được | Dependency | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| M05-TASK-001 | FR-001..003 / AC-001..003 | 001–004, 008–014, 020, 021 | `scoring/scorer.py`, `scoring/coverage.py`, `tests/scoring/test_scorer.py`, `tests/scoring/test_coverage.py` | Thứ tự 8 bước; 3 status; provenance lệch → `NOT_EVALUATED`; 5 dòng coverage không có score, fluency = 1,0 khi đủ; Interaction null; tất định; log không có vector | TASK-002 | ĐỀ XUẤT READY (sau TASK-002) |
| M05-TASK-002 | FR-001, FR-002 / AC-001, AC-002 | 005, 006, 007, 015–019 | `scoring/artifact.py`, `scoring/ridge.py`, `tests/scoring/test_artifact.py`, `tests/scoring/test_ridge.py` | Loader kiểm hash và `unit_of_inference`; OOD kèm chi tiết; band/near-boundary/clip đúng tại biên; `scale=0` không chia 0 | — | ĐỀ XUẤT READY |
| M05-TASK-003 | — | — | — | **Rút lại** (v0.2): metric chất lượng model ngoài phạm vi W2 | — | WITHDRAWN |
| M05-TASK-004 | FR-001 / AC-002 | 022 | `tests/scoring/test_integration_features.py` | FeatureSet từ extractor M04 đi qua scorer; ra `NOT_EVALUATED` + `OUT_OF_DISTRIBUTION` chỉ vì `log_uniq` | DEP-04 (M04-TASK-002), TASK-001 | ĐỀ XUẤT READY (sau M04-TASK-002, TASK-001) |

**Ngoài scope mọi task:** sửa file dùng chung, code M03/M04, chép artifact vào repo (P05-D-001 = Option B), huấn luyện lại hay đổi hệ số.

## Handoff và hoàn tất

Như [M03 Tasks](../m03-asr/06-tasks.md#handoff-và-hoàn-tất).

**Trạng thái (26/09/2026):** 3 task đề xuất READY theo thứ tự TASK-002 → 001 → 004. **Phase 05 verdict:** PENDING.
