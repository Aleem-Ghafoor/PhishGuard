"""PhishGuard - Group-based Phase 2 model comparison.

Compares V1, V2 and V3 on the group-isolated splits created by
ml_engine/create_group_split.py. Identical baseline feature vectors are kept
entirely within either train or test. Labels: good -> 0, bad -> 1.

Run from the project root:
    python ml_engine/train_group_comparison.py

This script does NOT overwrite Phase 2 results or the existing model artifact.
It writes its outputs to ml_engine/results/group_phase2/.
"""

from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
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
DATA_DIR = PROJECT_ROOT / "datasets" / "processed" / "group_comparisons"
RESULTS_DIR = ML_ENGINE_DIR / "results" / "group_phase2"

VERSIONS = {
    "V1": ("train_features_v1.csv", "test_features_v1.csv"),
    "V2": ("train_features_v2.csv", "test_features_v2.csv"),
    "V3": ("train_features_v3.csv", "test_features_v3.csv"),
}

RANDOM_STATE = 42
TARGET_RECALL = 0.75
BASELINE_FEATURES = [
    "URL_Length",
    "Dot_Count",
    "Hyphen_Count",
    "Digit_Count",
    "Special_Char_Count",
    "Has_HTTPS",
]

# KNN is intentionally excluded from this first grouped experiment because
# its fit/prediction on this dataset size can be very slow and memory-heavy.


# ---------------------------------------------------------------------
# DATA LOADING / VALIDATION
# ---------------------------------------------------------------------

def load_dataset(train_filename, test_filename, version):
    train_path = DATA_DIR / train_filename
    test_path = DATA_DIR / test_filename

    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError(
            f"{version} group split files were not found in: {DATA_DIR}\n"
            f"Expected: {train_filename} and {test_filename}\n"
            "Run: python ml_engine/create_group_split.py"
        )

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    if "Label" not in train_df.columns or "Label" not in test_df.columns:
        raise ValueError(f"{version}: Label column is missing.")
    if list(train_df.columns) != list(test_df.columns):
        raise ValueError(f"{version}: train/test columns do not match.")
    if train_df.empty or test_df.empty:
        raise ValueError(f"{version}: train or test split is empty.")
    if train_df.isnull().any().any() or test_df.isnull().any().any():
        raise ValueError(f"{version}: missing values found. Stop and inspect data.")

    feature_columns = [column for column in train_df.columns if column != "Label"]
    if not feature_columns:
        raise ValueError(f"{version}: no feature columns found.")

    label_map = {"good": 0, "bad": 1}
    train_labels = train_df["Label"].astype(str).str.strip().str.lower()
    test_labels = test_df["Label"].astype(str).str.strip().str.lower()

    unexpected = (set(train_labels.unique()) | set(test_labels.unique())) - set(label_map)
    if unexpected:
        raise ValueError(
            f"{version}: unexpected labels {sorted(unexpected)}; "
            "expected only 'good' and 'bad'."
        )

    X_train = train_df[feature_columns]
    X_test = test_df[feature_columns]
    y_train = train_labels.map(label_map).astype(int)
    y_test = test_labels.map(label_map).astype(int)

    non_numeric = X_train.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric:
        raise ValueError(f"{version}: non-numeric features found: {non_numeric}")

    # Basic consistency check: the group-split CSVs should retain both classes.
    if set(y_train.unique()) != {0, 1} or set(y_test.unique()) != {0, 1}:
        raise ValueError(f"{version}: both Good (0) and Bad (1) must exist in train and test.")

    return X_train, X_test, y_train, y_test, feature_columns


# ---------------------------------------------------------------------
# GROUP-AWARE VALIDATION SPLIT
# ---------------------------------------------------------------------

def make_group_validation_indices(X_train, y_train):
    missing = [column for column in BASELINE_FEATURES if column not in X_train.columns]
    if missing:
        raise ValueError(f"Shared baseline features missing for group validation: {missing}")

    group_frame = X_train[BASELINE_FEATURES].reset_index(drop=True)
    groups, _ = pd.factorize(pd.MultiIndex.from_frame(group_frame), sort=False)
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    subtrain_indices, validation_indices = next(
        splitter.split(X_train, y_train, groups)
    )

    subtrain_groups = set(groups[subtrain_indices])
    validation_groups = set(groups[validation_indices])
    if subtrain_groups.intersection(validation_groups):
        raise RuntimeError("Group overlap detected between subtrain and validation.")

    return subtrain_indices, validation_indices

# VALIDATION-ONLY THRESHOLD SELECTION
# ---------------------------------------------------------------------

def choose_threshold(y_true, probabilities, target_recall=TARGET_RECALL):
    from sklearn.metrics import precision_recall_curve

    precisions, recalls, thresholds = precision_recall_curve(
        y_true, probabilities, pos_label=1
    )

    valid = np.where(recalls[:-1] >= target_recall)[0]
    if len(valid) == 0:
        f1_values = (
            2 * precisions[:-1] * recalls[:-1]
            / (precisions[:-1] + recalls[:-1] + 1e-12)
        )
        best_index = int(np.nanargmax(f1_values))
    else:
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
    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()

    return {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision": float(precision_score(y_true, predictions, pos_label=1, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, pos_label=1, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, pos_label=1, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "average_precision": float(average_precision_score(y_true, probabilities)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


# ---------------------------------------------------------------------
# MODEL FACTORY - MATCHES THE PHASE 2 MODEL CONFIGURATION
# ---------------------------------------------------------------------

def build_models(y_subtrain):
    negative_count = int((y_subtrain == 0).sum())
    positive_count = int((y_subtrain == 1).sum())
    scale_pos_weight = negative_count / max(positive_count, 1)

    return {
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


# ---------------------------------------------------------------------
# RUN GROUP-BASED COMPARISON
# ---------------------------------------------------------------------

def run():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    metadata_path = DATA_DIR / "group_split_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Missing split metadata: {metadata_path}\n"
            "Run: python ml_engine/create_group_split.py"
        )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("group_overlap_count") != 0:
        raise RuntimeError("Group split metadata reports train/test group overlap. Aborting.")

    all_results = []
    reports = []

    # Build one internal group-isolated validation split from V1 and reuse the
    # exact same row indices for V2 and V3, just like the shared outer split.
    ref_train_file, ref_test_file = VERSIONS["V1"]
    X_ref_train, _, y_ref_train, _, _ = load_dataset(
        ref_train_file, ref_test_file, "V1"
    )
    subtrain_indices, validation_indices = make_group_validation_indices(
        X_ref_train, y_ref_train
    )
    del X_ref_train, y_ref_train

    print("\nGROUP-BASED PHISHGUARD MODEL COMPARISON")
    print(f"Split method: {metadata.get('method')}")
    print(f"Group definition: {metadata.get('group_definition')}")
    print(f"Group overlap: {metadata.get('group_overlap_count')}")
    print(f"Output folder: {RESULTS_DIR}")

    for version, (train_file, test_file) in VERSIONS.items():
        print("\n" + "=" * 76)
        print(f"STARTING {version}")
        print("=" * 76)

        X_train, X_test, y_train, y_test, feature_columns = load_dataset(
            train_file, test_file, version
        )

        print(f"Training shape: {X_train.shape}")
        print(f"Testing shape:  {X_test.shape}")
        print(f"Training labels (0=Good, 1=Bad): {y_train.value_counts().sort_index().to_dict()}")
        print(f"Testing labels  (0=Good, 1=Bad): {y_test.value_counts().sort_index().to_dict()}")

        X_subtrain = X_train.iloc[subtrain_indices]
        X_val = X_train.iloc[validation_indices]
        y_subtrain = y_train.iloc[subtrain_indices]
        y_val = y_train.iloc[validation_indices]
        print(f"Sub-training shape: {X_subtrain.shape}")
        print(f"Validation shape:   {X_val.shape}")
        print("Validation split: same group-isolated row indices reused for V1/V2/V3.")

        models = build_models(y_subtrain)

        for model_name, model in models.items():
            print(f"\n--- {version}: {model_name} ---")
            print("Fitting on sub-training data...")
            model.fit(X_subtrain, y_subtrain)

            val_probabilities = positive_class_probability(model, X_val)
            selected_threshold = choose_threshold(y_val, val_probabilities, TARGET_RECALL)
            print(f"Validation-selected threshold: {selected_threshold:.6f}")

            # Keep the same protocol as the earlier Phase 2 experiment:
            # select threshold on validation, then refit on all training rows.
            print("Refitting on complete group-isolated training data...")
            model.fit(X_train, y_train)

            print("Evaluating on the untouched group-isolated test set...")
            test_probabilities = positive_class_probability(model, X_test)

            default_metrics = calculate_metrics(y_test, test_probabilities, 0.50)
            tuned_metrics = calculate_metrics(y_test, test_probabilities, selected_threshold)

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

            default_predictions = (test_probabilities >= 0.50).astype(int)
            tuned_predictions = (test_probabilities >= selected_threshold).astype(int)
            reports.append({
                "dataset_version": version,
                "model": model_name,
                "default_threshold_classification_report": classification_report(
                    y_test, default_predictions,
                    labels=[0, 1],
                    target_names=["Good (Legitimate)", "Bad (Phishing)"],
                    output_dict=True,
                    zero_division=0,
                ),
                "tuned_threshold_classification_report": classification_report(
                    y_test, tuned_predictions,
                    labels=[0, 1],
                    target_names=["Good (Legitimate)", "Bad (Phishing)"],
                    output_dict=True,
                    zero_division=0,
                ),
            })

            print(
                "Default 0.50 | "
                f"Accuracy={default_metrics['accuracy']:.4f}, "
                f"Precision={default_metrics['precision']:.4f}, "
                f"Recall={default_metrics['recall']:.4f}, "
                f"F1={default_metrics['f1']:.4f}, "
                f"ROC-AUC={default_metrics['roc_auc']:.4f}, "
                f"AP={default_metrics['average_precision']:.4f}"
            )
            print(
                f"Tuned {selected_threshold:.4f} | "
                f"Accuracy={tuned_metrics['accuracy']:.4f}, "
                f"Precision={tuned_metrics['precision']:.4f}, "
                f"Recall={tuned_metrics['recall']:.4f}, "
                f"F1={tuned_metrics['f1']:.4f}"
            )
            del model

    results_df = pd.DataFrame(all_results)
    results_path = RESULTS_DIR / "group_model_comparison.csv"
    results_df.to_csv(results_path, index=False)

    reports_path = RESULTS_DIR / "group_classification_reports.json"
    reports_path.write_text(json.dumps(reports, indent=2), encoding="utf-8")

    run_info = {
        "experiment": "PhishGuard group-based model comparison",
        "split_metadata": metadata,
        "models": ["Decision Tree", "Random Forest", "XGBoost"],
        "threshold_selection": f"Group-isolated validation split only; target recall {TARGET_RECALL}",
        "test_evaluation": "Held-out group-isolated test set",
        "note": (
            "Both the internal validation split and final test split are group-isolated "
            "using the six shared baseline features. Threshold is selected using a "
            "model fitted on the sub-training split, then that model is refitted on "
            "all training rows before test evaluation. "
            "Probability calibration can shift slightly after refitting; interpret "
            "the tuned-threshold metrics with this limitation in mind."
        ),
    }
    (RESULTS_DIR / "group_run_metadata.json").write_text(
        json.dumps(run_info, indent=2), encoding="utf-8"
    )

    print("\n" + "=" * 76)
    print("GROUP-BASED COMPARISON COMPLETED")
    print("=" * 76)
    print(f"Results CSV: {results_path}")
    print(f"Classification reports: {reports_path}")
    print(f"Run metadata: {RESULTS_DIR / 'group_run_metadata.json'}")

    display_columns = [
        "dataset_version", "model", "feature_count",
        "default_accuracy", "default_precision", "default_recall",
        "default_f1", "default_roc_auc", "default_average_precision",
        "validation_threshold", "tuned_precision", "tuned_recall", "tuned_f1",
    ]
    print("\nRESULT SUMMARY (default and validation-tuned thresholds)")
    print(results_df[display_columns].to_string(index=False))


if __name__ == "__main__":
    run()
