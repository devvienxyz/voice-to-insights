import logging
import streamlit as st
import queue
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from app import setup_pytorch  # noqa: F401
from app.core import handle_summarization, handle_transcription, process_audio_frames
from app.constants import APP_TITLE, AUDIO_RECEIVER_SIZE, MEDIA_STREAM_CONSTRAINTS, PAGE_TITLE, WEBRTC_KEY
from app.utils import initialize_session_state, set_styles

logger = logging.getLogger(__name__)


st.set_page_config(page_title=PAGE_TITLE, layout="centered")
st.title(APP_TITLE)

set_styles()

webrtc_ctx = webrtc_streamer(
    key=WEBRTC_KEY,
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=AUDIO_RECEIVER_SIZE,
    media_stream_constraints=MEDIA_STREAM_CONSTRAINTS,
)

transcription_box = st.empty()
summary_box = st.empty()


def main():
    initialize_session_state()

    while True:
        if webrtc_ctx.audio_receiver:
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                logger.warning("Queue is empty. Abort.")
                break

            processed_audio = process_audio_frames(audio_frames)
            handle_transcription(processed_audio, transcription_box)
            handle_summarization(summary_box)
        else:
            logger.warning("WebRTC is not running. Please start the stream.")
            logger.debug(f"WebRTC state: {webrtc_ctx.state}")
            break


if __name__ == "__main__":
    main()
