import logging
import whisper
import tempfile
import numpy as np
import pydub
import threading
import queue
import streamlit as st
from transformers import pipeline
from app.constants import TextSummarizationModels


logger = logging.getLogger(__name__)

TRANSCRIPTION_QUEUE: queue.Queue = queue.Queue(maxsize=10)  # bounded to avoid memory bloat
whisper_model = whisper.load_model("base")  # tiny, base, small, medium, large


def process_audio_frames(audio_frames, sound_window_buffer, sound_window_len):
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

    return sound_window_buffer


def handle_transcription(sound_window_buffer, transcription_col):
    if sound_window_buffer:
        transcribed_text = transcribe(sound_window_buffer)
        print("Transcribed Text Fragment:", transcribed_text)
        transcription_col.write(transcribed_text)
    else:
        st.write("No audio frames received.")


def transcribe(audio_segment, language="en"):
    """Transcribe a pydub.AudioSegment using Whisper."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmpfile:
        audio_segment.export(tmpfile.name, format="wav")
        audio = whisper.load_audio(tmpfile.name)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(whisper_model.device)

        # Silent check
        if np.max(np.abs(audio)) < 1e-3:
            logger.debug("Silent or too quiet audio")
            return ""

        options = whisper.DecodingOptions(language=language, fp16=False)
        result = whisper_model.decode(mel, options)
        return result.text.strip()


def extract_bullet_points(text: str):
    lines = text.split(". ")
    return [f"- {line.strip()}" for line in lines if line]


def summarize(text: str, model=TextSummarizationModels.default.value):
    if len(text.strip().split()) < 20:
        print("\n\nToo short!!!   :")
        print(text)
        return text

    summarizer = pipeline("summarization", model=model)
    summary = summarizer(text, max_length=150, min_length=40, do_sample=False)[0]["summary_text"]
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
