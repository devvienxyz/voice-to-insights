import logging
import pydub.exceptions
import whisper
import tempfile
import numpy as np
import pydub
import threading
import queue
from transformers import pipeline
from constants import SOUND_WINDOW_LEN, TextSummarizationModels


logger = logging.getLogger(__name__)

TRANSCRIPTION_QUEUE = queue.Queue(maxsize=10)  # bounded to avoid memory bloat
whisper_model = whisper.load_model("base")  # tiny, base, small, medium, large


def process_audio_frames(audio_frames):
    """Process audio frames into a pydub AudioSegment."""
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


def update_sound_window_buffer(sound_window_buffer, sound_chunk):
    """Update the sound window buffer with the new sound chunk."""
    if sound_window_buffer is None:
        sound_window_buffer = pydub.AudioSegment.silent(duration=SOUND_WINDOW_LEN)

    try:
        sound_window_buffer = sound_window_buffer[-SOUND_WINDOW_LEN:] + sound_chunk
    except pydub.exceptions.TooManyMissingFrames:
        logger.warning("Too many missing frames in sound window buffer")
        # sound_window_buffer = pydub.AudioSegment.silent(duration=SOUND_WINDOW_LEN) + sound_chunk

    if len(sound_window_buffer) > SOUND_WINDOW_LEN:
        print("Sound window buffer too long, trimming")
        sound_window_buffer = sound_window_buffer[-SOUND_WINDOW_LEN:]

    return sound_window_buffer


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
