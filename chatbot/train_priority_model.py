import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

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

save_path = os.path.join(os.path.dirname(__file__), "priority_model.pkl")
joblib.dump((model, vectorizer), save_path)

print("✅ Model saved at:", save_path)
