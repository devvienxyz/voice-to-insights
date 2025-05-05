import warnings

warnings.filterwarnings("ignore", message="Tried to instantiate class '__path__._path'")

import logging
import os
from datetime import datetime
import torch
import whisper
import tempfile
import numpy as np
import pydub


logger = logging.getLogger(__name__)

RECORDINGS_DIR = "recordings"
SOUND_WINDOW_LEN = 5000  # 5 seconds

whisper_model = whisper.load_model("base")  # tiny, base, small, medium, large
# torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)]
torch.classes.__path__ = []


def ensure_recordings_dir_exists():
    """Ensure the recordings directory exists."""
    os.makedirs(RECORDINGS_DIR, exist_ok=True)


def save_recording(recording):
    """Save the recording to a file."""
    if len(recording) > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(RECORDINGS_DIR, f"recording_{timestamp}.wav")
        recording.set_frame_rate(44100).export(file_path, format="wav")
        logger.info(f"Recording saved to {file_path}")


def process_audio_frames(audio_frames):
    """Process audio frames into a pydub AudioSegment."""
    sound_chunk = pydub.AudioSegment.empty()
    for audio_frame in audio_frames:
        sound = pydub.AudioSegment(
            data=audio_frame.to_ndarray().tobytes(),
            sample_width=audio_frame.format.bytes,
            frame_rate=audio_frame.sample_rate,
            channels=len(audio_frame.layout.channels),
        )
        sound_chunk += sound
    return sound_chunk


def update_sound_window_buffer(sound_window_buffer, sound_chunk):
    """Update the sound window buffer with the new sound chunk."""
    if sound_window_buffer is None:
        sound_window_buffer = pydub.AudioSegment.silent(duration=SOUND_WINDOW_LEN)

    sound_window_buffer = sound_window_buffer[-SOUND_WINDOW_LEN:] + sound_chunk
    if len(sound_window_buffer) > SOUND_WINDOW_LEN:
        sound_window_buffer = sound_window_buffer[-SOUND_WINDOW_LEN:]

    return sound_window_buffer


def transcribe(audio_segment, language="en"):
    """Transcribe a pydub.AudioSegment using Whisper."""

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmpfile:
        audio_segment.export(tmpfile.name, format="wav")
        audio_tensor = whisper.audio.load_audio(tmpfile.name)

        # Check if the audio is silent (no meaningful content)
        if np.max(np.abs(audio_tensor)) < 1e-3:
            print("Warning: The audio is silent or too quiet to transcribe.")
            return []

        result = whisper_model.transcribe(audio_tensor, fp16=False, language=language)
        return result["text"]
