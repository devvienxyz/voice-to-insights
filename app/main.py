import setup_pytorch
import logging
import queue

import pydub
from streamlit_webrtc import WebRtcMode, webrtc_streamer
import streamlit as st
from utils import (
    ensure_recordings_dir_exists,
    process_audio_frames,
    update_sound_window_buffer,
    transcribe,
)

logger = logging.getLogger(__name__)


def setup_page():
    st.set_page_config(page_title="Audio Summarizer", layout="centered")
    st.title("🎤 Voice notes --> Summary + Action Items")


def main():
    ensure_recordings_dir_exists()

    webrtc_ctx = webrtc_streamer(
        key="sendonly-audio",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=4096,
        media_stream_constraints={"audio": True},
    )

    sound_window_buffer = None
    recording = pydub.AudioSegment.empty()

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
                text = transcribe(sound_window_buffer)
                logger.info(f"Transcription: {text}")
                st.text(text)

        else:
            break


if __name__ == "__main__":
    setup_page()
    main()
