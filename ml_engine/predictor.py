
import joblib
from pathlib import Path

from ml_engine.feature_extractor import (
    extract_url_features,
    FEATURE_COLUMNS
)


# ==========================================
# LOAD TRAINED MODEL
# ==========================================

ML_ENGINE_DIR = Path(__file__).resolve().parent

MODEL_PATH = ML_ENGINE_DIR / "model" / "random_forest_v3_group.pkl"

model_artifact = joblib.load(MODEL_PATH)

model = model_artifact["model"]
threshold = model_artifact["threshold"]
feature_columns = model_artifact["features"]


# ==========================================
# VALIDATE MODEL FEATURES
# ==========================================

# ==========================================
# VALIDATE MODEL FEATURES
# ==========================================

if set(feature_columns) != set(FEATURE_COLUMNS):
    raise ValueError(
        "Model and feature extractor are incompatible. "
        "Expected a model trained with all 21 V3 features."
    )

if 1 not in model.classes_:
    raise ValueError(
        "The loaded model does not contain phishing class label 1."
    )

phishing_class_index = list(model.classes_).index(1)


# ==========================================
# PREDICT URL
# ==========================================

def predict_url(url):

    # Extract all 21 V3 features
    features = extract_url_features(url)

    # Match the exact feature order used during model training
    features = features[feature_columns]

    # Get phishing probability
    probability = model.predict_proba(features)[0][phishing_class_index]

    # Apply saved threshold
    prediction = int(probability >= threshold)

    result = "Phishing" if prediction == 1 else "Legitimate"

    return {
        "url": url.strip(),
        "prediction": result,
        "phishing_probability": round(float(probability), 4),
        "threshold": float(threshold)
    }
