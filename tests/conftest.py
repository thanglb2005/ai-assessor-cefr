import pytest

FEATURE_ORDER_V2 = (
    "n_words", "words_per_sec", "total_dur", "mean_word_len", "ttr", "log_uniq",
    "asr_conf_mean", "asr_conf_geo", "vad_silence_ratio", "vad_mean_pause",
    "vad_pause_per_min", "vad_long_pause_ratio", "vad_pause_sd", "vad_mean_seg_len",
    "vad_n_seg_per_min", "vad_articulation_rate", "vad_onset_delay", "vad_speech_sec",
)  # fmt: skip


@pytest.fixture
def feature_order_v2():
    """Đúng 18 tên đặc trưng của ridge_resp_v2, theo thứ tự artifact."""
    return FEATURE_ORDER_V2
