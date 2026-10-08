"""Bounded in-process audio decoding for M02.

The caller supplies already-authorized bytes. No pathname or product QC defaults
are accepted here. Hard wall-clock isolation is outside the approved W2 scope.
"""

from __future__ import annotations

import hashlib
import io
import math
from dataclasses import dataclass, replace

import numpy as np
import soundfile as sf
import soxr

from aicefr.audio.config import AudioFormat, QCConfig
from aicefr.contracts import DecodedAudio, QCResult, QCStatus, ReasonCode
from aicefr.qc.measurements import measure_audio, missing_measurements

_OUTPUT_RATE_HZ = 16_000
_READ_BLOCK_FRAMES = 8_192
_EXTENSION_FORMATS = {item.value: item for item in AudioFormat}


@dataclass(frozen=True, slots=True)
class DecodeResult:
    audio: DecodedAudio | None
    qc: QCResult


def _reject(reason: ReasonCode, config: QCConfig) -> DecodeResult:
    return DecodeResult(
        audio=None,
        qc=QCResult(
            status=QCStatus.REJECT,
            reasons=(reason,),
            qc_config_version=config.version,
            measurements=missing_measurements(reason),
        ),
    )


def _detected_format(container: str, subtype: str) -> AudioFormat | None:
    container = container.upper()
    subtype = subtype.upper()
    if container == "WAV" and subtype.startswith("PCM_"):
        return AudioFormat.WAV_PCM
    if container == "FLAC" and subtype.startswith("PCM_"):
        return AudioFormat.FLAC
    if container == "OGG" and subtype == "VORBIS":
        return AudioFormat.OGG_VORBIS
    if subtype == "MPEG_LAYER_III" or container == "MPEG_LAYER_III":
        return AudioFormat.MP3
    return None


def _read_bounded(stream: sf.SoundFile, max_frames: int) -> np.ndarray | None:
    """Read at most max_frames+1 to detect a lying/unknown frame header."""
    if stream.frames < 0 or stream.frames > max_frames:
        return None
    chunks: list[np.ndarray] = []
    total = 0
    while True:
        requested = min(_READ_BLOCK_FRAMES, max_frames - total + 1)
        chunk = stream.read(frames=requested, dtype="float32", always_2d=True)
        if chunk.size == 0:
            break
        total += len(chunk)
        if total > max_frames:
            return None
        chunks.append(chunk)
    if not chunks:
        return np.empty((0, stream.channels), dtype=np.float32)
    return np.concatenate(chunks, axis=0)


def decode_and_measure(data: bytes, declared_extension: str, config: QCConfig) -> DecodeResult:
    """Return provisional PASS plus measurements, or a structural REJECT.

    The QC policy in M02-TASK-002 may change the provisional PASS to REVIEW or
    REJECT. The raw bytes stay unchanged and are never written by this function.
    """
    if not isinstance(data, bytes) or not data:
        return _reject(ReasonCode.QC_EMPTY_AUDIO, config)
    if len(data) > config.max_input_bytes:
        return _reject(ReasonCode.QC_INPUT_TOO_LARGE, config)
    if not isinstance(declared_extension, str):
        return _reject(ReasonCode.QC_UNSUPPORTED_FORMAT, config)
    declared = _EXTENSION_FORMATS.get(declared_extension.strip().lower().removeprefix("."))
    if declared is None or declared not in config.accepted_formats:
        return _reject(ReasonCode.QC_UNSUPPORTED_FORMAT, config)

    audio_sha256 = hashlib.sha256(data).hexdigest()
    if declared in {AudioFormat.WEBM, AudioFormat.MP4}:
        from aicefr.audio.recordings import RecordingDecodeError, recording_format, recording_wav

        if recording_format(data) != declared.value:
            return _reject(ReasonCode.QC_FORMAT_MISMATCH, config)
        try:
            wav = recording_wav(data, config)
        except RecordingDecodeError as error:
            return _reject(error.reason, config)
        pcm_config = replace(
            config,
            accepted_formats=(AudioFormat.WAV_PCM,),
            max_input_bytes=max(config.max_input_bytes, len(wav)),
        )
        result = decode_and_measure(wav, "wav", pcm_config)
        if result.audio is not None:
            result = DecodeResult(
                audio=result.audio.model_copy(update={"audio_sha256": audio_sha256}), qc=result.qc
            )
        return result
    try:
        with sf.SoundFile(io.BytesIO(data)) as stream:
            actual = _detected_format(stream.format, stream.subtype)
            if actual is None or actual not in config.accepted_formats:
                return _reject(ReasonCode.QC_UNSUPPORTED_FORMAT, config)
            if actual is not declared:
                return _reject(ReasonCode.QC_FORMAT_MISMATCH, config)
            if stream.channels < 1 or stream.channels > 2:
                return _reject(ReasonCode.QC_TOO_MANY_CHANNELS, config)
            if stream.samplerate < 1 or stream.samplerate > config.max_input_sample_rate_hz:
                return _reject(ReasonCode.QC_SAMPLE_RATE_LIMIT, config)
            input_rate_hz = stream.samplerate
            max_frames = math.floor(config.max_duration_s * input_rate_hz)
            input_samples = _read_bounded(stream, max_frames)
            if input_samples is None:
                return _reject(ReasonCode.QC_DURATION_LIMIT, config)
        if input_samples.size == 0:
            return _reject(ReasonCode.QC_EMPTY_AUDIO, config)
        if input_samples.shape[1] == 2:
            mono = np.mean(input_samples, axis=1, dtype=np.float32)
        else:
            mono = input_samples[:, 0]
        mono = np.ascontiguousarray(mono, dtype=np.float32)
        if input_rate_hz != _OUTPUT_RATE_HZ:
            mono = soxr.resample(mono, input_rate_hz, _OUTPUT_RATE_HZ, quality="HQ")
            mono = np.ascontiguousarray(mono, dtype=np.float32)
        if mono.size == 0 or not np.isfinite(mono).all():
            return _reject(ReasonCode.QC_DECODE_FAILED, config)
        audio = DecodedAudio(
            samples=mono,
            sample_rate_hz=_OUTPUT_RATE_HZ,
            duration_s=float(mono.size / _OUTPUT_RATE_HZ),
            audio_sha256=audio_sha256,
        )
        qc = QCResult(
            status=QCStatus.PASS,
            qc_config_version=config.version,
            measurements=measure_audio(audio, config),
        )
        return DecodeResult(audio=audio, qc=qc)
    except Exception:  # Native decoder/resampler errors must not leak to callers.
        return _reject(ReasonCode.QC_DECODE_FAILED, config)
