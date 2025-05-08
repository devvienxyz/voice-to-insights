import av
import streamlit as st
from constants import RECORDINGS_DIR, SOUND_WINDOW_LEN
import pydub
import logging
from core import (
    process_audio_frames,
    queue_audio_for_transcription,
    update_sound_window_buffer,
    transcribe,
)
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def audio_processing_wrapper(transcription_col, summary_col):
    """Wrapper function to process audio frames and update the UI."""
    print("Audio processing wrapper initialized.")

    def process_audio(audio_frame: av.AudioFrame) -> av.AudioFrame:
        """Inner function to handle audio frames."""
        print("Audio frames received:", len(audio_frame))

        if audio_frame:
            print("Audio frames received:", len(audio_frame))
            sound_chunk = process_audio_frames(audio_frame)

            if len(sound_chunk) > 0:
                st.session_state.sound_window_buffer = update_sound_window_buffer(
                    st.session_state.sound_window_buffer, sound_chunk
                )

                if len(st.session_state.sound_window_buffer) >= SOUND_WINDOW_LEN:
                    queue_audio_for_transcription(st.session_state.sound_window_buffer)
                    st.session_state.sound_window_buffer = pydub.AudioSegment.silent(duration=0)

                transcribed_text = transcribe(st.session_state.sound_window_buffer)
                print("Transcribed Text Fragment:", transcribed_text)
                st.session_state.transcribed_text.append(transcribed_text)
                # transcription_col.text(" ".join(st.session_state.transcribed_text))
                transcription_col.write(
                    f"<div style='white-space: pre-wrap;'>{transcribed_text}</div>",
                    unsafe_allow_html=True,
                )

                # Example of when to trigger summarization (you might need a different logic)
                # if len(st.session_state.transcribed_text) % 5 == 0 and st.session_state.transcribed_text:
                #     full_text = " ".join(st.session_state.transcribed_text)
                #     summary = summarize(text=full_text)
                #     st.session_state.summary_text.append(summary)
                #     if st.session_state.summary_col:
                #         st.session_state.summary_col.text("\n".join(st.session_state.summary_text))
        else:
            st.write("No audio frames received.")

    return process_audio


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
