
import joblib
from pathlib import Path

from ml_engine.feature_extractor import extract_url_features


# ==========================================
# LOAD TRAINED MODEL
# ==========================================

ML_ENGINE_DIR = Path(__file__).resolve().parent

MODEL_PATH = ML_ENGINE_DIR / "model" / "random_forest.pkl"

model_artifact = joblib.load(MODEL_PATH)

model = model_artifact["model"]
threshold = model_artifact["threshold"]
feature_columns = model_artifact["features"]


# ==========================================
# PREDICT URL
# ==========================================

def predict_url(url):

    # Extract features from URL
    features = extract_url_features(url)

    # Ensure the same feature order as training
    features = features[feature_columns]

    # Get phishing probability
    probability = model.predict_proba(features)[0][1]

    # Apply saved threshold
    prediction = int(probability >= threshold)

    if prediction == 1:
        result = "Phishing"
    else:
        result = "Legitimate"

    return {
        "url": url,
        "prediction": result,
        "phishing_probability": round(float(probability), 4),
        "threshold": float(threshold)
    }
