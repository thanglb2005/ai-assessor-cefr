"""Offline faster-whisper adapter. Model files must already exist locally."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aicefr.asr.service import EngineResult, ModelUnavailableError, RawWord
from aicefr.contracts import DecodedAudio


class FasterWhisperEngine:
    """Lazy, local-only Whisper engine implementing :class:`AsrEngine`."""

    def __init__(
        self,
        model_dir: str | Path,
        *,
        weight_name: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self.model_dir = Path(model_dir).expanduser()
        self.weight_name = weight_name
        self.device = device
        self.compute_type = compute_type
        self._model: Any = None

    def _load(self) -> Any:
        if self._model is not None:
            return self._model
        required = ("model.bin", "config.json", "tokenizer.json", "preprocessor_config.json")
        if not self.model_dir.is_dir() or any(
            not (self.model_dir / name).is_file() for name in required
        ):
            raise ModelUnavailableError("local ASR model directory unavailable")
        try:
            from importlib.metadata import version as package_version

            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise ModelUnavailableError("faster-whisper dependency unavailable") from exc
        try:
            self._model = WhisperModel(
                str(self.model_dir), device=self.device, compute_type=self.compute_type,
                local_files_only=True, cpu_threads=1 if self.device == "cpu" else 0,
            )
            self._version = package_version("faster-whisper")
        except Exception as exc:
            # Constructor errors can include machine paths; expose only a stable refusal.
            raise ModelUnavailableError("local ASR model unavailable") from exc
        return self._model

    def transcribe(self, audio: DecodedAudio) -> EngineResult:
        model = self._load()
        try:
            segments, _info = model.transcribe(
                audio.samples, language="en", word_timestamps=True, beam_size=5,
                vad_filter=False, condition_on_previous_text=False,
            )
            words: list[RawWord] = []
            text: list[str] = []
            for segment in segments:
                text.append(str(segment.text))
                for word in segment.words or ():
                    probability = getattr(word, "probability", None)
                    words.append(RawWord(
                        text=str(word.word), start_s=float(word.start), end_s=float(word.end),
                        prob=None if probability is None else float(probability),
                    ))
        except Exception:
            raise
        return EngineResult(
            text="".join(text), words=tuple(words), engine="faster-whisper",
            engine_version=self._version, weight_name=f"Systran/faster-whisper-{self.weight_name}",
        )


__all__ = ["FasterWhisperEngine"]
