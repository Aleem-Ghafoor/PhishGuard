"""
PhishGuard - Phase 2 controlled model comparison

Compares V1, V2 and V3 using identical train/test row splits.
Labels are explicitly encoded as: good -> 0, bad -> 1.

Run from the project root:
    python ml_engine/train_comparison.py

The test set is held out until final evaluation. Threshold selection is
performed only on a validation split carved out of the training data.
"""

from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    classification_report,
)
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

ML_ENGINE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ML_ENGINE_DIR.parent

DATA_DIR = PROJECT_ROOT / "datasets" / "processed" / "comparisons"
RESULTS_DIR = ML_ENGINE_DIR / "results" / "phase2"

VERSIONS = {
    "V1": ("train_features_v1.csv", "test_features_v1.csv"),
    "V2": ("train_features_v2.csv", "test_features_v2.csv"),
    "V3": ("train_features_v3.csv", "test_features_v3.csv"),
}

RANDOM_STATE = 42
VALIDATION_SIZE = 0.20
TARGET_RECALL = 0.75

# KNN on ~405k training rows and ~101k test rows can be very slow and
# memory-intensive. First run the tree-based models. We will benchmark
# KNN separately rather than letting it block the entire comparison.
RUN_KNN = False


# ---------------------------------------------------------------------
# DATA VALIDATION AND LABEL ENCODING
# ---------------------------------------------------------------------

def load_dataset(train_filename, test_filename, version):
    train_path = DATA_DIR / train_filename
    test_path = DATA_DIR / test_filename

    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError(
            f"{version} split files not found in: {DATA_DIR}\n"
            f"Expected: {train_filename} and {test_filename}"
        )

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    if "Label" not in train_df.columns or "Label" not in test_df.columns:
        raise ValueError(f"{version}: Label column is missing.")

    if list(train_df.columns) != list(test_df.columns):
        raise ValueError(f"{version}: train/test columns do not match.")

    if train_df.isnull().any().any() or test_df.isnull().any().any():
        raise ValueError(f"{version}: missing values found. Resolve before training.")

    feature_columns = [column for column in train_df.columns if column != "Label"]

    # Preserve the source labels in the CSVs; encode only in memory.
    label_map = {"good": 0, "bad": 1}
    train_labels = train_df["Label"].astype(str).str.strip().str.lower()
    test_labels = test_df["Label"].astype(str).str.strip().str.lower()

    unexpected = (set(train_labels.unique()) | set(test_labels.unique())) - set(label_map)
    if unexpected:
        raise ValueError(
            f"{version}: unexpected labels {sorted(unexpected)}. "
            "Expected only 'good' and 'bad'."
        )

    X_train = train_df[feature_columns]
    X_test = test_df[feature_columns]
    y_train = train_labels.map(label_map).astype(int)
    y_test = test_labels.map(label_map).astype(int)

    # This comparison expects numeric engineered features.
    non_numeric = X_train.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric:
        raise ValueError(
            f"{version}: non-numeric feature columns found: {non_numeric}"
        )

    return X_train, X_test, y_train, y_test, feature_columns


# ---------------------------------------------------------------------
# THRESHOLD SELECTION (VALIDATION SET ONLY)
# ---------------------------------------------------------------------

def choose_threshold(y_true, probabilities, target_recall=TARGET_RECALL):
    from sklearn.metrics import precision_recall_curve

    precisions, recalls, thresholds = precision_recall_curve(
        y_true, probabilities, pos_label=1
    )

    # precision_recall_curve returns one more precision/recall point
    # than thresholds, so use recalls[:-1] and precisions[:-1].
    valid = np.where(recalls[:-1] >= target_recall)[0]

    if len(valid) == 0:
        # Fallback: choose the threshold with the highest validation F1.
        f1_values = (
            2 * precisions[:-1] * recalls[:-1]
            / (precisions[:-1] + recalls[:-1] + 1e-12)
        )
        best_index = int(np.nanargmax(f1_values))
    else:
        # Among thresholds meeting target recall, maximize precision.
        best_index = int(valid[np.argmax(precisions[valid])])

    return float(thresholds[best_index])


# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------

def positive_class_probability(model, X):
    class_positions = np.where(model.classes_ == 1)[0]
    if len(class_positions) != 1:
        raise ValueError("Could not locate positive class 1 (Bad/Phishing).")
    return model.predict_proba(X)[:, int(class_positions[0])]


def calculate_metrics(y_true, probabilities, threshold):
    predictions = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(
        y_true, predictions, labels=[0, 1]
    ).ravel()

    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision": float(precision_score(y_true, predictions, pos_label=1, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, pos_label=1, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, pos_label=1, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        # Average Precision (AP) is used as the PR-curve summary metric.
        "average_precision": float(average_precision_score(y_true, probabilities)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


# ---------------------------------------------------------------------
# MODEL FACTORIES
# ---------------------------------------------------------------------

def build_models(y_subtrain):
    negative_count = int((y_subtrain == 0).sum())
    positive_count = int((y_subtrain == 1).sum())
    scale_pos_weight = negative_count / max(positive_count, 1)

    models = {
        "Decision Tree": DecisionTreeClassifier(
            random_state=RANDOM_STATE,
            class_weight="balanced",
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=30,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features="sqrt",
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            random_state=RANDOM_STATE,
            eval_metric="logloss",
            tree_method="hist",
            n_jobs=-1,
        ),
    }

    if RUN_KNN:
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.neighbors import KNeighborsClassifier

        models["KNN"] = Pipeline([
            ("scaler", StandardScaler()),
            ("knn", KNeighborsClassifier(
                n_neighbors=5,
                weights="distance",
                algorithm="auto",
                n_jobs=-1,
            )),
        ])

    return models


# ---------------------------------------------------------------------
# RUN COMPARISON
# ---------------------------------------------------------------------

def run():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    all_results = []
    reports = []

    for version, (train_file, test_file) in VERSIONS.items():
        print("\n" + "=" * 72)
        print(f"STARTING {version}")
        print("=" * 72)

        X_train, X_test, y_train, y_test, feature_columns = load_dataset(
            train_file, test_file, version
        )

        print(f"Training shape: {X_train.shape}")
        print(f"Testing shape:  {X_test.shape}")
        print("Training labels (0=Good, 1=Bad):")
        print(y_train.value_counts().sort_index().to_dict())
        print("Testing labels (0=Good, 1=Bad):")
        print(y_test.value_counts().sort_index().to_dict())

        X_subtrain, X_val, y_subtrain, y_val = train_test_split(
            X_train,
            y_train,
            test_size=VALIDATION_SIZE,
            random_state=RANDOM_STATE,
            stratify=y_train,
        )

        models = build_models(y_subtrain)

        for model_name, model in models.items():
            print(f"\n--- {version}: {model_name} ---")
            print("Fitting on sub-training data...")

            model.fit(X_subtrain, y_subtrain)

            val_probabilities = positive_class_probability(model, X_val)
            selected_threshold = choose_threshold(
                y_val, val_probabilities, TARGET_RECALL
            )
            print(f"Validation-selected threshold: {selected_threshold:.6f}")

            # Refit using all training data. The test set is still untouched.
            print("Refitting on complete training data...")
            model.fit(X_train, y_train)

            print("Evaluating once on held-out test data...")
            test_probabilities = positive_class_probability(model, X_test)

            default_metrics = calculate_metrics(
                y_test, test_probabilities, 0.50
            )
            tuned_metrics = calculate_metrics(
                y_test, test_probabilities, selected_threshold
            )

            result = {
                "dataset_version": version,
                "model": model_name,
                "feature_count": len(feature_columns),
                "validation_threshold": selected_threshold,
            }

            for key, value in default_metrics.items():
                result[f"default_{key}"] = value
            for key, value in tuned_metrics.items():
                result[f"tuned_{key}"] = value

            all_results.append(result)

            report = classification_report(
                y_test,
                (test_probabilities >= selected_threshold).astype(int),
                labels=[0, 1],
                target_names=["Good (Legitimate)", "Bad (Phishing)"],
                output_dict=True,
                zero_division=0,
            )
            reports.append({
                "dataset_version": version,
                "model": model_name,
                "classification_report": report,
            })

            print(
                f"Default threshold 0.50 | "
                f"Accuracy={default_metrics['accuracy']:.4f}, "
                f"Precision={default_metrics['precision']:.4f}, "
                f"Recall={default_metrics['recall']:.4f}, "
                f"F1={default_metrics['f1']:.4f}, "
                f"ROC-AUC={default_metrics['roc_auc']:.4f}, "
                f"AP={default_metrics['average_precision']:.4f}"
            )
            print(
                f"Tuned threshold {selected_threshold:.4f} | "
                f"Accuracy={tuned_metrics['accuracy']:.4f}, "
                f"Precision={tuned_metrics['precision']:.4f}, "
                f"Recall={tuned_metrics['recall']:.4f}, "
                f"F1={tuned_metrics['f1']:.4f}"
            )

            # Release model memory before moving to the next algorithm/version.
            del model

    results_df = pd.DataFrame(all_results)
    results_path = RESULTS_DIR / "phase2_model_comparison.csv"
    results_df.to_csv(results_path, index=False)

    reports_path = RESULTS_DIR / "phase2_classification_reports.json"
    reports_path.write_text(json.dumps(reports, indent=2), encoding="utf-8")

    print("\n" + "=" * 72)
    print("PHASE 2 COMPARISON COMPLETED")
    print("=" * 72)
    print(f"Results CSV: {results_path}")
    print(f"Classification reports: {reports_path}")
    display_columns = [
        "dataset_version", "model", "feature_count",
        "default_accuracy", "default_precision", "default_recall",
        "default_f1", "default_roc_auc", "default_average_precision",
        "tuned_threshold", "tuned_precision", "tuned_recall", "tuned_f1",
    ]
    print(results_df[display_columns].to_string(index=False))


if __name__ == "__main__":
    run()
