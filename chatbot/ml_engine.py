import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "priority_model.pkl")

model = None
vectorizer = None

try:
    if os.path.exists(MODEL_PATH):
        model, vectorizer = joblib.load(MODEL_PATH)
        print("✅ ML model loaded")
    else:
        print("⚠️ Model file not found")
except Exception as e:
    print("⚠️ Model load failed:", e)
    model = None
    vectorizer = None


def predict_priority(text):
    if model and vectorizer:
        X = vectorizer.transform([text])
        return model.predict(X)[0]

    # fallback rule-based
    text = text.lower()
    if "emergency" in text or "urgent" in text:
        return "High"
    elif "not working" in text or "delay" in text:
        return "Medium"
    return "Low"
