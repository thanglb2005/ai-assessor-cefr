"""M02-TEST-001/002/004/005/006: synthetic audio only."""

from __future__ import annotations

import hashlib
import io

import numpy as np
import pytest
import soundfile as sf

from aicefr.audio.config import AudioFormat, QCConfig
from aicefr.audio.decoder import decode_and_measure
from aicefr.contracts import QCStatus, ReasonCode


def config(**overrides: object) -> QCConfig:
    values = dict(
        version="test-m02-v1",
        accepted_formats=tuple(AudioFormat),
        max_input_bytes=1_000_000,
        min_duration_s=0.01,
        max_duration_s=1.0,
        max_input_sample_rate_hz=48_000,
        silence_threshold=0.01,
        clipping_threshold=0.99,
        review_silence_ratio=0.5,
        reject_silence_ratio=0.9,
        review_clipping_ratio=0.3,
        reject_clipping_ratio=0.6,
    )
    values.update(overrides)
    return QCConfig(**values)


def audio_bytes(
    samples: np.ndarray, rate: int = 16_000, *, format: str = "WAV",
    subtype: str | None = None,
) -> bytes:
    output = io.BytesIO()
    sf.write(output, samples, rate, format=format, subtype=subtype)
    return output.getvalue()


def test_empty_corrupt_and_unsupported_subtype() -> None:
    empty = decode_and_measure(b"", "wav", config())
    assert empty.audio is None
    assert empty.qc.status is QCStatus.REJECT
    assert empty.qc.reasons == (ReasonCode.QC_EMPTY_AUDIO,)
    assert all(
        m.value is None and m.missing_reason is ReasonCode.QC_EMPTY_AUDIO
        for m in empty.qc.measurements
    )

    corrupt = decode_and_measure(b"not an audio file", "wav", config())
    assert corrupt.qc.reasons == (ReasonCode.QC_DECODE_FAILED,)
    assert corrupt.audio is None

    wav_float = audio_bytes(np.full(160, 0.2), subtype="FLOAT")
    unsupported = decode_and_measure(wav_float, "wav", config())
    assert unsupported.qc.reasons == (ReasonCode.QC_UNSUPPORTED_FORMAT,)


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"max_input_bytes": 20}, ReasonCode.QC_INPUT_TOO_LARGE),
        ({"max_input_sample_rate_hz": 8_000}, ReasonCode.QC_SAMPLE_RATE_LIMIT),
        ({"max_duration_s": 0.01}, ReasonCode.QC_DURATION_LIMIT),
    ],
)
def test_resource_caps(overrides: dict[str, object], reason: ReasonCode) -> None:
    data = audio_bytes(np.ones(8_000, dtype=np.float32) * 0.2)
    result = decode_and_measure(data, "wav", config(**overrides))
    assert result.audio is None
    assert result.qc.reasons == (reason,)


def test_pcm_16k_mono_deterministic_resample() -> None:
    rate = 32_000
    signal = np.sin(2 * np.pi * 440 * np.arange(rate // 4) / rate).astype(np.float32) * 0.5
    data = audio_bytes(signal, rate)
    first = decode_and_measure(data, ".wav", config())
    second = decode_and_measure(data, "wav", config())
    assert first.audio is not None and second.audio is not None
    assert first.audio.sample_rate_hz == 16_000
    assert first.audio.samples.ndim == 1 and first.audio.samples.dtype == np.float32
    assert first.audio.samples.flags.c_contiguous
    assert first.audio.duration_s == pytest.approx(0.25, abs=1 / 16_000)
    assert first.audio.audio_sha256 == hashlib.sha256(data).hexdigest()
    np.testing.assert_allclose(first.audio.samples, second.audio.samples, atol=1e-7)
    assert first.qc.qc_config_version == "test-m02-v1"


def test_declared_format_mismatch_and_disabled_format() -> None:
    data = audio_bytes(np.zeros(160, dtype=np.float32))
    mismatch = decode_and_measure(data, "flac", config())
    assert mismatch.audio is None
    assert mismatch.qc.reasons == (ReasonCode.QC_FORMAT_MISMATCH,)
    disabled = decode_and_measure(data, "wav", config(accepted_formats=(AudioFormat.FLAC,)))
    assert disabled.qc.reasons == (ReasonCode.QC_UNSUPPORTED_FORMAT,)
    unknown = decode_and_measure(data, "aiff", config())
    assert unknown.qc.reasons == (ReasonCode.QC_UNSUPPORTED_FORMAT,)


@pytest.mark.parametrize(
    ("container", "subtype", "extension"),
    [
        ("WAV", "PCM_16", "wav"),
        ("FLAC", "PCM_16", "flac"),
        ("OGG", "VORBIS", "ogg"),
        ("MP3", "MPEG_LAYER_III", "mp3"),
    ],
)
def test_whitelisted_formats(container: str, subtype: str, extension: str) -> None:
    data = audio_bytes(np.sin(np.arange(3_200) * 0.03).astype(np.float32) * 0.3,
                       format=container, subtype=subtype)
    result = decode_and_measure(data, extension, config())
    assert result.qc.status is QCStatus.PASS
    assert result.qc.reasons == ()
    assert result.audio is not None and result.audio.samples.size > 0


def test_stereo_mean_and_more_than_two_channels_rejected() -> None:
    left = np.full(800, 0.25, dtype=np.float32)
    right = np.full(800, -0.125, dtype=np.float32)
    stereo = audio_bytes(np.column_stack((left, right)), subtype="PCM_16")
    result = decode_and_measure(stereo, "wav", config())
    assert result.audio is not None
    np.testing.assert_allclose(result.audio.samples, 0.0625, atol=1e-4)
    three_channel = audio_bytes(np.column_stack((left, right, left)), subtype="PCM_16")
    rejected = decode_and_measure(three_channel, "wav", config())
    assert rejected.audio is None
    assert rejected.qc.reasons == (ReasonCode.QC_TOO_MANY_CHANNELS,)


def test_config_requires_explicit_valid_limits() -> None:
    with pytest.raises(ValueError, match="version"):
        config(version="")
    with pytest.raises(ValueError, match="accepted_formats"):
        config(accepted_formats=())
    with pytest.raises(ValueError, match="max_input_bytes"):
        config(max_input_bytes=0)
    with pytest.raises(ValueError, match="duration"):
        config(min_duration_s=2)
    with pytest.raises(ValueError, match="amplitude"):
        config(silence_threshold=1.0)
    with pytest.raises(ValueError, match="silence REVIEW"):
        config(review_silence_ratio=1.0)
