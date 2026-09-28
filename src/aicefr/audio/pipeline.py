"""M02 boundary: only QC PASS may automatically enter ASR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from aicefr.audio.config import QCConfig
from aicefr.audio.decoder import decode_and_measure
from aicefr.contracts import DecodedAudio, QCResult, QCStatus, Transcript
from aicefr.qc.policy import evaluate_qc


class AsrPort(Protocol):
    def transcribe(self, response_id: str, audio: DecodedAudio, qc: QCResult) -> Transcript: ...


@dataclass(frozen=True, slots=True)
class PipelineResult:
    audio: DecodedAudio | None
    qc: QCResult
    transcript: Transcript | None

    @property
    def awaiting_review(self) -> bool:
        return self.qc.status is QCStatus.REVIEW


def process_audio(
    *, response_id: str, data: bytes, declared_extension: str, config: QCConfig, asr: AsrPort,
) -> PipelineResult:
    """Decode and classify audio, then dispatch PASS only through the injected port."""
    decoded = decode_and_measure(data, declared_extension, config)
    qc = evaluate_qc(decoded.qc, config)
    if qc.status is not QCStatus.PASS or decoded.audio is None:
        return PipelineResult(audio=decoded.audio, qc=qc, transcript=None)
    transcript = asr.transcribe(response_id, decoded.audio, qc)
    return PipelineResult(audio=decoded.audio, qc=qc, transcript=transcript)
