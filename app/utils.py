import streamlit as st
import logging
import os
from datetime import datetime
from app.constants import RECORDINGS_DIR

logger = logging.getLogger(__name__)


def save_recording(recording):
    """Save the recording to a file."""
    if len(recording) > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(RECORDINGS_DIR, f"recording_{timestamp}.wav")
        recording.set_frame_rate(44100).export(file_path, format="wav")
        logger.info(f"Recording saved to {file_path}")


def initialize_session_state():
    """Initialize session state variables."""
    if "transcribed_text" not in st.session_state:
        st.session_state.transcriptions = []

    if "summary_text" not in st.session_state:
        st.session_state.summaries = []

    if "bullet_points" not in st.session_state:
        st.session_state.bullet_points = []


def set_styles():
    st.markdown(
        """
        <style>
        .output-box {
            height: 200px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            background-color: transparent;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
