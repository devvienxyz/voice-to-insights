import streamlit as st
import requests

API_BASE = "http://localhost:8000"  # Change if deployed

st.title("🎙️ Voice-to-Insight Tool")
st.markdown("Upload a voice note to get a summary and action items.")

# Upload audio
audio_file = st.file_uploader("Upload audio (.mp3 or .wav)", type=["mp3", "wav"])

if audio_file:
    with st.spinner("Transcribing..."):
        # Transcribe
        files = {"file": audio_file.getvalue()}
        res = requests.post(f"{API_BASE}/transcribe", files=files)
        if res.status_code != 200:
            st.error("Transcription failed.")
        else:
            transcript = res.json().get("transcript", "")
            st.subheader("📜 Transcript")
            st.text(transcript)

            # Summarize
            with st.spinner("Summarizing..."):
                payload = {"transcript": transcript}
                res2 = requests.post(f"{API_BASE}/summarize", json=payload)
                if res2.status_code != 200:
                    st.error("Summarization failed.")
                else:
                    data = res2.json()
                    st.subheader("📝 Summary")
                    st.write(data.get("summary", "N/A"))

                    st.subheader("✅ Action Items")
                    for item in data.get("actions", []):
                        st.markdown(f"- {item}")
