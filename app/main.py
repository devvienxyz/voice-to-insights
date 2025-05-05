import setup_pytorch
import logging
import queue

import pydub
from streamlit_webrtc import WebRtcMode, webrtc_streamer
import streamlit as st
from utils import (
    ensure_recordings_dir_exists,
    process_audio_frames,
    summarize,
    update_sound_window_buffer,
    transcribe,
)

logger = logging.getLogger(__name__)


def setup_webrtc_streamer():
    """Set up the WebRTC streamer."""
    return webrtc_streamer(
        key="sendonly-audio",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=4096,
        media_stream_constraints={"audio": True},
    )


def setup_page():
    st.set_page_config(page_title="Audio Summarizer", layout="centered")
    st.title("🎤 Voice -> Summary + Action Items")

    st.session_state.webrtc_ctx = setup_webrtc_streamer()

    if "transcription_placeholder" not in st.session_state:
        print("Initializing placeholders")
        st.session_state.transcription_placeholder, st.session_state.summary_placeholder = (
            create_layout()
        )
    else:
        create_layout()


def create_layout():
    """Create the layout for the Streamlit app."""
    col1, col2 = st.columns(2)

    with col1:
        st.header("Transcriptions")
        transcription_placeholder = st.empty()

    with col2:
        st.header("Summary")
        summary_placeholder = st.empty()

    return transcription_placeholder, summary_placeholder


def reset_placeholders():
    """Reset the placeholders and clear session state."""
    st.session_state.transcription_placeholder.empty()
    st.session_state.summary_placeholder.empty()
    st.session_state.transcription_placeholder, st.session_state.summary_placeholder = (
        create_layout()
    )


def process_audio_stream(webrtc_ctx):
    """Process the audio stream from the WebRTC context."""
    sound_window_buffer = None
    recording = pydub.AudioSegment.empty()
    st.session_state.transcribed_text = []
    st.session_state.summary_text = []

    while True:
        if webrtc_ctx.audio_receiver:
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                pass

            sound_chunk = process_audio_frames(audio_frames)

            if len(sound_chunk) > 0:
                sound_window_buffer = update_sound_window_buffer(sound_window_buffer, sound_chunk)
                recording += sound_chunk

                transcribed_text = transcribe(sound_window_buffer)
                st.session_state.transcribed_text.append(transcribed_text)
                st.session_state.transcription_placeholder.text(st.session_state.transcribed_text)

                summary_text = summarize(text=transcribed_text)
                st.session_state.summary_text.append(summary_text)
                st.session_state.summary_placeholder.text(st.session_state.summary_text)
        else:
            break


def main():
    print("\n\n\n\n\n")
    # print(st.session_state)
    print("\n\n\n\n\n")
    webrtc_ctx = st.session_state.webrtc_ctx
    process_audio_stream(webrtc_ctx)

    if webrtc_ctx.state == "STOPPED":  # Check if the recording is stopped
        if st.button("Start Over"):
            reset_placeholders()
            return


if __name__ == "__main__":
    setup_page()
    main()
