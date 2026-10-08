"""Real local adapters on public short/long fixtures; never CEFR validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import time
from pathlib import Path

from aicefr.api.student import SubmitRequest
from aicefr.contracts import ActorRole, ReasonCode, ResponseStatus
from aicefr.local.app import create_runtime, load_config


def run(args):
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    config = {**load_config(args.config), "async_pipeline": False, "long_response_windows": True}
    config["tasks"] = [{"task_id": "fixture-speaking", "task_version": "1"}]
    runtime = create_runtime(args.data_dir, config=config)
    started = time.monotonic()
    results = []
    reports = []
    token = None
    try:
        actor_id = "fixture-model-" + secrets.token_hex(6)
        password = secrets.token_urlsafe(24)
        actor = runtime.auth.bootstrap_fixture_account(actor_id, ActorRole.STUDENT, password)
        runtime.consents.activate(actor, config["consent_version"])
        token = runtime.auth.login(actor_id, password)
        for name, path in [("short", args.audio_short), ("long", args.audio_long)]:
            data = path.read_bytes()
            elapsed = time.monotonic()
            status = runtime.app._student_api.submit(
                token,
                SubmitRequest(
                    task_id="fixture-speaking",
                    task_version="1",
                    consent_version=config["consent_version"],
                    filename=path.name,
                    content_type="audio/wav",
                    audio_bytes=data,
                ),
            )
            report = runtime.app._reports.get(status.response_id)
            assert status.status in {ResponseStatus.COMPLETED, ResponseStatus.REVIEW_REQUIRED}, (
                status
            )
            assert report is not None and not report.evidence_issues
            if name == "short":
                assert report.overall_score is not None and report.overall_band is not None
                assert report.source_versions["asr_model"] == "whisper-small"
            else:
                assert ReasonCode.SCORE_AGGREGATED in report.reasons
                assert status.status is ResponseStatus.REVIEW_REQUIRED
                assert report.source_versions["aggregation"] == "median-windows-v1"
                windows = json.loads(report.source_versions["window_results"])
                assert len(windows) == 2 and windows[0]["start_s"] == 0
                assert windows[0]["end_s"] == windows[1]["start_s"]
            reports.append(report)
            results.append(
                {
                    "fixture": name,
                    "audio_sha256": hashlib.sha256(data).hexdigest(),
                    "response_id": status.response_id,
                    "response_status": status.status.value,
                    "assessment_status": report.assessment_status.value,
                    "overall_score": report.overall_score,
                    "overall_band": report.overall_band.value if report.overall_band else None,
                    "reasons": [reason.value for reason in report.reasons],
                    "comments": len(report.comments),
                    "invalid_evidence": len(report.evidence_issues),
                    "source_versions": report.source_versions,
                    "elapsed_seconds": round(time.monotonic() - elapsed, 3),
                }
            )
        pipeline = runtime.control.pipeline
        assert pipeline._asr._engine._model is not None
        assert pipeline._extractor._vad._engine._model is not None
        model = pipeline._scorer._artifact.sha256
    finally:
        runtime.close()
    reopened = create_runtime(args.data_dir, config=config)
    try:
        assert reopened.auth.resolve(token).actor_id == actor_id
        for report in reports:
            assert reopened.app._reports.get(report.response_id) == report
        reopened.auth.logout(token)
    finally:
        reopened.close()
    evidence = {
        "result": "PASS",
        "fixtures": results,
        "real_asr_vad_loaded": True,
        "model_sha256": model,
        "restart_reports_sessions": "PASS",
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "cefr_accuracy": "NOT_MEASURED",
    }
    (args.evidence_dir / "result.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False)
    )
    print(
        json.dumps(
            {
                "result": "PASS",
                "fixtures": len(results),
                "elapsed_seconds": evidence["elapsed_seconds"],
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("config", "data-dir", "audio-short", "audio-long", "evidence-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    run(parser.parse_args())
