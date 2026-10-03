# M05 — 05 Plan & Task Readiness (Kế hoạch)

> **v0.2 · 26/09/2026 · APPROVED Phase 05 ngày 26/09/2026.** Dựa trên [Requirement v0.2](01-requirement.md), [Research v0.2](02-research.md), [Specification v0.2](03-specification.md), [Test Plan v0.2](04-test-plan.md) — cả bốn APPROVED. Chưa phát prompt Antigravity.

**Owner:** Sang. **Vùng file của M05:** `src/aicefr/scoring/`, `tests/scoring/`. File dùng chung thuộc Thắng — M05 chỉ yêu cầu.

## Kiến trúc

```text
ModelConfig (tên, SHA-256 ghim, đường dẫn) ──► load_artifact()      bước 1–2
FeatureSet (M04) + Transcript.status (M03) ──► RidgeScorer.score()
                                                ├─ bước 3  transcript OK
                                                ├─ bước 4  provenance (==)
                                                ├─ bước 5  không null
                                                ├─ bước 6  OOD
                                                ├─ bước 7  z → raw → clip → band
                                                ├─ bước 8  near-boundary
                                                └─ coverage 5 tiêu chí + Interaction null
                                             ──► Assessment (M06, M07)
```

| Thành phần | File dự kiến | Ghi chú |
| --- | --- | --- |
| Loader artifact | `scoring/artifact.py` | Chỉ JSON; kiểm SHA-256 và `unit_of_inference`; trả `feature_order`, `feature_version`, `trained_with` cho M03/M04 |
| Toán chấm | `scoring/ridge.py` | `predict`, `ood_detail`, `to_band`, `near_boundary` — hàm thuần |
| Coverage | `scoring/coverage.py` | Bảng tiêu chí → đặc trưng, chỉ tên có trong `feature_order` |
| Scorer | `scoring/scorer.py` | Thứ tự 8 bước, dừng ở bước lỗi đầu tiên, dựng Assessment |

## Thứ tự triển khai

1. **M05-TASK-002** loader + toán chấm — M03-TASK-004 và M04-TASK-002 cần loader này.
2. **M05-TASK-001** scorer + coverage (đường từ chối đầy đủ).
3. **M05-TASK-004** integration M04 → M05 — sau M04-TASK-002.

**M05-TASK-003** (bản v0.1: đánh giá metric có điều kiện) **rút lại**: Test Plan v0.2 đã loại metric chất lượng model khỏi W2 (M05-TEST-005 cũ không còn). Giữ ID để không tái dùng.

## Quyết định cần user — P05-D-001: nơi đặt `ridge_resp_v2.json`

Fact: `.gitignore` của repo có dòng `models/`, nên đường dẫn kiểu `src/aicefr/scoring/models/` **bị Git bỏ qua**. AGENTS.md cấm commit "model weights không có quyền phân phối"; artifact là hệ số học từ corpus S&I (không được phân phối lại dữ liệu), còn quyền phân phối **hệ số** chưa được ghi ở đâu.

| Option | Cách làm | Hệ quả |
| --- | --- | --- |
| A. Commit vào repo (thư mục không tên `models/`) | Test vàng chạy mọi nơi, kể cả CI | Cần xác nhận quyền phân phối hệ số và cả nhóm đồng ý ngoại lệ với AGENTS.md |
| B. Giữ ngoài repo | Đường dẫn qua biến môi trường `AICEFR_MODEL_DIR`; SHA-256 ghim trong code; test cần artifact thật tự `skip` khi thiếu | Không đụng quy tắc nhóm; test vàng (M05-TEST-001, 003, 015, 022…) chỉ chạy trên máy có artifact và phải báo `SKIPPED`, không được tính là PASS trên CI |

**Đã chốt 26/09/2026 (user): Option B** — artifact giữ ngoài repo, đường dẫn qua `AICEFR_MODEL_DIR`, SHA-256 ghim trong code. Evidence Phase 06/08 cho các test vàng lấy từ máy Sang (có artifact, hash khớp); trên máy không có artifact, các test này báo `SKIPPED`.

## Dependency và trạng thái sẵn sàng (26/09/2026)

| ID | Cần gì | Của ai | Trạng thái | Chặn task |
| --- | --- | --- | --- | --- |
| DEP-01 | Skeleton `pyproject.toml`/`tests/`, `pytest-cov` | Thắng (Sang làm thay) | **Đã có** trên `main` a92fafe (PR #6, 26/09/2026) | — |
| DEP-02 | Contract chung có `Assessment`, `CriterionCoverage`, `Interaction`, `AssessmentStatus` theo M05 Spec; reason code hiện có + **mới** `FEATURE_VERSION_MISMATCH`, `MODEL_ARTIFACT_INVALID` | Thắng (Sang làm thay) | **Đã có** — `src/aicefr/contracts.py` | — |
| DEP-03 | P05-D-001 được chốt | Sang | **Đã chốt** — Option B, 26/09/2026 | — |
| DEP-04 | FeatureSet thật từ extractor | Sang (M04-TASK-002) | **Đã có** — M04-TASK-002 nghiệm thu 27/09/2026 | TASK-004 |

## Required checks mỗi task

- Test ID của task, rồi `python3 -m pytest -q -m "not smoke" tests/scoring`.
- Coverage **TP-D-001**: `--cov=aicefr.scoring --cov-branch`; line ≥ 90 %, branch ≥ 85 % (M05 không có adapter nặng nên không loại trừ gì).
- Giá trị vàng khớp Test Plan với sai số 1e-4; báo rõ số test `SKIPPED` vì thiếu artifact.
- `ruff`/typecheck nếu được cấu hình; diff chỉ trong vùng M05; không commit artifact nếu chọn Option B.

## Clean Code

Mọi con số (mean, scale, coef, intercept, ngưỡng band, margin, `ood_tolerance`) đọc từ artifact, không có bản sao trong code; thứ tự 8 bước viết thành chuỗi kiểm rõ ràng, mỗi bước một hàm; không pickle.

## Rủi ro, rollback, phục hồi

| Rủi ro | Xử lý |
| --- | --- |
| Artifact bị thay mà hash không đổi trong config | Hash ghim trong code/config có review; TEST-006 bắt file bị sửa |
| Test vàng bị skip trên CI mà trông như xanh (Option B) | Evidence phải liệt kê số test skip; Phase 08 chạy trên máy có artifact |
| Contract chung đổi | Chỉ dùng type từ contract; đổi contract → artifact phía sau stale theo SDD |
| Rollback | Một commit mỗi task; revert |

## Evidence và quyền

Prompt `prompts/`, raw report/coverage `evidence/`, review `reviews/`; Shared workspace, fingerprint `sdd-workspace-v2`. Antigravity không sao chép artifact vào repo, không gọi mạng, không sửa ngoài vùng M05.

## Definition of Ready

| Check | Kết quả |
| --- | --- |
| 1–2. Trace; boundary/data flow/lỗi | PASS |
| 3. Runtime/convention | PASS — `pyproject.toml` và CI đã có trên `main` |
| 4–6, 8–9 | PASS |
| 7. Dependency sẵn sàng | PASS — TASK-002 và 001 không còn dependency ngoài; TASK-004 làm sau M04-TASK-002 (DEP-04) |

**CODEX CHECK RESULT:** PASS (kiểm lại 26/09/2026 sau khi DEP-01/02 có trên `main`). **CODEX RECOMMENDATION:** RECOMMEND APPROVAL Phase 05. **User verdict Phase 05:** APPROVED 26/09/2026 (Sang).

**Cập nhật dependency 03/10/2026:** DEP-04 đã có; M05-TASK-004 đã implement, xem [M05-EV-003](evidence/evidence-manifest.md).

## Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi |
| --- | --- | --- |
| v0.1 | 25/09/2026 | Bản nháp đầu |
| v0.2 | 26/09/2026 | Theo Spec/Test Plan v0.2: 4 thành phần, task 001/002/004, rút TASK-003; P05-D-001 chốt Option B; DoR |
