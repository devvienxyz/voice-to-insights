from backend.utils.gpt import summarize_text


def test_summarize_output():
    transcript = "I need to follow up with John and submit the report."
    result = summarize_text(transcript)
    assert "summary" in result
    assert "actions" in result
    assert isinstance(result["actions"], list)
