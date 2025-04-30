import pytest
from backend.utils.whisper import transcribe_audio


def test_transcribe_valid_audio():
    path = "tests/sample.wav"  # Use a real small audio file
    result = transcribe_audio(path)
    assert isinstance(result, str)
    assert len(result) > 0
