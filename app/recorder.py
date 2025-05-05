"""A sample to use WebRTC in sendonly mode to transfer audio frames
from the browser to the server and visualize them with matplotlib
and `st.pyplot`."""
import setup_pytorch
import logging
import queue

import pydub
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from utils import (
    ensure_recordings_dir_exists,
    process_audio_frames,
    update_sound_window_buffer,
    transcribe,
)

logger = logging.getLogger(__name__)


def main():
    """Main function to handle audio streaming and recording."""
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
                logger.warning("Queue is empty. Saving recording and aborting.")
                # save_recording(recording)
                # break

            sound_chunk = process_audio_frames(audio_frames)

            if len(sound_chunk) > 0:
                sound_window_buffer = update_sound_window_buffer(sound_window_buffer, sound_chunk)
                recording += sound_chunk
                # transcribe(sound_window_buffer)

                text = transcribe(sound_window_buffer)
                logger.info(f"Transcription: {text}")

        else:
            # pass
            # logger.warning("AudioReceiver is not set. Saving recording and aborting.")
            # save_recording(recording)
            break


if __name__ == "__main__":
    main()
