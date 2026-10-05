# TC2.6 — CI/CD và vận hành

**Nguồn tiêu chí:** rubric PDF tại docs/rubric/. Trạng thái của folder: PARTIAL — có workflow và local run guide; remote run/deploy chưa xác minh.

## Hồ sơ cần có

Cấu hình pipeline, lịch sử run/deploy, build artifact, hướng dẫn vận hành và link môi trường nếu có.

## Minh chứng hiện có

| Artifact | Phạm vi | Trạng thái |
| --- | --- | --- |
| [CI workflow](../../../.github/workflows/ci.yml) | Install một lần; pytest/branch coverage, Ruff và Markdown/forbidden guards | Source review trong W3; remote run NOT_RUN cho branch này |
| [Local run guide](../../local-run.md) | Setup/CLI, external data/model, loopback, restart/shutdown | W3 local demonstration |
| [W3 Evidence](../../sdd/features/w3-local-integration/evidence/evidence-manifest.md) | Actual local tests/build/browser/smoke gắn revision | Local verification, không suy ra deploy thành công |

## Còn thiếu / cần xác minh

Branch W3 chưa push, không có GitHub Actions run/deployment URL từ lượt này. Workflow mặc định không tải Whisper/Ridge hay gửi audio. Production hosting/TLS, retention/export/delete và policy dữ liệu thật chưa được nghiệm thu; local server chỉ một process trên loopback.

Khi có evidence mới, thêm dòng gồm: Evidence ID, nguồn/path hoặc URL, ngày, owner, Prompt/Task/AC nếu áp dụng, revision/checksum và trạng thái xác minh. Chỉ ghi số liệu và trạng thái PASS khi có phép đo cùng evidence tương ứng.
