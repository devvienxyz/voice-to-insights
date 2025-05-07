import torch
import whisper
from transformers import pipeline

torch.set_num_threads(10)
torch.set_num_interop_threads(10)


def preload_whisper_model():
    print("Downloading Whisper model...")
    whisper.load_model("medium", device="cpu")


def preload_transformers_model():
    print("Downloading Transformers summarization model...")
    pipeline("summarization", model="facebook/bart-large-cnn")


if __name__ == "__main__":
    preload_whisper_model()
    preload_transformers_model()
    print("✅ Model warm-up complete.")
