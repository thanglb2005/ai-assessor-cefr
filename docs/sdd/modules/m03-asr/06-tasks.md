# M03 — 06 Tasks

> **v0.2 · 26/09/2026 · chờ Phase 05 verdict.** Theo [Plan v0.2](05-plan.md). Chưa phát prompt. Owner mọi task: **Sang**.

| Task ID | FR / AC | Test ID | Vùng file | Mục tiêu quan sát được | Dependency | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| M03-TASK-001 | FR-001, FR-002 / AC-001, AC-002 | 001–007, 016 | `asr/service.py`, `asr/validation.py`, `tests/asr/test_service.py`, `tests/asr/test_validation.py` | `AsrService` trả Transcript đúng status/reason cho QC gate, lỗi engine, timestamp sai, `prob=None`, transcript rỗng, model thiếu; log không chứa transcript | DEP-01, DEP-02, TASK-003, TASK-004 | BLOCKED |
| M03-TASK-002 | FR-001 / AC-002 | S1, S2 | `asr/faster_whisper_engine.py`, `tests/smoke/test_asr_smoke.py` | Adapter faster-whisper `small` chạy offline; evidence smoke đủ trường S1; ghi `asr_conf_mean` (S2) | DEP-01..06, TASK-001 | BLOCKED |
| M03-TASK-003 | FR-002 / AC-001 | 008–012 | `asr/hallucination.py`, `tests/asr/test_hallucination.py` | 5 luật cho đúng kết quả tại và quanh ngưỡng; ngưỡng gom trong config `hallucination-v1` | DEP-01, DEP-02 | BLOCKED |
| M03-TASK-004 | FR-003 / AC-003 | 013–015 | `asr/identity.py`, `tests/asr/test_identity.py` | Ánh xạ weight → identifier chuẩn; so `==`; `whisper-small.en` và weight lạ → `ASR_VERSION_MISMATCH` | DEP-01, DEP-02 | BLOCKED |

**Ngoài scope mọi task:** sửa `pyproject.toml`, contract/reason code chung, pipeline, code của M02/M04/M05; tải model; dữ liệu người học.

**Thao tác của owner (không giao Antigravity):** DEP-05 tải weight `whisper-small` (CTranslate2) có chủ đích và ghi nguồn, license, SHA-256 vào `evidence/`; DEP-06 chuẩn bị audio có quyền dùng ngoài repo.

## Handoff và hoàn tất

- Mỗi task một prompt trong `prompts/` (mẫu `antigravity-handoff.md` §3), có base revision và fingerprint `sdd-workspace-v2`.
- Task chỉ xong khi có actual diff, lệnh test/coverage chạy thật, Phase 07 review, Phase 08 trên revision cuối và user verdict.

**Trạng thái:** 4 task `BLOCKED` chờ DEP-01/DEP-02 (Thắng). **Phase 05 verdict:** PENDING.
