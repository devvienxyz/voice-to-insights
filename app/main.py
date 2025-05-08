import logging
import streamlit as st
import queue
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from app import setup_pytorch  # noqa: F401
from app.core import handle_transcription, process_audio_frames
from app.constants import APP_TITLE, AUDIO_RECEIVER_SIZE, MEDIA_STREAM_CONSTRAINTS, PAGE_TITLE, WEBRTC_KEY

logger = logging.getLogger(__name__)

# --- State Initialization ---
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = []
if "summary_text" not in st.session_state:
    st.session_state.summary_text = []

st.set_page_config(page_title=PAGE_TITLE, layout="centered")
st.title(APP_TITLE)

webrtc_ctx = webrtc_streamer(
    key=WEBRTC_KEY,
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=AUDIO_RECEIVER_SIZE,
    media_stream_constraints=MEDIA_STREAM_CONSTRAINTS,
)

col1, col2 = st.columns(2)

with col1:
    st.header("Transcriptions")
    transcription_col = st.empty()
with col2:
    st.header("Summary")
    summary_col = st.empty()


def main():
    sound_window_len = 5000  # 5s
    sound_window_buffer = None

    while True:
        if webrtc_ctx.audio_receiver:
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                logger.warning("Queue is empty. Abort.")
                break

            sound_window_buffer = process_audio_frames(audio_frames, sound_window_buffer, sound_window_len)
            handle_transcription(sound_window_buffer, transcription_col)

        else:
            logger.warning("WebRTC is not running. Please start the stream.")
            logger.debug(f"WebRTC state: {webrtc_ctx.state}")
            break


if __name__ == "__main__":
    main()
