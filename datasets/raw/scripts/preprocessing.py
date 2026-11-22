
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parents[2]

# Support both local and GitHub folder structures
if (BASE_DIR / "datasets" / "processed").exists():
    DATA_DIR = BASE_DIR / "datasets" / "processed"
else:
    DATA_DIR = BASE_DIR / "dataset" / "proceed"

INPUT_PATH = DATA_DIR / "url_features.csv"
TRAIN_PATH = DATA_DIR / "train_features.csv"
TEST_PATH = DATA_DIR / "test_features.csv"

FEATURE_COLUMNS = [
    "URL_Length",
    "Dot_Count",
    "Hyphen_Count",
    "Digit_Count",
    "Special_Char_Count",
    "Has_HTTPS"
]

LABEL_MAPPING = {
    "good": 0,
    "bad": 1
}

print("========== DATA PREPROCESSING ==========")

df = pd.read_csv(INPUT_PATH)

# Convert labels into numerical values
df["Label"] = (
    df["Label"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map(LABEL_MAPPING)
)

if df["Label"].isnull().any():
    raise ValueError("Unknown labels found in the dataset.")

# Separate features and target
X = df[FEATURE_COLUMNS]
y = df["Label"]

print("\nFeature Order:")
print(X.columns.tolist())

print("\nEncoded Label Distribution:")
print(y.value_counts())

# Split data into 80% training and 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Add labels back to the datasets
train_data = X_train.copy()
train_data["Label"] = y_train

test_data = X_test.copy()
test_data["Label"] = y_test

# Save the new datasets
train_data.to_csv(TRAIN_PATH, index=False)
test_data.to_csv(TEST_PATH, index=False)

print("\nTraining Dataset Shape:")
print(train_data.shape)

print("\nTesting Dataset Shape:")
print(test_data.shape)

print("\nTraining Label Distribution:")
print(train_data["Label"].value_counts())

print("\nTesting Label Distribution:")
print(test_data["Label"].value_counts())

print("\nPreprocessing completed successfully!")
print("Training data:", TRAIN_PATH)
print("Testing data:", TEST_PATH)
