import pytest
from pydub import AudioSegment


@pytest.fixture
def dummy_audio():
    # Generate 1 second of silent audio
    return AudioSegment.silent(duration=1000)
