
"""PhishGuard - Final V3 Random Forest training.

Trains the V3 Random Forest using the existing group-isolated
training split and saves a separate model artifact.

Run from project root:
    python ml_engine/train_final_v3.py

Does NOT overwrite the existing V1 model.
"""

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)

from feature_extractor import FEATURE_COLUMNS


# ==========================================
# CONFIGURATION
# ==========================================

ML_ENGINE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ML_ENGINE_DIR.parent

DATA_DIR = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "group_comparisons"
)

MODEL_DIR = ML_ENGINE_DIR / "model"

TRAIN_PATH = DATA_DIR / "train_features_v3.csv"
TEST_PATH = DATA_DIR / "test_features_v3.csv"
METADATA_PATH = DATA_DIR / "group_split_metadata.json"

MODEL_PATH = MODEL_DIR / "random_forest_v3_group.pkl"

RANDOM_STATE = 42
THRESHOLD = 0.50


# ==========================================
# LOAD AND VALIDATE DATA
# ==========================================

def load_data():

    for path in [TRAIN_PATH, TEST_PATH, METADATA_PATH]:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    metadata = json.loads(
        METADATA_PATH.read_text(encoding="utf-8")
    )

    if metadata.get("group_overlap_count") != 0:
        raise ValueError("Group overlap detected. Training aborted.")

    if "Label" not in train_df.columns or "Label" not in test_df.columns:
        raise ValueError("Label column is missing.")

    train_features = [
        column for column in train_df.columns if column != "Label"
    ]

    test_features = [
        column for column in test_df.columns if column != "Label"
    ]

    if set(train_features) != set(FEATURE_COLUMNS):
        raise ValueError("Training dataset does not contain exactly the 21 V3 features.")

    if set(test_features) != set(FEATURE_COLUMNS):
        raise ValueError("Test dataset does not contain exactly the 21 V3 features.")

    if train_df.empty or test_df.empty:
        raise ValueError("Training or test dataset is empty.")

    if train_df.isnull().any().any() or test_df.isnull().any().any():
        raise ValueError("Missing values detected in dataset.")

    label_map = {"good": 0, "bad": 1}

    y_train_raw = train_df["Label"].astype(str).str.strip().str.lower()
    y_test_raw = test_df["Label"].astype(str).str.strip().str.lower()

    unexpected = (
        set(y_train_raw.unique()) | set(y_test_raw.unique())
    ) - set(label_map)

    if unexpected:
        raise ValueError(f"Unexpected labels found: {unexpected}")

    X_train = train_df[FEATURE_COLUMNS]
    X_test = test_df[FEATURE_COLUMNS]

    y_train = y_train_raw.map(label_map).astype(int)
    y_test = y_test_raw.map(label_map).astype(int)

    if set(y_train.unique()) != {0, 1}:
        raise ValueError("Both classes must exist in training data.")

    if set(y_test.unique()) != {0, 1}:
        raise ValueError("Both classes must exist in test data.")

    if not all(np.issubdtype(dtype, np.number) for dtype in X_train.dtypes):
        raise ValueError("Non-numeric training features detected.")

    print("Dataset validation successful.")
    print("Training shape:", X_train.shape)
    print("Testing shape:", X_test.shape)
    print("Training labels:", y_train.value_counts().sort_index().to_dict())
    print("Testing labels:", y_test.value_counts().sort_index().to_dict())

    return X_train, X_test, y_train, y_test, metadata


# ==========================================
# TRAIN FINAL V3 RANDOM FOREST
# ==========================================

def train_model(X_train, y_train):

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=30,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features="sqrt",
        class_weight="balanced_subsample",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    print("\nTraining V3 Random Forest...")

    model.fit(X_train, y_train)

    print("Training completed.")

    return model


# ==========================================
# EVALUATE ON GROUP-ISOLATED TEST SET
# ==========================================

def evaluate_model(model, X_test, y_test):

    class_positions = np.where(model.classes_ == 1)[0]

    if len(class_positions) != 1:
        raise ValueError("Phishing class 1 not found.")

    phishing_index = int(class_positions[0])

    probabilities = model.predict_proba(X_test)[:, phishing_index]

    predictions = (probabilities >= THRESHOLD).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1]
    ).ravel()

    metrics = {
        "threshold": THRESHOLD,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "average_precision": float(average_precision_score(y_test, probabilities)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }

    print("\nV3 RANDOM FOREST TEST RESULTS")
    print("-" * 45)

    for key, value in metrics.items():
        print(f"{key}: {value}")

    return metrics


# ==========================================
# SAVE MODEL ARTIFACT
# ==========================================

def save_model(model, metadata, metrics):

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    model_artifact = {
        "model": model,
        "threshold": THRESHOLD,
        "features": FEATURE_COLUMNS.copy(),
        "model_name": "Random Forest",
        "dataset_version": "V3",
        "split_method": metadata.get("method"),
        "random_state": RANDOM_STATE,
        "test_metrics": metrics,
    }

    joblib.dump(model_artifact, MODEL_PATH)

    print("\nModel artifact saved successfully:")
    print(MODEL_PATH)


# ==========================================
# MAIN
# ==========================================

def main():

    X_train, X_test, y_train, y_test, metadata = load_data()

    model = train_model(X_train, y_train)

    metrics = evaluate_model(model, X_test, y_test)

    save_model(model, metadata, metrics)

    print("\nFINAL V3 TRAINING COMPLETED.")


if __name__ == "__main__":
    main()
