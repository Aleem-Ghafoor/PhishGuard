
import pandas as pd
from pathlib import Path

# Locate the project folder
BASE_DIR = Path(__file__).resolve().parents[2]

# Load cleaned dataset
DATA_PATH = BASE_DIR / "datasets" / "processed" / "cleaned_phishing_urls.csv"

df = pd.read_csv(DATA_PATH)

print("========== DATASET INSPECTION ==========")

# Dataset dimensions
print("\nDataset Shape:")
print(df.shape)

# Column names
print("\nColumns:")
print(df.columns.tolist())

# First five records
print("\nFirst Five Records:")
print(df.head())

# Missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Duplicate records
print("\nDuplicate Records:")
print(df.duplicated().sum())

# Label distribution
print("\nLabel Distribution:")
print(df["Label"].value_counts())

print("\n========== INSPECTION COMPLETED ==========")
