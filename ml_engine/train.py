
import pandas as pd
import joblib

from pathlib import Path

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    precision_recall_curve,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from xgboost import XGBClassifier

from evaluation import evaluate_model


# ==========================================
# CONFIGURATION
# ==========================================

ML_ENGINE_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = ML_ENGINE_DIR.parent

TRAIN_PATH = PROJECT_ROOT / "datasets/raw/processed/train_features.csv"
TEST_PATH = PROJECT_ROOT / "datasets/raw/processed/test_features.csv"

MODEL_DIR = ML_ENGINE_DIR / "model"
MODEL_PATH = MODEL_DIR / "random_forest.pkl"

TARGET_RECALL = 0.75
RANDOM_STATE = 42


# ==========================================
# HELPER FUNCTION: SELECT THRESHOLD
# ==========================================

def select_recall_threshold(model, X_val, y_val, model_name):

    probabilities = model.predict_proba(X_val)[:, 1]

    precisions, recalls, thresholds = precision_recall_curve(
        y_val,
        probabilities
    )

    valid_indices = [
        i for i in range(len(thresholds))
        if recalls[i] >= TARGET_RECALL
    ]

    if not valid_indices:
        raise ValueError(
            f"{model_name} could not achieve target validation recall."
        )

    best_index = max(
        valid_indices,
        key=lambda i: (precisions[i], thresholds[i])
    )

    best_threshold = thresholds[best_index]

    print(f"\n{model_name} Selected Threshold: {best_threshold:.6f}")
    print(f"Validation Precision: {precisions[best_index]:.4f}")
    print(f"Validation Recall: {recalls[best_index]:.4f}")

    return best_threshold, probabilities


# ==========================================
# HELPER FUNCTION: THRESHOLD COMPARISON
# ==========================================

def compare_thresholds(y_true, probabilities, threshold_values, model_name):

    print(f"\n========== {model_name} THRESHOLD COMPARISON ==========")

    f1_scores = []

    for threshold in threshold_values:

        predictions = (probabilities >= threshold).astype(int)

        accuracy = accuracy_score(y_true, predictions)
        precision = precision_score(
            y_true, predictions, zero_division=0
        )
        recall = recall_score(
            y_true, predictions, zero_division=0
        )
        f1 = f1_score(
            y_true, predictions, zero_division=0
        )

        f1_scores.append(f1)

        print(f"\nThreshold: {threshold:.2f}")
        print(f"Accuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-Score:  {f1:.4f}")

    best_position = f1_scores.index(max(f1_scores))
    best_threshold = threshold_values[best_position]

    print(f"\nBest {model_name} F1 Threshold: {best_threshold:.2f}")
    print(f"Validation F1: {f1_scores[best_position]:.4f}")

    return best_threshold, f1_scores[best_position]


# ==========================================
# LOAD DATASETS
# ==========================================

train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

print("\n========== DATASET INFORMATION ==========")

print("Training Shape:", train_df.shape)
print("Testing Shape:", test_df.shape)

print("\nTraining Class Distribution:")
print(train_df["Label"].value_counts())

print("\nTesting Class Distribution:")
print(test_df["Label"].value_counts())

print("\nMissing Values:")
print(train_df.isnull().sum())


# ==========================================
# HTTPS FEATURE ANALYSIS
# ==========================================

print("\n========== HTTPS FEATURE ANALYSIS ==========")

print("\nHTTPS Distribution:")
print(train_df["Has_HTTPS"].value_counts())

print("\nHTTPS Distribution by Label:")
print(pd.crosstab(
    train_df["Label"],
    train_df["Has_HTTPS"]
))


# ==========================================
# FEATURE AND TARGET SEPARATION
# ==========================================

X_train = train_df.drop("Label", axis=1)
y_train = train_df["Label"]

X_test = test_df.drop("Label", axis=1)
y_test = test_df["Label"]


# ==========================================
# TRAIN / VALIDATION SPLIT
# ==========================================

X_subtrain, X_val, y_subtrain, y_val = train_test_split(
    X_train,
    y_train,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y_train
)


# ==========================================
# DECISION TREE BASELINE
# ==========================================

print("\n========== DECISION TREE BASELINE ==========")

dt_model = DecisionTreeClassifier(
    random_state=RANDOM_STATE
)

dt_model.fit(X_train, y_train)

evaluate_model(
    dt_model,
    X_test,
    y_test,
    "DECISION TREE BASELINE"
)


# ==========================================
# KNN - K-NEAREST NEIGHBORS
# ==========================================

print("\n========== KNN MODEL ==========")

knn_model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(
        n_neighbors=5,
        weights="distance",
        algorithm="kd_tree",
        leaf_size=40,
        n_jobs=-1
    ))
])

print("\nTraining KNN on sub-training data...")

knn_model.fit(X_subtrain, y_subtrain)

knn_best_threshold, knn_val_probabilities = select_recall_threshold(
    knn_model,
    X_val,
    y_val,
    "KNN"
)


# ==========================================
# KNN THRESHOLD COMPARISON
# ==========================================

knn_threshold_values = [
    0.10, 0.15, 0.20, 0.25, 0.30,
    0.35, 0.40, 0.45, 0.50, 0.60, 0.70
]

knn_f1_threshold, knn_best_f1 = compare_thresholds(
    y_val,
    knn_val_probabilities,
    knn_threshold_values,
    "KNN"
)


# ==========================================
# FINAL KNN EVALUATION
# ==========================================

print("\nRetraining KNN on complete training data...")

knn_final = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(
        n_neighbors=5,
        weights="distance",
        algorithm="kd_tree",
        leaf_size=40,
        n_jobs=-1
    ))
])

knn_final.fit(X_train, y_train)

print("\n========== KNN RECALL-FOCUSED EVALUATION ==========")

evaluate_model(
    knn_final,
    X_test,
    y_test,
    "KNN (Recall-Optimized Threshold)",
    threshold=knn_best_threshold
)

print("\n========== KNN F1-FOCUSED EVALUATION ==========")

evaluate_model(
    knn_final,
    X_test,
    y_test,
    "KNN (F1 Threshold 0.45)",
    threshold=0.45
)


# ==========================================
# DECISION TREE - THRESHOLD OPTIMIZATION
# ==========================================

print("\n========== DECISION TREE THRESHOLD OPTIMIZATION ==========")

dt_tuned = DecisionTreeClassifier(
    random_state=RANDOM_STATE
)

dt_tuned.fit(X_subtrain, y_subtrain)

dt_best_threshold, dt_val_probabilities = select_recall_threshold(
    dt_tuned,
    X_val,
    y_val,
    "DECISION TREE"
)


# ==========================================
# DECISION TREE THRESHOLD COMPARISON
# ==========================================

dt_threshold_values = [
    0.10, 0.15, 0.18, 0.20, 0.25,
    0.30, 0.40, 0.50, 0.70
]

dt_f1_threshold, dt_best_f1 = compare_thresholds(
    y_val,
    dt_val_probabilities,
    dt_threshold_values,
    "DECISION TREE"
)


# ==========================================
# FINAL DECISION TREE EVALUATION
# ==========================================

dt_final = DecisionTreeClassifier(
    random_state=RANDOM_STATE
)

dt_final.fit(X_train, y_train)

print("\n========== DECISION TREE RECALL-FOCUSED EVALUATION ==========")

evaluate_model(
    dt_final,
    X_test,
    y_test,
    "DECISION TREE (Recall-Optimized)",
    threshold=dt_best_threshold
)

print("\n========== DECISION TREE F1-FOCUSED EVALUATION ==========")

evaluate_model(
    dt_final,
    X_test,
    y_test,
    "DECISION TREE (Threshold 0.40)",
    threshold=0.40
)


# ==========================================
# RANDOM FOREST HYPERPARAMETER TUNING
# ==========================================

print("\n========== RANDOM FOREST HYPERPARAMETER TUNING ==========")

rf_model = RandomForestClassifier(
    random_state=RANDOM_STATE,
    n_jobs=1
)

param_grid = {
    "n_estimators": [50, 100],
    "max_depth": [20, 30],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2],
    "max_features": ["sqrt"],
    "class_weight": ["balanced"]
}

random_search = RandomizedSearchCV(
    estimator=rf_model,
    param_distributions=param_grid,
    n_iter=4,
    cv=2,
    scoring="average_precision",
    random_state=RANDOM_STATE,
    n_jobs=2,
    verbose=2
)

random_search.fit(X_subtrain, y_subtrain)

best_rf_model = random_search.best_estimator_

print("\nBest Random Forest Hyperparameters:")
print(random_search.best_params_)

print("\nBest Cross Validation Average Precision:")
print(random_search.best_score_)


# ==========================================
# RANDOM FOREST THRESHOLD OPTIMIZATION
# ==========================================

print("\n========== RANDOM FOREST THRESHOLD OPTIMIZATION ==========")

rf_best_threshold, rf_val_probabilities = select_recall_threshold(
    best_rf_model,
    X_val,
    y_val,
    "RANDOM FOREST"
)


# ==========================================
# FINAL RANDOM FOREST EVALUATION
# ==========================================

print("\n========== FINAL RANDOM FOREST EVALUATION ==========")

best_rf_model.fit(X_train, y_train)

evaluate_model(
    best_rf_model,
    X_test,
    y_test,
    "TUNED RANDOM FOREST",
    threshold=rf_best_threshold
)


# ==========================================
# SAVE FINAL RANDOM FOREST MODEL
# ==========================================

print("\n========== SAVING FINAL MODEL ==========")

MODEL_DIR.mkdir(parents=True, exist_ok=True)

model_artifact = {
    "model": best_rf_model,
    "threshold": float(rf_best_threshold),
    "features": list(X_train.columns),
    "model_name": "Tuned Random Forest",
    "best_parameters": random_search.best_params_,
    "random_state": RANDOM_STATE
}

joblib.dump(model_artifact, MODEL_PATH)

print(f"\nFinal model saved successfully at: {MODEL_PATH}")
print(f"Saved threshold: {rf_best_threshold:.6f}")
print("Saved features:", model_artifact["features"])


# ==========================================
# XGBOOST CLASSIFIER
# ==========================================

print("\n========== XGBOOST CLASSIFIER ==========")

scale_pos_weight = (
    (y_train == 0).sum() / (y_train == 1).sum()
)

print(f"Scale Pos Weight: {scale_pos_weight:.4f}")

xgb_model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=RANDOM_STATE,
    eval_metric="logloss",
    n_jobs=2
)

xgb_model.fit(X_subtrain, y_subtrain)


# ==========================================
# XGBOOST THRESHOLD OPTIMIZATION
# ==========================================

print("\n========== XGBOOST THRESHOLD OPTIMIZATION ==========")

xgb_best_threshold, xgb_val_probabilities = select_recall_threshold(
    xgb_model,
    X_val,
    y_val,
    "XGBOOST"
)


# ==========================================
# FINAL XGBOOST EVALUATION
# ==========================================

print("\n========== FINAL XGBOOST EVALUATION ==========")

xgb_model.fit(X_train, y_train)

evaluate_model(
    xgb_model,
    X_test,
    y_test,
    "XGBOOST (Recall-Optimized)",
    threshold=xgb_best_threshold
)


# ==========================================
# FEATURE STATISTICS
# ==========================================

print("\n========== FEATURE STATISTICS BY CLASS ==========")

print(train_df.groupby("Label").mean(numeric_only=True))


# ==========================================
# TRAINING COMPLETED
# ==========================================

print("\n========== MODEL TRAINING COMPLETED ==========")
