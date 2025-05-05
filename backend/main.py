from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.utils.whisper import transcribe_audio
from backend.utils.gpt import summarize_text
import tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    text = transcribe_audio(tmp_path)
    return {"transcript": text}


@app.post("/summarize")
def summarize(payload: dict):
    transcript = payload.get("transcript", "")
    result = summarize_text(transcript)
    return result


@app.get("/health")
def health_check():
    return {"status": "ok"}
