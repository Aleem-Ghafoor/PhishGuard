# AI-Based Phishing URL Detection
## Dataset Documentation and Exploratory Data Analysis

### 1. Project Objective

The objective of this project is to develop a machine learning system that identifies whether a given URL is legitimate or phishing. The system classifies URLs into two categories: `good` and `bad`.

### 2. Dataset Information

- **Dataset Name:** Phishing Site URLs
- **Source:** Kaggle
- **Contributor:** taruntiwarihp
- **Original File:** phishing_site_urls.csv
- **Cleaned File:** cleaned_phishing_urls.csv

The dataset contains website URLs with their corresponding labels. It is used to train and evaluate a machine learning model for phishing URL detection.

### 3. Dataset Features

The original dataset contains two columns:

| Column | Description |
|---|---|
| URL | Website address used as input |
| Label | Target class: good or bad |

- `good` represents a legitimate URL.
- `bad` represents a phishing or malicious URL.

### 4. Data Cleaning and Preprocessing

The following preprocessing steps were performed:

1. Loaded the original CSV dataset using Pandas.
2. Checked the dataset for missing values.
3. Identified and removed duplicate records.
4. Handled URLs that appeared with conflicting labels.
5. Removed unnecessary spaces and empty URLs.
6. Saved the cleaned dataset as `cleaned_phishing_urls.csv`.

**Missing-value and duplicate handling:**

- Rows with missing URL or Label values are removed.
- Empty URLs are removed.
- URLs with conflicting labels are identified and removed.
- Duplicate URLs are removed so that repeated URLs do not appear in the cleaned dataset.

**Final dataset statistics:**

- Original dataset records: 549,346
- Final cleaned records: 507,194
- Missing values: 0

### 5. Class Distribution

The cleaned dataset contains:

| Label | Number of Records |
|---|---:|
| Good | 392,896 |
| Bad | 114,298 |
| Total | 507,194 |

The dataset contains more legitimate URLs than phishing URLs.

### 6. Train-Test Split

The cleaned dataset is divided using an 80:20 train-test split.

Stratified splitting is used to maintain the class distribution in both sets.

**Split configuration:**

- Training data: 80%
- Testing data: 20%
- Random state: 42
- Stratification: Enabled

**Training records:** 405,755

**Testing records:** 101,439

**Training distribution:**

| Label | Number of Records |
|---|---:|
| Good | 314,317 |
| Bad | 91,438 |

**Testing distribution:**

| Label | Number of Records |
|---|---:|
| Good | 78,579 |
| Bad | 22,860 |

### 7. URL Feature Extraction

After coordination with the machine learning team, six manually extracted numerical URL features were selected for both Decision Tree and Random Forest models.

The features must be used in the following exact order:

| Order | Feature | Description |
|---:|---|---|
| 1 | URL_Length | Total number of characters in a URL |
| 2 | Dot_Count | Number of dots in a URL |
| 3 | Hyphen_Count | Number of hyphens in a URL |
| 4 | Digit_Count | Number of numeric digits |
| 5 | Special_Char_Count | Number of non-alphanumeric characters |
| 6 | Has_HTTPS | Binary value: 1 if URL starts with HTTPS, otherwise 0 |

**HTTPS encoding:**

- `1` = URL starts with `https://`
- `0` = Otherwise

The feature extraction script uses the URL string's beginning to identify HTTPS. It does not count an HTTPS string appearing later in the URL as an HTTPS prefix.

These six features are used as the primary input features for model training. TF-IDF is not included in the current approach.

### 8. Exploratory Data Analysis Findings

The average feature values for both classes were compared.

| Feature | Bad URLs | Good URLs |
|---|---:|---:|
| Average URL Length | 71.06 | 45.77 |
| Average Dot Count | 3.01 | 1.78 |
| Average Hyphen Count | 0.72 | 1.33 |
| Average Digit Count | 10.28 | 3.13 |
| Average Special Characters | 9.11 | 6.48 |

**Observations:**

1. Bad URLs have a greater average length than good URLs.
2. Bad URLs contain more dots on average.
3. Good URLs contain more hyphens on average in this dataset.
4. Bad URLs contain considerably more digits.
5. Bad URLs also contain more special characters on average.

These observations show differences between the two URL classes. However, individual features alone cannot guarantee whether a URL is malicious.

### 9. Visualizations

The following graphs were generated and saved in the `EDA_Graphs` folder:

1. Average URL Length: Good vs Bad
2. URL Length Distribution: Good vs Bad
3. Average Number of Digits in URLs

### 10. Additional Dataset Observations

During URL inspection, some entries were found without an explicit protocol, while a few contained HTTP or HTTPS text. The cleaned dataset inspection did not identify Markdown-style link entries.

Therefore, URL formatting was considered during feature extraction.

The `Has_HTTPS` feature uses binary encoding based on whether the URL string starts with `https://`. URLs without this explicit prefix are assigned a value of 0.

In the generated feature dataset, 7 URLs received a value of 1, while 507,187 received a value of 0.

### 11. Final Machine Learning Preprocessing

The following preprocessing configuration has been agreed upon with the machine learning team.

**Target Label Encoding:**

| Original Label | Encoded Value | Meaning |
|---|---:|---|
| good | 0 | Legitimate |
| bad | 1 | Phishing |

Phishing is treated as the positive class.

**Feature Processing:**

- Six manually extracted numerical URL features are used.
- Features are maintained in the exact order specified in Section 7.
- No feature scaling is required for Decision Tree and Random Forest models.
- No TF-IDF vectorization is used in the current approach.
- No oversampling or undersampling is applied in the current preprocessing pipeline.
- The training and testing sets are kept separate.

**Train-Test Configuration:**

- Split ratio: 80:20
- Random state: 42
- Stratification: Enabled

**Verified output sizes:**

- Training dataset: 405,755 records
- Testing dataset: 101,439 records
- Both datasets contain six feature columns and one Label column.

### 12. Generated Output Files

The data engineering work includes the following CSV files:

| File Name | Purpose |
|---|---|
| `cleaned_phishing_urls.csv` | Cleaned URL dataset prepared earlier |
| `train_data.csv` | Original training split prepared earlier |
| `test_data.csv` | Original testing split prepared earlier |
| `url_features.csv` | Dataset containing six extracted URL features and original labels |
| `train_features.csv` | Training dataset containing six features and encoded labels |
| `test_features.csv` | Testing dataset containing six features and encoded labels |

The three feature-based files were generated by running the feature extraction and preprocessing scripts.

### 13. Data Engineering Scripts

The following Python scripts were created to organize and automate the data engineering workflow:

| Script | Purpose |
|---|---|
| `data_inspection.py` | Checks dataset shape, columns, missing values, duplicates, and label distribution |
| `data_cleaning.py` | Performs dataset cleaning and saves the cleaned CSV file |
| `feature_extraction.py` | Extracts the six numerical URL features |
| `preprocessing.py` | Encodes target labels and creates stratified training and testing datasets |

The feature extraction and preprocessing scripts were executed successfully. Their output shapes and class distributions were verified against the expected dataset statistics.

### 14. Conclusion

The dataset was cleaned, checked for missing values and duplicate records, and analyzed through exploratory data analysis.

Six manually extracted URL features were selected in coordination with the machine learning team. Target labels are encoded numerically, and the dataset is prepared using an 80:20 stratified train-test split.

Python scripts were created to automate feature extraction and preprocessing. The resulting feature-based datasets are prepared for Decision Tree and Random Forest model training without feature scaling or TF-IDF vectorization.