import pandas as pd
import pickle
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

print("Training complaint priority model...")

data = {
    "text": [
        "water leakage emergency",
        "transformer blast urgent",
        "road accident danger",

        "streetlight not working",
        "water supply irregular",
        "pothole issue",

        "garbage collection delay",
        "park cleaning required",
        "minor noise complaint"
    ],
    "priority": [
        "High","High","High",
        "Medium","Medium","Medium",
        "Low","Low","Low"
    ]
}

df = pd.DataFrame(data)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["text"])

model = LogisticRegression()
model.fit(X, df["priority"])

MODEL_PATH = os.path.join(os.path.dirname(__file__), "priority_model.pkl")

with open(MODEL_PATH, "wb") as f:
    pickle.dump((model, vectorizer), f)

print("✅ Model saved:", MODEL_PATH)
print("DONE")
