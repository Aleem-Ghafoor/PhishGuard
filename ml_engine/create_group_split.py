"""Create leakage-resistant, shared group-based splits for PhishGuard V1/V2/V3.

Run from the project root:
    python ml_engine/create_group_split.py

All rows sharing the same six baseline V1 feature values are assigned to
one partition. The exact same row indices are reused for V1, V2 and V3.
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "datasets" / "raw" / "versions"
OUTPUT_DIR = PROJECT_ROOT / "datasets" / "processed" / "group_comparisons"

FILES = {
    "V1": "url_features.csv",
    "V2": "url_features_v2.csv",
    "V3": "url_features_v3.csv",
}
BASELINE_FEATURES = [
    "URL_Length",
    "Dot_Count",
    "Hyphen_Count",
    "Digit_Count",
    "Special_Char_Count",
    "Has_HTTPS",
]
LABEL_COLUMN = "Label"
RANDOM_STATE = 42
N_SPLITS = 5  # One fold is approximately 20% test data.
LABEL_MAP = {"good": 0, "bad": 1}


def load_and_validate():
    datasets = {}
    for version, filename in FILES.items():
        path = RAW_DIR / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}\nCopy {filename} into {RAW_DIR} first."
            )
        df = pd.read_csv(path)
        if LABEL_COLUMN not in df.columns:
            raise ValueError(f"{filename}: missing '{LABEL_COLUMN}' column.")
        if df.isnull().any().any():
            raise ValueError(f"{filename}: missing values found; stop and inspect first.")
        labels = df[LABEL_COLUMN].astype(str).str.strip().str.lower()
        unexpected = set(labels.unique()) - set(LABEL_MAP)
        if unexpected:
            raise ValueError(f"{filename}: unexpected labels: {sorted(unexpected)}")
        datasets[version] = df

    row_counts = {version: len(df) for version, df in datasets.items()}
    if len(set(row_counts.values())) != 1:
        raise ValueError(f"Row counts differ across versions: {row_counts}")

    reference = datasets["V1"]
    missing_baseline = [c for c in BASELINE_FEATURES if c not in reference.columns]
    if missing_baseline:
        raise ValueError(f"V1 missing baseline features: {missing_baseline}")

    ref_labels = reference[LABEL_COLUMN].astype(str).str.strip().str.lower().reset_index(drop=True)
    for version, df in datasets.items():
        labels = df[LABEL_COLUMN].astype(str).str.strip().str.lower().reset_index(drop=True)
        if not labels.equals(ref_labels):
            raise ValueError(f"{version}: label sequence/order differs from V1.")
        for column in BASELINE_FEATURES:
            if column not in df.columns:
                raise ValueError(f"{version}: missing shared feature {column}.")
            # Exact value equality is required before reusing row indices.
            if not reference[column].reset_index(drop=True).equals(df[column].reset_index(drop=True)):
                raise ValueError(f"{version}: shared feature '{column}' differs from V1.")

    return datasets, ref_labels


def main():
    datasets, labels_text = load_and_validate()
    reference = datasets["V1"]
    y = labels_text.map(LABEL_MAP).to_numpy(dtype=int)

    # Factorize complete rows of the six shared baseline features into group IDs.
    group_frame = reference[BASELINE_FEATURES].reset_index(drop=True)
    groups, unique_groups = pd.factorize(
        pd.MultiIndex.from_frame(group_frame), sort=False
    )
    unique_group_count = len(unique_groups)

    splitter = StratifiedGroupKFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    train_idx, test_idx = next(splitter.split(np.zeros(len(y)), y, groups))

    train_group_ids = set(groups[train_idx])
    test_group_ids = set(groups[test_idx])
    overlap = train_group_ids.intersection(test_group_ids)
    if overlap:
        raise RuntimeError(f"Group leakage detected: {len(overlap)} groups overlap.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for version, df in datasets.items():
        train_df = df.iloc[train_idx].reset_index(drop=True)
        test_df = df.iloc[test_idx].reset_index(drop=True)
        train_df.to_csv(OUTPUT_DIR / f"train_features_{version.lower()}.csv", index=False)
        test_df.to_csv(OUTPUT_DIR / f"test_features_{version.lower()}.csv", index=False)

    # Audit exact full-feature vector overlap after split for each version.
    overlap_audit = {}
    for version, df in datasets.items():
        feature_cols = [c for c in df.columns if c != LABEL_COLUMN]
        train_vectors = pd.MultiIndex.from_frame(df.iloc[train_idx][feature_cols].reset_index(drop=True))
        test_vectors = pd.MultiIndex.from_frame(df.iloc[test_idx][feature_cols].reset_index(drop=True))
        overlap_audit[version] = int(train_vectors.isin(test_vectors).sum())

    def class_counts(indices):
        vals, counts = np.unique(y[indices], return_counts=True)
        result = {"Good": 0, "Bad": 0}
        for value, count in zip(vals, counts):
            result["Good" if value == 0 else "Bad"] = int(count)
        return result

    metadata = {
        "method": "StratifiedGroupKFold",
        "n_splits": N_SPLITS,
        "selected_fold": 1,
        "random_state": RANDOM_STATE,
        "group_definition": "Identical values across the six shared V1 baseline features",
        "total_rows": int(len(y)),
        "unique_groups": int(unique_group_count),
        "train_rows": int(len(train_idx)),
        "test_rows": int(len(test_idx)),
        "train_groups": int(len(train_group_ids)),
        "test_groups": int(len(test_group_ids)),
        "group_overlap_count": int(len(overlap)),
        "train_class_counts": class_counts(train_idx),
        "test_class_counts": class_counts(test_idx),
        "exact_full_feature_vector_overlap_rows_by_version": overlap_audit,
        "note": "Same row indices are used for V1, V2 and V3. A zero overlap confirms no identical full feature vector from the held-out test rows appears in training for that version.",
    }
    with open(OUTPUT_DIR / "group_split_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\nGROUP SPLIT CREATED SUCCESSFULLY")
    print(f"Output folder: {OUTPUT_DIR}")
    print(f"Total rows: {len(y):,}")
    print(f"Unique baseline feature groups: {unique_group_count:,}")
    print(f"Train rows: {len(train_idx):,} ({len(train_idx)/len(y):.2%})")
    print(f"Test rows:  {len(test_idx):,} ({len(test_idx)/len(y):.2%})")
    print(f"Train classes: {metadata['train_class_counts']}")
    print(f"Test classes:  {metadata['test_class_counts']}")
    print(f"Group overlap: {len(overlap)}")
    print("Exact full-feature-vector overlap rows:")
    for version, count in overlap_audit.items():
        print(f"  {version}: {count}")
    print("\nCreated 6 split CSVs and group_split_metadata.json.")


if __name__ == "__main__":
    main()
