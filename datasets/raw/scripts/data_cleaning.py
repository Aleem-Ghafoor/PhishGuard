
import pandas as pd
from pathlib import Path

# Locate project directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Input and output paths
INPUT_PATH = BASE_DIR / "raw" / "phishing_site_urls.csv"
OUTPUT_PATH = BASE_DIR / "processed" / "cleaned_phishing_urls.csv"

print("========== DATA CLEANING ==========")

# Load original dataset
df = pd.read_csv(INPUT_PATH)

print("\nOriginal Dataset Shape:")
print(df.shape)

# Remove rows with missing URL or Label
df = df.dropna(subset=["URL", "Label"])

# Remove leading and trailing spaces
df["URL"] = df["URL"].astype(str).str.strip()
df["Label"] = df["Label"].astype(str).str.strip()

# Remove empty URLs
df = df[df["URL"] != ""]

# Remove duplicate URLs that have conflicting labels
conflicting_urls = df.groupby("URL")["Label"].nunique()
conflicting_urls = conflicting_urls[conflicting_urls > 1].index

print("\nConflicting URLs Found:")
print(len(conflicting_urls))

df = df[~df["URL"].isin(conflicting_urls)]

# Remove duplicate records
df = df.drop_duplicates(subset=["URL"])

# Reset index
df = df.reset_index(drop=True)

# Create output directory if it does not exist
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Save cleaned dataset
df.to_csv(OUTPUT_PATH, index=False)

print("\nCleaned Dataset Shape:")
print(df.shape)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nLabel Distribution:")
print(df["Label"].value_counts())

print("\nCleaned dataset saved successfully!")
print("========== CLEANING COMPLETED ==========")
