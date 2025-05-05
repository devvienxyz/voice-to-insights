import streamlit as st
import requests
from io import BytesIO
from pydub import AudioSegment


class LLMVoiceApp:
    def __init__(self):
        self.backend_url = "http://localhost:10000/transcribe"
        self.audio_bytes = None
        self.transcript = None

    def run(self):
        st.set_page_config(page_title="LLM Voice App", layout="centered")
        st.title("🧠 Talk to an LLM")
        self.render_upload_section()
        self.render_recording_section()
        self.send_audio_to_backend()

    def render_upload_section(self):
        st.subheader("🎵 Upload Audio File")
        file = st.file_uploader("Upload WAV/MP3/OGG", type=["wav", "mp3", "ogg"])
        if file:
            st.audio(file)
            ext = file.name.split(".")[-1]
            audio = AudioSegment.from_file(BytesIO(file.read()), format=ext)
            buffer = BytesIO()
            audio.export(buffer, format="wav")
            buffer.seek(0)
            self.audio_bytes = buffer

    def render_recording_section(self):
        st.subheader("🎤 Or Record Audio")
        with st.expander("Use Microphone (Coming Soon)"):
            st.info("🎙️ Recording via mic not implemented yet.")
            # Future: Add streamlit-webrtc audio capture here

    def send_audio_to_backend(self):
        if self.audio_bytes and st.button("📤 Send to Backend"):
            st.info("Transcribing...")
            files = {"file": ("audio.wav", self.audio_bytes, "audio/wav")}
            res = requests.post(self.backend_url, files=files)
            if res.ok:
                self.transcript = res.json().get("text", "")
                st.success("📝 Transcription Complete")
                st.markdown(f"> {self.transcript}")
            else:
                st.error("❌ Transcription failed.")


if __name__ == "__main__":
    app = LLMVoiceApp()
    app.run()
