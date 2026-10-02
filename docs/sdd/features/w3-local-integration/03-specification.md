# W3 — Specification

Version v0.1 · 02/10/2026. Implementation authority: chỉ dẫn trực tiếp của Thắng trong 01-requirement; không ghi APPROVED thay user.

## Domain flow

1. Authenticated student + active consent + allowlisted task submit immutable raw blob.
2. PipelineCoordinator.enqueue(response) chạy đồng bộ cho local demo, chỉ xử lý QUEUED response. Đọc authorized stored bytes; nhận diện container từ bytes vì ResponseRecord không giữ filename; dùng whitelist/caps M02. Giữ raw bytes/checksum.
3. CAS transition QUEUED→RUNNING; QC REJECT→REJECTED không ASR/score; QC REVIEW→REVIEW_REQUIRED, report NOT_EVALUATED với QC reasons và candidate. PASS chạy injected AsrService→FeatureExtractor→RidgeScorer; không tạo transcript fallback.
4. M06 tạo report với source versions và evidence thật (nếu có); failure/refusal có null overall. Persist report trước khi báo COMPLETED. Assessment cần review tạo candidate ở final response revision (tránh stale ngay sau tạo).
5. SQLite report/review decision/audit dùng cùng connection và transaction; teacher decision callback rollback toàn bộ nếu report update lỗi. Report có teacher result riêng, không ghi đè overall AI.
6. Unexpected pipeline exception ghi controlled FAILED + reason, không stack trace/audio/credential trong log. Không retry duplicate enqueue tự động sau final trạng thái.

## Public integration contract giữa agents

- Pipeline lane: aicefr.pipeline.coordinator.PipelineCoordinator(*, responses, reports, reviews, qc_config, asr, extractor, scorer), implements enqueue(ResponseRecord)->None.
- Pipeline lane: aicefr.report.sqlite.SQLiteReportRepository(store), put(DiagnosticReport)->None, get(response_id)->DiagnosticReport|None; dùng store connection và transaction-aware semantics.
- Speech lane: aicefr.asr.local.FasterWhisperEngine(model_dir, *, weight_name='small', device='cpu', compute_type='int8'), implements AsrEngine; local path only, no download.
- Speech lane: aicefr.features.local.SileroVadEngine(*, threshold=0.5, min_silence_ms=150), name='silero'; implements VadEngine with measured package version and seconds output.
- App lane: aicefr.local factory/CLI assembles above existing services; python -m aicefr.local --help; explicit data_dir outside repository, loopback serving only, single process.
- App lane: injection override for unit/browser fixture testing only; default app never supplies a fake transcript, score or auto-consent. Missing models build controlled unavailable adapters and NOT_EVALUATED reports.

## HTTP/UI

Login/logout issue HttpOnly SameSite session cookie; unsafe cookie requests require same-origin check. Consent activation/withdrawal are authenticated student actions; no client role choice/signup. Browser upload redirects to student status/report, API submit retains JSON behavior. Teacher can view candidate's report and listen authorized audio, then claim/approve/override/reject; student cannot use teacher routes or access foreign response/blob. Error text is generic, bounded input and security headers remain. Fixture/demo limits visible in UI; sample configuration is explicitly demo-only. No real-data operational admin/export/delete policy.

## Error and recovery

Configuration/model paths validate before use; path traversal/symlink escapes fail closed. Model artifact hash/provenance not relaxed. Optional dependency missing never triggers network download. Reopening runtime restores accounts, sessions, consent, report, queue and final teacher result. Browser QA checks critical journeys at desktop/mobile without making up screenshots.

