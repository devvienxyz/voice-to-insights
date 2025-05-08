import pytest
from pydub import AudioSegment
from app.core import process_audio_frames


@pytest.mark.unit
def test_process_audio_frames_with_empty_audio_frames():
    sound_window_buffer = None
    sound_window_len = 5000  # 5 seconds
    audio_frames = []

    result = process_audio_frames(audio_frames, sound_window_buffer, sound_window_len)

    assert result is None, "Expected sound_window_buffer to remain None when no audio frames are provided."


@pytest.mark.unit
def test_process_audio_frames_with_audio_frames():
    sound_window_buffer = None
    sound_window_len = 5000  # 5 seconds
    audio_frame = AudioSegment.silent(duration=1000)  # 1 second of silence
    audio_frames = [audio_frame]

    result = process_audio_frames(audio_frames, sound_window_buffer, sound_window_len)

    assert result is not None, "Expected sound_window_buffer to be initialized."
    assert len(result) == 1000, "Expected sound_window_buffer to contain 1 second of audio."


@pytest.mark.unit
def test_process_audio_frames_with_existing_buffer():
    sound_window_buffer = AudioSegment.silent(duration=3000)  # 3 seconds of silence
    sound_window_len = 5000  # 5 seconds
    audio_frame = AudioSegment.silent(duration=3000)  # 3 seconds of silence
    audio_frames = [audio_frame]

    result = process_audio_frames(audio_frames, sound_window_buffer, sound_window_len)

    assert result is not None, "Expected sound_window_buffer to remain initialized."
    assert len(result) == 5000, "Expected sound_window_buffer to be trimmed to 5 seconds."


@pytest.mark.unit
def test_process_audio_frames_with_buffer_exceeding_limit():
    sound_window_buffer = AudioSegment.silent(duration=5000)  # 5 seconds of silence
    sound_window_len = 5000  # 5 seconds
    audio_frame = AudioSegment.silent(duration=3000)  # 3 seconds of silence
    audio_frames = [audio_frame]

    result = process_audio_frames(audio_frames, sound_window_buffer, sound_window_len)

    assert result is not None, "Expected sound_window_buffer to remain initialized."
    assert len(result) == 5000, "Expected sound_window_buffer to be trimmed to 5 seconds."
