"""Fixture M04 do nhóm tạo (M04 Test Plan v0.2); không phải dữ liệu người học."""

import numpy as np

from aicefr.contracts import AsrStatus, DecodedAudio, Transcript, Word

# FX-TEXT (M04 Test Plan v0.2): 14 word, D = 11,0 s.
FX_TOKENS = ["Um,", "I", "think", "that", "the", "city", "is", "nice.",
             "The", "city", "is", "big", "and", "green."]  # fmt: skip
FX_PROBS = [0.5, 0.9, 0.8, 0.9, 0.95, 0.7, 0.9, 0.85, 0.9, 0.8, 0.9, 0.6, 0.95, None]
FX_SEGMENTS = [(0.5, 3.0), (3.4, 6.0), (7.5, 10.0)]  # FX-VAD
FX_DURATION = 11.0


def make_words(tokens, probs=None):
    probs = probs if probs is not None else [0.9] * len(tokens)
    return tuple(
        Word(text=t, start_s=0.5 + 0.6 * i, end_s=0.9 + 0.6 * i, prob=p)
        for i, (t, p) in enumerate(zip(tokens, probs, strict=True))
    )


def make_transcript(words=None, status=AsrStatus.OK, text="fixture", asr_model="whisper-small"):
    return Transcript(
        response_id="r1",
        status=status,
        text=text,
        words=make_words(FX_TOKENS, FX_PROBS) if words is None else words,
        asr_model=asr_model,
        engine="fake",
        engine_version="fixture",
        decode_config_version="asr-decode-v1",
        audio_sha256="a" * 64,
        test_only=True,
    )


def make_audio(duration=FX_DURATION):
    return DecodedAudio(
        samples=np.zeros(16, dtype=np.float32),
        sample_rate_hz=16_000,
        duration_s=duration,
        audio_sha256="a" * 64,
    )


class FakeVad:
    def __init__(self, segments=FX_SEGMENTS, name="silero", threshold=0.5, min_silence_ms=150,
                 fail=False):  # fmt: skip
        self.name, self.version = name, "6.2.1"
        self.threshold, self.min_silence_ms = threshold, min_silence_ms
        self._segments, self._fail, self.calls = list(segments), fail, 0

    def segments(self, samples, sample_rate_hz):
        self.calls += 1
        if self._fail:
            raise RuntimeError("VAD hỏng")
        return self._segments


TRAINED_WITH = {"asr_model": "whisper-small", "vad_name": "silero", "vad_threshold": 0.5,
                "vad_min_silence_ms": 150}  # fmt: skip

EXPECTED_TEXT = {
    "n_words": 14,
    "words_per_sec": 1.272727,
    "mean_word_len": 3.214286,
    "ttr": 0.785714,
    "log_uniq": 2.484907,
    "asr_conf_mean": 0.819231,
    "asr_conf_geo": 0.806303,
}
EXPECTED_VAD = {
    "vad_silence_ratio": 0.309091,
    "vad_mean_pause": 0.966667,
    "vad_pause_per_min": 16.363636,
    "vad_long_pause_ratio": 0.333333,
    "vad_pause_sd": 0.449691,
    "vad_mean_seg_len": 2.533333,
    "vad_n_seg_per_min": 16.363636,
    "vad_articulation_rate": 1.842105,
    "vad_onset_delay": 0.5,
    "vad_speech_sec": 7.6,
}
