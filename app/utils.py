"""A sample to use WebRTC in sendonly mode to transfer audio frames
from the browser to the server and visualize them with matplotlib
and `st.pyplot`."""

import logging
import os
import queue
from datetime import datetime
import torch
import torchaudio
import whisper
import tempfile

import warnings

warnings.filterwarnings("ignore", message="Tried to instantiate class '__path__._path'")

import pydub
from streamlit_webrtc import WebRtcMode, webrtc_streamer

logger = logging.getLogger(__name__)

RECORDINGS_DIR = "recordings"
SOUND_WINDOW_LEN = 5000  # 5 seconds

whisper_model = whisper.load_model("base")  # tiny, base, small, medium, large


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
        audio_tensor, sr = torchaudio.load(tmpfile.name)
        audio_tensor = torchaudio.functional.resample(audio_tensor, orig_freq=sr, new_freq=16000)
        audio_np = audio_tensor.squeeze().numpy()
        result = whisper_model.transcribe(
            audio_np, fp16=torch.cuda.is_available(), language=language
        )
        print("\n\n\nRaw Whisper Result: \n")
        print(type(result))
        print(result)
        return result["text"]
