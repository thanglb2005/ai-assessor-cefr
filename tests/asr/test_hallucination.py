import pytest
from tests.asr.fixtures import words

from aicefr.asr.hallucination import HallucinationConfig, detect_hallucination
from aicefr.contracts import Word


def unique(n, prefix="w"):
    return [f"{prefix}{i}" for i in range(n)]


def test_normal_speech_has_no_finding():
    assert detect_hallucination(words("I think the city is really nice to live in".split())) is None


@pytest.mark.parametrize(("repeats", "flagged"), [(6, False), (7, True)])
def test_consecutive_token_repeats(repeats, flagged):
    """M03-TEST-008."""
    tokens = unique(3) + ["okay"] * repeats + unique(3, "v")
    finding = detect_hallucination(words(tokens))
    assert (finding is not None and finding.rule == "consecutive_repeat") is flagged


def _share_tokens(count, total):
    tokens = []
    for i in range(count):
        tokens += ["the", f"w{i}"]
    return (tokens + unique(total - len(tokens), "v"))[:total]


@pytest.mark.parametrize(
    ("count", "total", "flagged"), [(21, 60, False), (22, 60, True), (29, 59, False)]
)
def test_single_token_share(count, total, flagged):
    """M03-TEST-009: 21/60 = 0,35 không cờ; 22/60 cờ; dưới 60 từ không áp luật."""
    tokens = _share_tokens(count, total)
    assert len(tokens) == total
    finding = detect_hallucination(words(tokens))
    assert (finding is not None and finding.rule == "token_share") is flagged


@pytest.mark.parametrize(("repeats", "flagged"), [(2, False), (3, True)])
def test_phrase_repeated_back_to_back(repeats, flagged):
    """M03-TEST-010."""
    tokens = unique(2) + ["i", "like", "it"] * repeats + unique(2, "v")
    finding = detect_hallucination(words(tokens))
    assert (finding is not None and finding.rule == "phrase_repeat") is flagged


@pytest.mark.parametrize(("run", "flagged"), [(4, False), (5, True)])
def test_low_probability_tail(run, flagged):
    """M03-TEST-011."""
    ws = words(unique(10)) + words(unique(run, "t"), prob=0.01)
    finding = detect_hallucination(ws)
    assert (finding is not None and finding.rule == "low_prob_tail") is flagged


def test_missing_probability_breaks_low_probability_tail():
    ws = words(unique(10)) + words(unique(4, "t"), prob=0.01)
    ws[-3] = Word(text="x", start_s=ws[-3].start_s, end_s=ws[-3].end_s, prob=None)
    assert detect_hallucination(ws) is None


@pytest.mark.parametrize(("run", "flagged"), [(3, False), (4, True)])
def test_stalled_clock(run, flagged):
    """M03-TEST-012."""
    ws = words(unique(5)) + words(unique(run, "s"), dur=0.01, gap=0.0) + words(unique(3, "z"))
    finding = detect_hallucination(ws)
    assert (finding is not None and finding.rule == "stalled_clock") is flagged


def test_thresholds_are_versioned_config():
    cfg = HallucinationConfig()
    assert cfg.version == "hallucination-v1"
    strict = HallucinationConfig(max_consecutive_repeats=2)
    assert detect_hallucination(words(["a", "a", "a"]), strict).rule == "consecutive_repeat"
