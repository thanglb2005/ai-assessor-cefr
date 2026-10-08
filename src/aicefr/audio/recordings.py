"""Bounded, pipe-only WebM/MP4 recording decode; original upload remains immutable."""

from __future__ import annotations

import json
import math
import shutil
import subprocess

from aicefr.contracts import ReasonCode


class RecordingDecodeError(Exception):
    def __init__(self, reason: ReasonCode) -> None:
        self.reason = reason


def recording_format(data: bytes) -> str | None:
    if data.startswith(b"\x1a\x45\xdf\xa3"):
        return "webm"
    if data[4:8] == b"ftyp":
        return "mp4"
    return None


def recording_available() -> bool:
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def recording_wav(data: bytes, config) -> bytes:
    if not recording_available():
        raise RecordingDecodeError(ReasonCode.QC_DECODE_FAILED)
    try:
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-protocol_whitelist",
                "pipe",
                "-show_entries",
                "stream=codec_type,channels,sample_rate:format=duration,format_name",
                "-of",
                "json",
                "pipe:0",
            ],
            input=data,
            capture_output=True,
            check=True,
            timeout=10,
        )
        info = json.loads(probe.stdout)
        audio = [stream for stream in info["streams"] if stream["codec_type"] == "audio"]
        if len(audio) != 1 or not 1 <= int(audio[0]["channels"]) <= 2:
            raise RecordingDecodeError(ReasonCode.QC_TOO_MANY_CHANNELS)
        rate = int(audio[0]["sample_rate"])
        if not 1 <= rate <= config.max_input_sample_rate_hz:
            raise RecordingDecodeError(ReasonCode.QC_SAMPLE_RATE_LIMIT)
        duration = info.get("format", {}).get("duration")
        if duration is not None and (
            not math.isfinite(float(duration)) or float(duration) > config.max_duration_s
        ):
            raise RecordingDecodeError(ReasonCode.QC_DURATION_LIMIT)
        ceiling = math.ceil((config.max_duration_s + 1) * 16000 * 2) + 4096
        result = subprocess.run(
            [
                "ffmpeg",
                "-nostdin",
                "-v",
                "error",
                "-threads",
                "1",
                "-protocol_whitelist",
                "pipe",
                "-i",
                "pipe:0",
                "-map",
                "0:a:0",
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-t",
                str(config.max_duration_s + 1),
                "-fs",
                str(ceiling),
                "-f",
                "wav",
                "-c:a",
                "pcm_s16le",
                "pipe:1",
            ],
            input=data,
            capture_output=True,
            check=True,
            timeout=30,
        )
        if len(result.stdout) > ceiling:
            raise RecordingDecodeError(ReasonCode.QC_DURATION_LIMIT)
        return result.stdout
    except RecordingDecodeError:
        raise
    except Exception:
        raise RecordingDecodeError(ReasonCode.QC_DECODE_FAILED) from None
