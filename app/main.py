import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import numpy as np
from transcriber import AudioTranscriber
from summarizer import TextSummarizer
from io import BytesIO
import soundfile as sf

st.set_page_config(page_title="Audio Summarizer", layout="centered")

st.title("🎤 Audio to Summary + Action Items")

class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.audio = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray()
        self.audio.append(pcm)
        return frame

    def get_audio_bytes(self):
        if not self.audio:
            return None
        audio_np = np.concatenate(self.audio, axis=1)[0]
        buf = BytesIO()
        sf.write(buf, audio_np, samplerate=16000, format="WAV")
        return buf.getvalue()

def main():
    st.info("🎙️ Start speaking. When you're done, press Stop.")

    ctx = webrtc_streamer(
        key="audio",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if ctx.audio_processor and st.button("🔍 Transcribe & Summarize"):
        audio_bytes = ctx.audio_processor.get_audio_bytes()
        if audio_bytes:
            st.subheader("⏱️ Transcribing...")
            transcriber = AudioTranscriber()
            transcript = transcriber.transcribe(audio_bytes)

            st.success("📝 Transcription Complete")
            st.text_area("Transcript", transcript, height=200)

            st.subheader("🧠 Generating Summary & Action Items...")
            summarizer = TextSummarizer()
            summary, bullets = summarizer.summarize(transcript)

            st.success("📌 Summary Generated")
            st.markdown(f"**Summary:** {summary}")
            st.markdown("**Action Items:**")
            st.markdown("\n".join(bullets))
        else:
            st.warning("No audio captured.")

if __name__ == "__main__":
    main()
