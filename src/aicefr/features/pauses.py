"""Đặc trưng ngừng từ segment VAD (M04 Spec v0.2, catalogue #9–18).

`P` = khoảng giữa hai segment liên tiếp cộng khoảng đuôi, chỉ giữ khoảng > 0,30 s.
`P` rỗng cho 0 ở #10, #12, #13 là giá trị đo thật; không có segment nào thì cả
10 đặc trưng là `None`.
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence

from aicefr.contracts import ReasonCode
from aicefr.features.text import Measure

PAUSE_MIN_S = 0.30
LONG_PAUSE_S = 1.00
# Timestamp VAD ở mức mili-giây; bỏ sai số dấu phẩy động khi so đúng ngưỡng
# (vd. 1,3 − 1,0 = 0,30000000000000004 không được tính là > 0,30).
_EPS = 1e-9

VAD_FEATURES = (
    "vad_silence_ratio",
    "vad_mean_pause",
    "vad_pause_per_min",
    "vad_long_pause_ratio",
    "vad_pause_sd",
    "vad_mean_seg_len",
    "vad_n_seg_per_min",
    "vad_articulation_rate",
    "vad_onset_delay",
    "vad_speech_sec",
)


def pause_features(
    segments: Sequence[tuple[float, float]], duration_s: float, n_words: int | None
) -> dict[str, Measure]:
    """`n_words=None` khi transcript không dùng được: #16 là None, còn lại vẫn tính."""
    if not segments:
        return dict.fromkeys(VAD_FEATURES, (None, ReasonCode.FEATURE_NOT_COMPUTABLE))

    seg = sorted(segments)
    lengths = [end - start for start, end in seg]
    speech = sum(lengths)
    gaps = [seg[i + 1][0] - seg[i][1] for i in range(len(seg) - 1)]
    gaps.append(duration_s - seg[-1][1])
    pauses = [g for g in gaps if g > PAUSE_MIN_S + _EPS]
    minutes = duration_s / 60

    out: dict[str, Measure] = {
        "vad_silence_ratio": (1 - speech / duration_s, None),
        "vad_mean_pause": (statistics.fmean(pauses) if pauses else 0.0, None),
        "vad_pause_per_min": (len(pauses) / minutes, None),
        "vad_long_pause_ratio": (
            sum(p > LONG_PAUSE_S + _EPS for p in pauses) / len(pauses) if pauses else 0.0,
            None,
        ),
        "vad_pause_sd": (statistics.pstdev(pauses) if len(pauses) > 1 else 0.0, None),
        "vad_mean_seg_len": (statistics.fmean(lengths), None),
        "vad_n_seg_per_min": (len(seg) / minutes, None),
        "vad_onset_delay": (seg[0][0], None),
        "vad_speech_sec": (speech, None),
    }
    if n_words is None or speech <= 0:
        out["vad_articulation_rate"] = (None, ReasonCode.FEATURE_NOT_COMPUTABLE)
    else:
        out["vad_articulation_rate"] = (n_words / speech, None)
    return out
