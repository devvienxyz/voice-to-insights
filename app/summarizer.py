from transformers import pipeline


class TextSummarizer:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

    def summarize(self, text: str):
        summary = self.summarizer(text, max_length=150, min_length=40, do_sample=False)[0][
            "summary_text"
        ]
        bullet_items = self._extract_bullet_points(summary)
        return summary, bullet_items

    def _extract_bullet_points(self, text: str):
        lines = text.split(". ")
        return [f"- {line.strip()}" for line in lines if line]
