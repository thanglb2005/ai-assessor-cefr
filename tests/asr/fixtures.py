"""Fixture M03 do nhóm tạo (M03 Test Plan v0.2); không phải audio hay lời nói người học."""

import numpy as np

from aicefr.asr.service import EngineResult, ModelUnavailableError, RawWord
from aicefr.contracts import DecodedAudio, QCResult, QCStatus, Word

WEIGHT_SMALL = "Systran/faster-whisper-small"


def raw_words(tokens, dur=0.3, gap=0.1, prob=0.9):
    out, t = [], 0.1
    for tok in tokens:
        out.append(RawWord(tok, t, t + dur, prob))
        t += dur + gap
    return out


def words(tokens, dur=0.3, gap=0.1, prob=0.9):
    return [Word(text=w.text, start_s=w.start_s, end_s=w.end_s, prob=w.prob)
            for w in raw_words(tokens, dur, gap, prob)]  # fmt: skip


def audio(duration=60.0):
    return DecodedAudio(samples=np.zeros(16, dtype=np.float32), sample_rate_hz=16_000,
                        duration_s=duration, audio_sha256="b" * 64)  # fmt: skip


def qc(status=QCStatus.PASS):
    return QCResult(status=status, qc_config_version="qc-v1")


class FakeAsrEngine:
    """Engine giả cho unit test; kết quả luôn mang test_only=True."""

    def __init__(self, result=None, error=None, weight=WEIGHT_SMALL):
        self.result = result or EngineResult(
            text="I think the city is nice", words=raw_words("I think the city is nice".split()),
            engine="fake-asr", engine_version="0.0-test", weight_name=weight, test_only=True,
        )  # fmt: skip
        self.error, self.calls = error, 0

    def transcribe(self, audio):
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


class CountingLoader:
    def __init__(self, engine=None, unavailable=False):
        self.engine, self.unavailable, self.calls = engine, unavailable, 0

    def __call__(self):
        self.calls += 1
        if self.unavailable:
            raise ModelUnavailableError("thiếu weight local")
        return self.engine
