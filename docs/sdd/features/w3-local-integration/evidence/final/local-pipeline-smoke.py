"""Independent reviewer smoke of the final local runtime; no input/token logging."""
import hashlib
import json
import secrets
import subprocess
import tempfile
import time
from pathlib import Path

from aicefr.api.student import SubmitRequest
from aicefr.contracts import ActorRole, AssessmentStatus, ResponseStatus
from aicefr.local.__main__ import _demo_config
from aicefr.local.app import create_runtime
from aicefr.report.sqlite import SQLiteReportRepository

base = Path('/home/thanglvc/Documents/HCMUTE/TLCN/ai-assessor-cefr-thamchie')
config = _demo_config()
config.update({'model_artifact': str(base/'src/aicefr/scoring/models/ridge_resp_v2.json'), 'asr_model_dir':'/tmp/aicefr-w3-models/faster-whisper-small'})
audio = (base/'artifacts/sample_audio/p3_b2.wav').read_bytes()
password = secrets.token_urlsafe(24)
start = time.monotonic()
with tempfile.TemporaryDirectory(prefix='aicefr-w3-final-runtime-') as data_dir:
    runtime = create_runtime(data_dir, config=config)
    try:
        actor = runtime.auth.bootstrap_fixture_account('fixture-final-smoke', ActorRole.STUDENT, password)
        runtime.consents.activate(actor, 'demo-v1')
        token = runtime.auth.login(actor.actor_id, password)
        status = runtime.app._student_api.submit(token, SubmitRequest(task_id='demo-speaking',task_version='1',consent_version='demo-v1',filename='local-smoke.wav',content_type='audio/wav',audio_bytes=audio))
        report = SQLiteReportRepository(runtime.store).get(status.response_id)
        assert status.status is ResponseStatus.COMPLETED and status.report_available
        assert report is not None and report.assessment_status is AssessmentStatus.ESTIMATED
        assert report.overall_score is not None and report.overall_band is not None
        assert report.teacher_verified is False and report.teacher_final is None
        assert report.comments and not report.evidence_issues
        assert all(comment.evidence_id for comment in report.comments)
        assert report.source_versions['asr_model'] == 'whisper-small'
        assert report.source_versions['qc_config'] == config['qc']['version']
        response_id = status.response_id
        output = {'source_revision':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),'audio_sha256':hashlib.sha256(audio).hexdigest(),'duration_s':41.145,'status':status.status.value,'report_available':status.report_available,'assessment_status':report.assessment_status.value,'distinct_comment_evidence_ids':len({comment.evidence_id for comment in report.comments}),'comments':len(report.comments),'invalid_evidence':len(report.evidence_issues),'teacher_verified':report.teacher_verified,'source_versions':report.source_versions,'elapsed_seconds':round(time.monotonic()-start,3),'wer':'NOT_MEASURED','cefr_accuracy':'NOT_MEASURED'}
    finally:
        runtime.close()
    reopened = create_runtime(data_dir, config=config)
    try:
        restored = SQLiteReportRepository(reopened.store).get(response_id)
        assert restored == report
        assert reopened.store.get_response(response_id).status is ResponseStatus.COMPLETED
        assert reopened.auth.resolve(token).actor_id == actor.actor_id
        reopened.auth.logout(token)
        from aicefr.auth.service import AuthorizationError
        try:
            reopened.auth.resolve(token)
        except AuthorizationError:
            output['restart_report_session_and_logout']='PASS'
        else:
            raise AssertionError('revoked session still active')
    finally:
        reopened.close()
print(json.dumps(output, ensure_ascii=False), flush=True)
print('FINAL_LOCAL_PIPELINE_SMOKE_PASS', flush=True)
