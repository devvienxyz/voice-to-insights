import whisper

model = whisper.load_model("base")  # Use "tiny" if low spec

def transcribe_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path)
    return result["text"]
