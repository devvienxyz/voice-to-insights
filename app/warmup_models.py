import whisper
from transformers import pipeline


def preload_whisper_model():
    print("Downloading Whisper model...")
    whisper.load_model("base")


def preload_transformers_model():
    print("Downloading Transformers summarization model...")
    pipeline("summarization", model="facebook/bart-large-cnn")


if __name__ == "__main__":
    preload_whisper_model()
    preload_transformers_model()
    print("✅ Model warm-up complete.")
