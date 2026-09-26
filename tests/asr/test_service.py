import logging

import pytest
from tests.asr.fixtures import CountingLoader, FakeAsrEngine, audio, qc, raw_words

from aicefr.asr.service import AsrService, EngineResult, RawWord
from aicefr.contracts import AsrStatus, QCStatus, ReasonCode


def service(engine=None, loader=None, trained="whisper-small"):
    return AsrService(engine_loader=loader or CountingLoader(engine or FakeAsrEngine()),
                      trained_asr_model=trained)  # fmt: skip


def result(words, text="fixture text", weight="Systran/faster-whisper-small"):
    return EngineResult(text=text, words=words, engine="fake-asr", engine_version="0.0-test",
                        weight_name=weight, test_only=True)  # fmt: skip


def test_ok_transcript_keeps_order_filler_and_provenance():
    """M03-TEST-001."""
    eng = FakeAsrEngine(result(raw_words(["um", "I", "think"]), text="um I think"))
    t = service(eng).transcribe("r1", audio(), qc())
    assert t.status is AsrStatus.OK and t.reasons == ()
    assert [w.text for w in t.words] == ["um", "I", "think"]
    assert (t.asr_model, t.engine, t.engine_version) == ("whisper-small", "fake-asr", "0.0-test")
    assert t.decode_config_version == "asr-decode-v1" and t.audio_sha256 == "b" * 64
    assert t.test_only is True


def test_missing_probability_stays_none():
    """M03-TEST-002 (regression REF-03: trước đây thành 0.0)."""
    ws = raw_words(["a", "b", "c"])
    ws[1] = RawWord("b", ws[1].start_s, ws[1].end_s, None)
    t = service(FakeAsrEngine(result(ws))).transcribe("r1", audio(), qc())
    assert t.words[1].prob is None and t.words[0].prob == 0.9


@pytest.mark.parametrize("error", [RuntimeError("engine hỏng"), TimeoutError("quá hạn")])
def test_engine_error_or_timeout_is_asr_failed(error):
    """M03-TEST-003."""
    t = service(FakeAsrEngine(error=error)).transcribe("r1", audio(), qc())
    assert t.status is AsrStatus.ASR_FAILED and t.reasons == (ReasonCode.ASR_FAILED,)
    assert t.words == ()


@pytest.mark.parametrize(
    "ws",
    [
        [RawWord("a", -0.1, 0.2, 0.9)],
        [RawWord("a", 0.5, 0.4, 0.9)],
        [RawWord("a", 1.0, 1.2, 0.9), RawWord("b", 0.8, 1.3, 0.9)],
        [RawWord("a", 0.0, 61.0, 0.9)],
        [RawWord("a", 0.0, 0.2, 1.5)],
    ],
    ids=["start_am", "end_truoc_start", "khong_don_dieu", "vuot_duration", "prob_ngoai_khoang"],
)
def test_invalid_words_are_asr_failed_without_words(ws):
    """M03-TEST-004."""
    t = service(FakeAsrEngine(result(ws))).transcribe("r1", audio(60.0), qc())
    assert t.status is AsrStatus.ASR_FAILED and t.words == ()


def test_qc_reject_does_not_call_engine():
    """M03-TEST-005."""
    eng = FakeAsrEngine()
    loader = CountingLoader(eng)
    t = service(loader=loader).transcribe("r1", audio(), qc(QCStatus.REJECT))
    assert t.status is AsrStatus.NOT_RUN
    assert loader.calls == 0 and eng.calls == 0


def test_qc_review_still_runs_engine():
    t = service().transcribe("r1", audio(), qc(QCStatus.REVIEW))
    assert t.status is AsrStatus.OK


def test_missing_model_is_not_run_without_download():
    """M03-TEST-006: loader báo thiếu weight một lần, không thử tải."""
    loader = CountingLoader(unavailable=True)
    t = service(loader=loader).transcribe("r1", audio(), qc())
    assert t.status is AsrStatus.NOT_RUN and t.reasons == (ReasonCode.ASR_FAILED,)
    assert loader.calls == 1


def test_engine_is_loaded_once_and_reused():
    loader = CountingLoader(FakeAsrEngine())
    s = service(loader=loader)
    s.transcribe("r1", audio(), qc())
    s.transcribe("r2", audio(), qc())
    assert loader.calls == 1


@pytest.mark.parametrize(("ws", "text"), [([], ""), (raw_words(["a"]), "   ")])
def test_empty_transcript_is_unreliable(ws, text):
    """M03-TEST-007."""
    t = service(FakeAsrEngine(result(ws, text=text))).transcribe("r1", audio(), qc())
    assert t.status is AsrStatus.UNRELIABLE
    assert t.reasons == (ReasonCode.ASR_EMPTY_TRANSCRIPT,)


def test_hallucination_is_unreliable():
    ws = raw_words(["a", "b"] + ["okay"] * 7)
    t = service(FakeAsrEngine(result(ws, text="a b okay"))).transcribe("r1", audio(), qc())
    assert t.status is AsrStatus.UNRELIABLE and t.reasons == (ReasonCode.ASR_HALLUCINATION,)


def test_matching_weight_has_no_mismatch():
    """M03-TEST-013."""
    t = service().transcribe("r1", audio(), qc())
    assert t.asr_model == "whisper-small" and t.reasons == ()


def test_english_only_weight_is_mismatch_but_status_unchanged():
    """M03-TEST-014 (regression F-04)."""
    eng = FakeAsrEngine(weight="Systran/faster-whisper-small.en")
    t = service(eng).transcribe("r1", audio(), qc())
    assert t.asr_model is None
    assert t.reasons == (ReasonCode.ASR_VERSION_MISMATCH,) and t.status is AsrStatus.OK


def test_other_model_is_mismatch_but_status_unchanged():
    """M03-TEST-015."""
    s = AsrService(
        engine_loader=CountingLoader(FakeAsrEngine(weight="m")),
        trained_asr_model="whisper-small",
        weight_map={"m": "whisper-medium"},
    )
    t = s.transcribe("r1", audio(), qc())
    assert t.asr_model == "whisper-medium" and t.status is AsrStatus.OK
    assert t.reasons == (ReasonCode.ASR_VERSION_MISMATCH,)


def test_log_does_not_contain_transcript_text(caplog):
    """M03-TEST-016."""
    ws = raw_words(["SECRET-NAME-123", "says", "hello"])
    eng = FakeAsrEngine(result(ws, text="SECRET-NAME-123 says hello"))
    with caplog.at_level(logging.INFO, logger="aicefr.asr.service"):
        service(eng).transcribe("r1", audio(), qc())
    assert "SECRET-NAME-123" not in caplog.text
    assert "response_id=r1" in caplog.text and "status=OK" in caplog.text
