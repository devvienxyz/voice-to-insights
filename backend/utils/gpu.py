import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_text(transcript: str) -> dict:
    prompt = f"""
You are a productivity assistant. Summarize the following transcript and list all action items clearly.

Transcript:
\"\"\"{transcript}\"\"\"

Return format:
Summary: <text>
Action Items:
- item 1
- item 2
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    
    content = response['choices'][0]['message']['content']
    
    # crude split (robust parsing would use regex)
    parts = content.split("Action Items:")
    summary = parts[0].replace("Summary:", "").strip()
    actions = [a.strip("- ").strip() for a in parts[1].strip().split("\n") if a.strip()]
    
    return {"summary": summary, "actions": actions}
