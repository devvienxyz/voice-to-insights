from enum import Enum


class TextSummarizationModels(Enum):
    default = "sshleifer/distilbart-cnn-12-6"



RECORDINGS_DIR = "recordings"
SOUND_WINDOW_LEN = 5000  # 5 seconds

# --- Configuration ---
AUDIO_RECEIVER_SIZE = 4096
MEDIA_STREAM_CONSTRAINTS = {"audio": True}
WEBRTC_KEY = "sendonly-audio"
PAGE_TITLE = "Audio Summarizer"
APP_TITLE = "🎤 Voice -> Summary + Action Items"
