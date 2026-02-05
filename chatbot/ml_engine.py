# chatbot/ml_engine.py

HIGH_WORDS = [
    "urgent", "emergency", "danger", "fire", "accident",
    "attack", "fraud", "critical", "immediately", "hospital"
]

MEDIUM_WORDS = [
    "delay", "not working", "issue", "problem",
    "complaint", "error", "failed"
]


def predict_priority(text):
    text = text.lower()

    for w in HIGH_WORDS:
        if w in text:
            return "High"

    for w in MEDIUM_WORDS:
        if w in text:
            return "Medium"

    return "Low"
