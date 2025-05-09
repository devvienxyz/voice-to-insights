import logging
import whisper
import tempfile
import numpy as np
import pydub
import threading
import queue
import streamlit as st
from threading import Lock
from transformers import pipeline
from app.constants import TextSummarizationModels

# Thread lock to prevent concurrent decode corruption (esp. in Streamlit)
decode_lock = Lock()
logger = logging.getLogger(__name__)

TRANSCRIPTION_QUEUE: queue.Queue = queue.Queue(maxsize=10)  # bounded to avoid memory bloat
whisper_model = whisper.load_model("base")  # tiny, base, small, medium, large


def process_audio_frames(audio_frames):
    sound_chunk = pydub.AudioSegment.empty()

    for audio_frame in audio_frames:
        sound = pydub.AudioSegment(
            data=audio_frame.to_ndarray().tobytes(),
            sample_width=audio_frame.format.bytes,
            frame_rate=audio_frame.sample_rate,
            channels=len(audio_frame.layout.channels),
        )
        sound_chunk += sound

    return sound_chunk


def handle_transcription(processed_audio, transcription_box):
    if processed_audio:
        transcribed_text = transcribe(processed_audio)

        st.session_state.transcriptions.append(transcribed_text)

        transcription_html = "<br>".join(st.session_state.transcriptions)
        transcription_box.markdown("#### Transcriptions")
        transcription_box.markdown(f'<div class="output-box">{transcription_html}</div>', unsafe_allow_html=True)

    else:
        st.write("No audio frames received.")


def handle_summarization(summary_box):
    full_transcription = " ".join(st.session_state.transcriptions)
    summaries, bullets = summarize(full_transcription)

    st.session_state.summaries.append(summaries)
    st.session_state.bullet_points.append(bullets)

    flat_bullets = st.session_state.bullet_points[-1] if st.session_state.bullet_points else []

    summary_html = "" if not st.session_state.summaries else st.session_state.summaries[-1]
    bullets_html = "".join(f"<li>{item}</li>" for item in flat_bullets)

    full_html = f"""
    <div class="output-box">
        <p>{summary_html}</p>
        <ul>{bullets_html}</p>
    </div>
    """

    summary_box.markdown("#### Summary", unsafe_allow_html=True)
    summary_box.markdown(full_html, unsafe_allow_html=True)


def transcribe(processed_audio, language="en"):
    """Transcribe a pydub.AudioSegment using Whisper."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmpfile:
        processed_audio.export(tmpfile.name, format="wav")
        audio = whisper.load_audio(tmpfile.name)
        audio = whisper.pad_or_trim(audio)

        # Silent check
        if np.max(np.abs(audio)) < 1e-3:
            logger.debug("Silent or too quiet audio")
            return ""

        mel = whisper.log_mel_spectrogram(audio).to(whisper_model.device)

        # Sanity check to avoid decoding empty input
        if mel.shape[-1] == 0:
            return {"text": "", "error": "Empty or invalid audio input."}

        options = whisper.DecodingOptions(language=language, fp16=False)

        with decode_lock:
            result = whisper_model.decode(mel, options)

        return result.text.strip()


def extract_bullet_points(text: str):
    lines = text.split(". ")
    return [f"- {line.strip()}" for line in lines if line]


def summarize(text: str, model=TextSummarizationModels.default.value):
    words = text.strip().split()

    if len(words) < 20:
        logger.debug(f"Text too short for summarization. Text: {text}")
        return text, []

    summarizer = pipeline("summarization", model=model)
    input_len = len(words)
    max_len = min(150, int(input_len * 0.7))  # 70% of input as a cap
    min_len = min(40, max_len - 10)  # avoid hitting max directly

    summary = summarizer(text, max_length=max_len, min_length=min_len, do_sample=False)[0]["summary_text"]

    bullet_items = extract_bullet_points(summary)
    return summary, bullet_items


def start_transcription_worker(callback):
    def worker():
        while True:
            audio_segment = TRANSCRIPTION_QUEUE.get()
            try:
                text = transcribe(audio_segment)
                if text:
                    callback(text)  # push transcription to main app/GUI/log
            except Exception as e:
                logger.exception("Transcription failed: %s", e)
            finally:
                TRANSCRIPTION_QUEUE.task_done()

    t = threading.Thread(target=worker, daemon=True)
    t.start()


def queue_audio_for_transcription(audio_segment):
    """Push audio to transcription queue. Drops if queue is full."""
    try:
        TRANSCRIPTION_QUEUE.put_nowait(audio_segment)
    except queue.Full:
        logger.warning("Dropped audio chunk due to queue overflow")
