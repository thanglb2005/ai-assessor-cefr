from importlib.metadata import PackageNotFoundError
from types import ModuleType

import numpy as np
import pytest

from aicefr.features.local import SileroVadEngine, VadUnavailableError


def test_silero_checks_mono_float32_16khz_and_returns_seconds(monkeypatch):
    calls = {}
    model = object()
    package = ModuleType("silero_vad")
    def load(**kwargs):
        calls["load"] = kwargs
        return model

    package.load_silero_vad = load

    def get_timestamps(tensor, loaded, **kwargs):
        calls["arguments"] = (tensor, loaded, kwargs)
        return [{"start": 0.1, "end": 0.8}]

    package.get_speech_timestamps = get_timestamps
    torch = ModuleType("torch")
    torch.from_numpy = lambda value: value
    monkeypatch.setitem(__import__("sys").modules, "silero_vad", package)
    monkeypatch.setitem(__import__("sys").modules, "torch", torch)
    monkeypatch.setattr("aicefr.features.local.version", lambda _: "6.2.1")
    engine = SileroVadEngine(threshold=0.6, min_silence_ms=200)
    values = np.ones(1600, dtype=np.float32)
    assert engine.segments(values, 16_000) == [(0.1, 0.8)]
    assert engine.version == "6.2.1" and engine.name == "silero"
    assert calls["load"] == {"onnx": False}
    assert calls["arguments"][1] is model
    assert calls["arguments"][2] == {
        "threshold": 0.6, "sampling_rate": 16_000,
        "min_silence_duration_ms": 200, "return_seconds": True,
    }


@pytest.mark.parametrize(
    ("values", "rate"),
    [(np.zeros((2, 20), dtype=np.float32), 16_000),
     (np.zeros(20, dtype=np.float64), 16_000),
     (np.zeros(20, dtype=np.float32), 8_000)],
)
def test_silero_rejects_noncontract_audio(values, rate):
    with pytest.raises(ValueError):
        SileroVadEngine().segments(values, rate)


def test_missing_silero_import_is_controlled_and_does_not_load_model(monkeypatch):
    monkeypatch.setattr("aicefr.features.local.version", lambda _: "6.2.1")
    monkeypatch.setitem(__import__("sys").modules, "silero_vad", None)
    engine = SileroVadEngine()
    assert engine.version == "6.2.1"
    with pytest.raises(VadUnavailableError):
        engine.segments(np.zeros(1024, dtype=np.float32), 16_000)


def test_missing_silero_distribution_version_refuses_with_explicit_value(monkeypatch):
    def package_missing(_name):
        raise PackageNotFoundError

    monkeypatch.setattr("aicefr.features.local.version", package_missing)
    monkeypatch.setitem(__import__("sys").modules, "silero_vad", ModuleType("silero_vad"))
    engine = SileroVadEngine()
    assert engine.version == "unavailable"
    with pytest.raises(VadUnavailableError, match="version unavailable"):
        engine.segments(np.zeros(1024, dtype=np.float32), 16_000)


def test_invalid_silero_configuration_rejected():
    with pytest.raises(ValueError):
        SileroVadEngine(threshold=float("nan"))
    with pytest.raises(ValueError):
        SileroVadEngine(min_silence_ms=0)
    with pytest.raises(ValueError):
        SileroVadEngine(min_silence_ms=True)
    with pytest.raises(ValueError):
        SileroVadEngine(min_silence_ms=150.0)
