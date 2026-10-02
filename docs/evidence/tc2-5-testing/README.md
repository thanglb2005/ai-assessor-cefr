# TC2.5 — Kiểm thử phần mềm

**Nguồn tiêu chí:** rubric PDF tại docs/rubric/. Trạng thái của folder: PARTIAL — có test/source/evidence local, user verdict PENDING.

## Hồ sơ cần có

Test plan, test case, test code, kết quả chạy, coverage, defect log và trạng thái sửa.

## Minh chứng hiện có

| Evidence | Phạm vi | Trạng thái |
| --- | --- | --- |
| [W3 Test Plan](../../sdd/features/w3-local-integration/04-test-plan.md) | W3-TEST-001–008 map W3-AC-001–005 | Tests phải đối chiếu final source |
| [W3 Review](../../sdd/features/w3-local-integration/reviews/review-01.md) | Defect findings/corrections và test quality | Codex actual diff review |
| [W3 Evidence Manifest](../../sdd/features/w3-local-integration/evidence/evidence-manifest.md) | Regression/coverage/browser/persistence output | Số liệu dùng đúng revision trong từng report |
| [Real ASR/VAD smoke](../../sdd/features/w3-local-integration/evidence/real-speech-smoke.md) | Hai audio local, actual engine/features | WAV PASS; MP3 codec warnings được ghi; WER/accuracy NOT_MEASURED |

## Còn thiếu / cần xác minh

Chưa có ground truth WER, validation/calibration CEFR trên người học hay benchmark đa môi trường. Browser fixture journey chỉ chứng minh chức năng, không là user study. Các tests cần model path/codec có thể skip trên môi trường thiếu prerequisite; final report nêu số skip và lý do, không dùng mocks thay smoke thật.

Khi có evidence mới, thêm dòng gồm: Evidence ID, nguồn/path hoặc URL, ngày, owner, Prompt/Task/AC nếu áp dụng, revision/checksum và trạng thái xác minh. Chỉ ghi số liệu và trạng thái PASS khi có phép đo cùng evidence tương ứng.
