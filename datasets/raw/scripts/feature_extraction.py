import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# Support both local and GitHub folder structures
if (BASE_DIR / "datasets" / "processed").exists():
    DATA_DIR = BASE_DIR / "datasets" / "processed"
else:
    DATA_DIR = BASE_DIR / "dataset" / "proceed"

INPUT_PATH = DATA_DIR / "cleaned_phishing_urls.csv"
OUTPUT_PATH = DATA_DIR / "url_features.csv"

FEATURE_COLUMNS = [
    "URL_Length",
    "Dot_Count",
    "Hyphen_Count",
    "Digit_Count",
    "Special_Char_Count",
    "Has_HTTPS"
]


def extract_features(url):
    url = str(url).strip()

    return {
        "URL_Length": len(url),
        "Dot_Count": url.count("."),
        "Hyphen_Count": url.count("-"),
        "Digit_Count": sum(char.isdigit() for char in url),
        "Special_Char_Count": sum(not char.isalnum() for char in url),
        "Has_HTTPS": int(url.lower().startswith("https://"))
    }


print("========== URL FEATURE EXTRACTION ==========")

df = pd.read_csv(INPUT_PATH)

features_df = pd.DataFrame(
    df["URL"].apply(extract_features).tolist(),
    columns=FEATURE_COLUMNS
)

features_df["Label"] = df["Label"].values

features_df.to_csv(OUTPUT_PATH, index=False)

print("\nFeature Names:")
print(FEATURE_COLUMNS)

print("\nFirst Five Records:")
print(features_df.head())

print("\nDataset Shape:")
print(features_df.shape)

print("\nHTTPS Distribution:")
print(features_df["Has_HTTPS"].value_counts())

print("\nFeature extraction completed successfully!")
print("Saved to:", OUTPUT_PATH)
