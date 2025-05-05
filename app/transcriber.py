import whisper
import tempfile
import torchaudio

class AudioTranscriber:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_bytes):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            result = self.model.transcribe(tmp.name)
        return result['text']
