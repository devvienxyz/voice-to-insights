from unittest import mock
from io import BytesIO
from app import core


def test_extract_bullet_points():
    text = "This is a sentence. Another point here. Final one."
    bullets = core.extract_bullet_points(text)
    assert bullets == ["This is a sentence", "Another point here", "Final one"]


@mock.patch("app.core.pipeline")
def test_summarize_short_text(mock_pipeline):
    short_text = "Too short for meaningful summarization."
    summary, bullets = core.summarize(short_text)
    assert summary == short_text
    assert bullets == []


@mock.patch("app.core.pipeline")
def test_summarize_long_text(mock_pipeline):
    mock_pipeline.return_value.return_value = [{"summary_text": "This is a summary. With two bullet points."}]
    text = "This is a long enough input " * 10
    summary, bullets = core.summarize(text)
    assert "This is a summary" in summary
    assert len(bullets) == 2


@mock.patch("app.core.whisper")
@mock.patch("app.core.decode_lock", mock.MagicMock())
def test_transcribe_silent_audio(mock_whisper, dummy_audio):
    dummy_wav = BytesIO()
    dummy_audio.export(dummy_wav, format="wav")
    dummy_wav.seek(0)

    mock_whisper.load_audio.return_value = [0.0] * 16000
    mock_whisper.pad_or_trim.return_value = [0.0] * 16000
    mock_whisper.log_mel_spectrogram.return_value.to.return_value = mock.MagicMock(shape=(80, 0))
    mock_whisper.DecodingOptions.return_value = mock.MagicMock()

    core.whisper_model = mock.MagicMock()
    result = core.transcribe(dummy_audio)
    assert result == "" or isinstance(result, dict)  # Can be "" or {"text": "", ...}


@mock.patch("app.core.whisper")
@mock.patch("app.core.decode_lock", mock.MagicMock())
def test_transcribe_valid_audio(mock_whisper, dummy_audio):
    dummy_wav = BytesIO()
    dummy_audio.export(dummy_wav, format="wav")
    dummy_wav.seek(0)

    mock_whisper.load_audio.return_value = [0.1] * 16000
    mock_whisper.pad_or_trim.return_value = [0.1] * 16000
    mock_whisper.log_mel_spectrogram.return_value.to.return_value = mock.MagicMock(shape=(80, 300))
    mock_whisper.DecodingOptions.return_value = mock.MagicMock()

    mock_result = mock.MagicMock()
    mock_result.text = "Hello world"
    mock_result.no_speech_prob = 0.2
    core.whisper_model.decode.return_value = mock_result

    core.whisper_model = mock.MagicMock(decode=mock.MagicMock(return_value=mock_result))
    result = core.transcribe(dummy_audio)
    assert result == "Hello world"
