import pytest
from unittest import mock
import numpy as np
from pydub import AudioSegment


@pytest.fixture
def mock_audio_frame():
    def _make_mock_frame(duration_ms=1000):
        mock_frame = mock.Mock()
        sample_rate = 44100
        sample_width = 2
        num_samples = int(sample_rate * duration_ms / 1000)
        mock_array = np.zeros(num_samples, dtype=np.int16)
        mock_frame.to_ndarray.return_value = mock_array
        mock_frame.format = mock.Mock()
        mock_frame.format.bytes = sample_width
        mock_frame.sample_rate = sample_rate
        mock_frame.layout = mock.Mock()
        mock_frame.layout.channels = [0, 1]
        return mock_frame

    return _make_mock_frame


@pytest.fixture
def default_sound_window_len():
    return 5000


@pytest.fixture
def initial_sound_window_buffer():
    return AudioSegment.silent(duration=3000)
