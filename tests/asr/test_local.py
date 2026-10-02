from types import ModuleType, SimpleNamespace

import pytest
from tests.asr.fixtures import audio

from aicefr.asr.local import FasterWhisperEngine
from aicefr.asr.service import AsrService, ModelUnavailableError
from aicefr.contracts import QCResult, QCStatus


def model_dir(tmp_path):
    for filename in ("model.bin", "config.json", "tokenizer.json", "preprocessor_config.json"):
        (tmp_path / filename).write_text("fixture")
    return tmp_path


def test_missing_local_model_refuses_without_import_or_download(tmp_path):
    engine = FasterWhisperEngine(tmp_path / "absent")
    with pytest.raises(ModelUnavailableError):
        engine.transcribe(audio())


def test_local_adapter_passes_offline_english_word_timestamp_options(monkeypatch, tmp_path):
    seen = {}

    class Model:
        def transcribe(self, samples, **kwargs):
            seen["options"] = kwargs
            word = SimpleNamespace(word=" hello", start=0.1, end=0.4, probability=0.91)
            return iter([SimpleNamespace(text=" hello", words=[word])]), object()

    def constructor(path, **kwargs):
        seen["path"] = path
        seen["constructor"] = kwargs
        return Model()

    module = ModuleType("faster_whisper")
    module.WhisperModel = constructor
    monkeypatch.setitem(__import__("sys").modules, "faster_whisper", module)
    monkeypatch.setattr("importlib.metadata.version", lambda _: "1.2.3")
    result = FasterWhisperEngine(model_dir(tmp_path)).transcribe(audio())
    assert seen["constructor"]["local_files_only"] is True
    assert seen["constructor"]["cpu_threads"] == 1
    assert seen["options"]["language"] == "en"
    assert seen["options"]["word_timestamps"] is True
    assert seen["options"]["condition_on_previous_text"] is False
    assert result.engine_version == "1.2.3" and result.weight_name == "Systran/faster-whisper-small"
    assert result.test_only is False
    assert (result.words[0].text, result.words[0].prob) == (" hello", 0.91)


def test_unknown_weight_identity_is_preserved_for_refusal(monkeypatch, tmp_path):
    class Model:
        def transcribe(self, *_args, **_kwargs):
            return iter(()), object()

    module = ModuleType("faster_whisper")
    module.WhisperModel = lambda *_args, **_kwargs: Model()
    monkeypatch.setitem(__import__("sys").modules, "faster_whisper", module)
    monkeypatch.setattr("importlib.metadata.version", lambda _: "1.0")
    result = FasterWhisperEngine(model_dir(tmp_path), weight_name="small.en").transcribe(audio())
    assert result.weight_name == "Systran/faster-whisper-small.en"


def test_asr_engine_exception_message_and_traceback_are_not_logged(caplog):
    secret = "TRANSCRIPT-SECRET-9981"

    class Broken:
        def transcribe(self, _audio):
            raise RuntimeError(secret)

    result = AsrService(lambda: Broken(), trained_asr_model="whisper-small").transcribe(
        "r-safe", audio(), QCResult(status=QCStatus.PASS, qc_config_version="test")
    )
    assert result.status.value == "ASR_FAILED"
    assert secret not in caplog.text
    assert "Traceback" not in caplog.text and "response_id=r-safe" in caplog.text
