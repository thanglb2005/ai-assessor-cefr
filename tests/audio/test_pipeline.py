"""M02-TEST-008: no automatic ASR for QC REVIEW or REJECT."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pytest
from tests.audio.test_decoder import audio_bytes, config

from aicefr.audio.pipeline import process_audio
from aicefr.contracts import AsrStatus, DecodedAudio, QCResult, QCStatus, Transcript


@dataclass
class AsrSpy:
    calls: list[tuple[str, DecodedAudio, QCResult]] = field(default_factory=list)

    def transcribe(self, response_id: str, audio: DecodedAudio, qc: QCResult) -> Transcript:
        self.calls.append((response_id, audio, qc))
        return Transcript(
            response_id=response_id,
            status=AsrStatus.OK,
            text="synthetic",
            engine="spy",
            engine_version="test",
            decode_config_version="test",
            audio_sha256=audio.audio_sha256,
            test_only=True,
        )


@pytest.mark.parametrize(
    ("signal", "expected_status", "expected_calls"),
    [
        (np.full(1_600, 0.25, dtype=np.float32), QCStatus.PASS, 1),
        (np.concatenate((np.zeros(960), np.full(640, 0.25))).astype(np.float32),
         QCStatus.REVIEW, 0),
        (np.zeros(1_600, dtype=np.float32), QCStatus.REJECT, 0),
    ],
)
def test_pass_only_dispatch(signal: np.ndarray, expected_status: QCStatus,
                            expected_calls: int) -> None:
    spy = AsrSpy()
    result = process_audio(
        response_id="synthetic-r1", data=audio_bytes(signal), declared_extension="wav",
        config=config(), asr=spy,
    )
    assert result.qc.status is expected_status
    assert len(spy.calls) == expected_calls
    assert (result.transcript is not None) is (expected_calls == 1)
    assert result.awaiting_review is (expected_status is QCStatus.REVIEW)
    if expected_calls:
        assert spy.calls[0][1] is result.audio
        assert spy.calls[0][2] is result.qc


def test_structural_reject_does_not_dispatch_or_create_transcript() -> None:
    spy = AsrSpy()
    result = process_audio(
        response_id="synthetic-r2", data=b"", declared_extension="wav", config=config(),
        asr=spy,
    )
    assert result.qc.status is QCStatus.REJECT
    assert result.audio is None and result.transcript is None
    assert not result.awaiting_review and not spy.calls
