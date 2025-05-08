import setup_pytorch  # noqa: F401
import logging
import pydub
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from core import transcribe
from constants import APP_TITLE, AUDIO_RECEIVER_SIZE, MEDIA_STREAM_CONSTRAINTS, PAGE_TITLE, WEBRTC_KEY
import queue

logger = logging.getLogger(__name__)

# --- State Initialization ---
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = []
if "summary_text" not in st.session_state:
    st.session_state.summary_text = []
if "sound_window_buffer" not in st.session_state:
    st.session_state.sound_window_buffer = pydub.AudioSegment.silent(duration=0)


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

            sound_chunk = pydub.AudioSegment.empty()

            for audio_frame in audio_frames:
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound

            if len(sound_chunk) > 0:
                if sound_window_buffer is None:
                    sound_window_buffer = pydub.AudioSegment.silent(duration=sound_window_len)

                sound_window_buffer += sound_chunk
                if len(sound_window_buffer) > sound_window_len:
                    sound_window_buffer = sound_window_buffer[-sound_window_len:]

            if sound_window_buffer:
                transcribed_text = transcribe(sound_window_buffer)
                print("Transcribed Text Fragment:", transcribed_text)
                transcription_col.write(transcribed_text)
            else:
                st.write("No audio frames received.")

        else:
            logger.warning("WebRTC is not running. Please start the stream.")
            logger.debug(f"WebRTC state: {webrtc_ctx.state}")
            break


if __name__ == "__main__":
    main()
