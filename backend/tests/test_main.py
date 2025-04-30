from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_transcribe_endpoint():
    with open("tests/sample.wav", "rb") as f:
        response = client.post("/transcribe", files={"file": f})
    assert response.status_code == 200
    assert "transcript" in response.json()


def test_summarize_endpoint():
    payload = {"transcript": "Email Sarah and pay the invoice by Friday."}
    response = client.post("/summarize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert isinstance(data.get("actions", []), list)
