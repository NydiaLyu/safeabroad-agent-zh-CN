import re


def redact_text(text: str) -> str:
    text = re.sub(r"[\w\.-]+@[\w\.-]+", "[EMAIL]", text)
    text = re.sub(r"(?<![A-Za-z0-9-])\+?\d(?:[\d\s-]{7,}\d)(?![A-Za-z0-9-])", "[PHONE_OR_ID]", text)
    text = re.sub(r"\b[A-Z]\d{6,}\b", "[EVENT_OR_ID_NUMBER]", text)
    return text
