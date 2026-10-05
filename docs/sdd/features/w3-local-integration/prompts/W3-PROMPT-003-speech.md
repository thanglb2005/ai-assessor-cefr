# W3-PROMPT-003 — speech

PROMPT ID: W3-PROMPT-003
TASK IDS: W3-TASK-005, W3-TASK-006
SCOPE ID/TYPE/ROOT: W3 / feature / docs/sdd/features/w3-local-integration/
ATTEMPT: 1
HANDOFF MODE: isolated local Git worktree
REPO ROOT: /tmp/aicefr-w3-speech
BRANCH: feat/W3-speech
BASE REVISION: 7bb327b655c67d8eb5aafc4cd8ec9481fabdff28
BASE SOURCE REVISION: 2b428ceea9e4459f3235d4ce67f10bab31585ebf
WORKSPACE FINGERPRINT: 077da2ddbf9d18bdd92d48ed0d434619ee942398cbc3656b7400662205490881
FINGERPRINT ALGORITHM: sdd-workspace-v2
FINGERPRINT METADATA FILES: docs/sdd/features/w3-local-integration/prompts/W3-PROMPT-003-speech.md
FINGERPRINT EXCLUSIONS: KHÔNG CÓ
ARTIFACT VERSIONS: W3 v0.1
AUTHORIZATION: direct user instruction in 01-requirement, implementation/delegation allowed; final user verdict PENDING

## Authorization và vai trò
Thắng trực tiếp yêu cầu dùng subagents Luna triển khai hết W3, Codex review, lưu prompt/AI log và tạo nhánh riêng (02/10/2026). Chỉ dẫn mới nhất này thay executor Antigravity và giới hạn subagents read-only trong skill. Bạn là implementation agent gpt-6-luna; không tự approve phase/nghiệm thu. Không cần hỏi lại quyền implement. Mọi formal USER VERDICT giữ PENDING.

## Context phải đọc
AGENTS.md; AI_CONTEXT.md; docs/sdd/features/w3-local-integration/01-requirement.md, 02-research.md, 03-specification.md, 04-test-plan.md, 05-plan.md, 06-tasks.md, 07-status.md; các source/SDD trực tiếp liên quan. W2 specification/rubric/model mapping giữ nguyên. Bỏ qua context cấp repo đã cũ khi có record scope/revision mới hơn.

## Quy tắc worktree và báo cáo
Chỉ làm trong REPO ROOT chỉ định. Root integration branch và worktrees khác thuộc agents khác. Không git switch/reset/rebase/cherry-pick/push, không sửa AI workbook/Status/SDD của root. Local commit được user authorize; git add đúng allowed files + prompt của mình + raw report của mình. Không git add -A. Cài thêm dependency hoặc đổi shared contracts phải báo root trước. Không cần tạo subagents con.

Trước sửa: git status, git rev-parse HEAD, verify fingerprint bằng helper với đúng metadata files. Dùng PYTHONPATH=src /tmp/aicefr-w3-venv/bin/python -m pytest ... trong worktree để tránh import editable root. Ruff /tmp/aicefr-w3-venv/bin/ruff. Env đã có existing .[dev], openpyxl và Playwright; optional ASR/VAD chưa cài. Report/coverage output ở /tmp theo lane.

UT REQUIRED: YES. Viết tests với code; assertion trên hành vi và rollback/privacy, không network/real data/model download. Đo line/branch changed packages và nêu uncovered critical paths; không hạ threshold/exclusion/skips để ép PASS. Không ghi stacktrace có nội dung input/secret/transcript. Không dùng test_only transcript/fixture score cho default runtime hoặc claim CEFR accuracy.

Raw report tiếng Việt, có Prompt/Task ID, starting fingerprint/base, commit/source tree fingerprint, file list, commands+exit+PASS/FAIL/SKIP, coverage/tool/report path, source citations khi dùng, assumption/limitation. Commit source/tests trước, sau đó viết raw report dẫn code commit và commit evidence. Return code/evidence commit SHA và blockers thật. Root sẽ review actual diff/rerun; COMPLETED không là user acceptance.

## Mục tiêu
Offline local ASR/VAD adapters, W3 scoring/ASR/VAD edge cases và CI checks; giữ rubric/model provenance, privacy và actual measurement.

## Allowed files
src/aicefr/asr/local.py (mới), src/aicefr/features/local.py (mới); src/aicefr/asr/service.py và src/aicefr/features/extractor.py (safe logging/errors only); src/aicefr/scoring/artifact.py, scorer.py, ridge.py (finite/shape/provenance/refusal robustness, no đổi rubric/hash/band semantics); tests/asr/test_local.py, tests/features/test_local.py, tests/scoring/test_w3_validation.py; .github/workflows/ci.yml; scripts/ci/**; tests/ci/**; evidence/raw-speech.md và evidence/model-provenance.md của scope W3. Không sửa pyproject/shared contracts/runtime/pipeline/report/auth/API hoặc tests của lane khác.

## Contract
FasterWhisperEngine(model_dir,*,weight_name='small',device='cpu',compute_type='int8') implements AsrEngine. Lazy import faster_whisper; path existing local model only, local_files_only=True; CPU deterministic flags khi phù hợp, English language, word timestamps. Convert engine output RawWord safely; engine metadata package version + canonical weight_name; test_only=False only actual engine. Missing path/dependency→ModelUnavailableError; no automatic download. Do not trust arbitrary weight_name provenance mismatch as compatible.
SileroVadEngine(*,threshold=0.5,min_silence_ms=150) implements VadEngine; name='silero', version actual installed package; lazy imports, bundled local model only no torch.hub network; output seconds using validated16k mono input. Missing dependency/model returns controlled unavailable handling, not silence/zero fallback.

## Primary-source verification
Browse only official faster-whisper/Silero documentation/repositories for APIs before implementation, cite source URLs in raw report/model provenance. Current optional dependencies already declared in pyproject; no new production deps. No weight/model/audio downloads. Source corpus artifact in internal repo matches pinned hash; inspect metadata but no copy into Git. Real ASR smoke stays NOT_RUN unless allowed audio and local weights actually exist; fixture mocks aren't real evidence.

## Edge cases/CI
Artifact invalid finite fields, zero/nonpositive scale, duplicated/empty feature order, malformed vectors, unordered/out-of-range band thresholds, nonfinite score must fail closed with controlled reason, not NaN/crash/fake metrics. Retain pinned hash/one-response inference and existing equations. Reject test_only transcript for real scorer if supported using existing safe reason (no change contracts), preserve tests semantics where intentional fixture-only logic documented.
AsrService/FeatureExtractor currently log.exception on engine errors: avoid stacktrace/exception string (could contain transcript/path/secrets); log only response ID/status/reason safely. Controlled errors do not invent transcript/feature fallback.
CI runs dependency install once without fallback masking failure; regression+branch coverage; lint/static and existing docs/forbidden-file guards; no heavy model/download default. Add smoke marker tests only if actual prerequisites are explicit and absent record NOT_RUN/SKIP; no overengineer. Keep CI source/privacy scans meaningful, do not falsely claim content secret scanning from only extension guard.

## Checks
W3-TEST-003,006,008 + affected existing tests. Unit mock external heavy boundary, no internet. Measure coverage local adapters/scoring changed paths; Ruff/diff check. In worktree PYTHONPATH=src; existing artifact can be read outside repo via AICEFR_MODEL_DIR for10 existing tests only; report commands and hash. Include honest error-analysis (failure scenarios/reasons, no user CEFR accuracy claim).
