from __future__ import annotations

import hashlib
import io
import shutil
import subprocess
from dataclasses import replace

import numpy as np
import pytest
import soundfile as sf

from aicefr.audio.config import AudioFormat, QCConfig
from aicefr.audio.decoder import decode_and_measure
from aicefr.audio.recordings import recording_format
from aicefr.contracts import QCStatus, ReasonCode
from aicefr.local.__main__ import _demo_config

pytestmark = pytest.mark.skipif(
    not (shutil.which("ffmpeg") and shutil.which("ffprobe")),
    reason="optional ffmpeg/ffprobe recording adapter unavailable",
)


def recording(kind: str, *, seconds: float = 2) -> bytes:
    assert shutil.which("ffmpeg"), "ffmpeg required for recording integration checks"
    stream = io.BytesIO()
    sf.write(stream, np.full(round(seconds * 16000), 0.2, dtype=np.float32), 16000, format="WAV")
    options = (
        ["-c:a", "libopus", "-f", "webm"]
        if kind == "webm"
        else ["-c:a", "aac", "-movflags", "frag_keyframe+empty_moov", "-f", "mp4"]
    )
    return subprocess.run(
        ["ffmpeg", "-v", "error", "-i", "pipe:0", *options, "pipe:1"],
        input=stream.getvalue(),
        capture_output=True,
        check=True,
    ).stdout


def config():
    return QCConfig(**{**_demo_config()["qc"], "accepted_formats": ("wav", "webm", "mp4")})


@pytest.mark.parametrize("kind", ["webm", "mp4"])
def test_real_browser_container_decode_preserves_original_hash(kind):
    data = recording(kind)
    before = hashlib.sha256(data).hexdigest()
    result = decode_and_measure(data, kind, config())
    assert result.qc.status is QCStatus.PASS
    assert result.audio is not None
    # AAC encoder padding can add about two frames; use actual decoded duration.
    assert 1.9 <= result.audio.duration_s <= 2.15
    assert result.audio.audio_sha256 == before == hashlib.sha256(data).hexdigest()
    assert recording_format(data) == kind


def test_recording_limits_mismatch_and_absent_decoder_fail_closed(monkeypatch):
    data = recording("webm", seconds=4)
    assert decode_and_measure(data, "mp4", config()).qc.reasons == (ReasonCode.QC_FORMAT_MISMATCH,)
    assert decode_and_measure(data, "webm", replace(config(), max_duration_s=3)).qc.reasons == (
        ReasonCode.QC_DURATION_LIMIT,
    )
    assert decode_and_measure(
        data, "webm", replace(config(), accepted_formats=(AudioFormat.WAV_PCM,))
    ).qc.reasons == (ReasonCode.QC_UNSUPPORTED_FORMAT,)
    monkeypatch.setattr("aicefr.audio.recordings.recording_available", lambda: False)
    assert decode_and_measure(data, "webm", config()).qc.reasons == (ReasonCode.QC_DECODE_FAILED,)


def test_invalid_recording_or_transcode_timeout_never_leaks_error(monkeypatch):
    assert decode_and_measure(b"\x1a\x45\xdf\xa3broken", "webm", config()).qc.reasons == (
        ReasonCode.QC_DECODE_FAILED,
    )
    data = recording("webm")

    def fail(*args, **kwargs):
        raise subprocess.TimeoutExpired("private-machine-path", 10)

    monkeypatch.setattr("aicefr.audio.recordings.subprocess.run", fail)
    result = decode_and_measure(data, "webm", config())
    assert result.audio is None and result.qc.reasons == (ReasonCode.QC_DECODE_FAILED,)
    assert "private-machine-path" not in result.qc.model_dump_json()
