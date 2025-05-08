import streamlit as st
from constants import RECORDINGS_DIR
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def reset_placeholders_and_state(webrtc_ctx, transcription_col, summary_col):
    """Resets the UI placeholders and relevant session state."""
    transcription_col.empty()
    summary_col.empty()
    st.session_state.transcribed_text = []
    st.session_state.summary_text = []
    st.session_state.sound_window_buffer.clear()
    webrtc_ctx.reset()


def save_recording(recording):
    """Save the recording to a file."""
    if len(recording) > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(RECORDINGS_DIR, f"recording_{timestamp}.wav")
        recording.set_frame_rate(44100).export(file_path, format="wav")
        logger.info(f"Recording saved to {file_path}")
