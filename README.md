# 🛡️ PhishGuard – AI-Based Phishing URL Detection

PhishGuard is an AI/ML-based web application designed to detect potentially malicious and phishing URLs. It analyzes URL characteristics and uses Machine Learning models to classify URLs as **Legitimate** or **Phishing**.

The goal is to help users identify suspicious URLs and reduce the risk of phishing attacks.

## 🎯 Problem Statement

Phishing attacks are a common cybersecurity threat. Attackers create fake websites and malicious URLs to steal sensitive information such as passwords, financial details, and personal data.

PhishGuard aims to address this problem by using Machine Learning techniques to analyze URL features and predict whether a URL is legitimate or potentially malicious.

## ✨ Key Features

- URL-based phishing detection.
- Machine Learning-based classification.
- URL feature extraction and analysis.
- Data preprocessing and exploratory data analysis.
- Training and comparison of multiple ML models.
- Model evaluation using classification metrics.
- Threshold analysis for phishing detection.
- Random Forest-based final prediction model.
- Prediction interface for URL classification.
- Django-based web application and ML integration (in progress).

## 📊 Dataset

The project uses the **PhiUSIIL Phishing URL Dataset**, containing:

- **Total Records:** 235,795
- **Total Features:** 56
- **Input:** URL-related features.
- **Output:** URL classification.

Some dataset features include:

- URLLength
- DomainLength
- IsDomainIP
- TLD
- URLSimilarityIndex
- CharContinuationRate
- TLDLegitimateProb
- URLCharProb

**Dataset Source:** [UCI Machine Learning Repository – PhiUSIIL Phishing URL Dataset](https://archive.ics.uci.edu/dataset/967/phiusil%2Bphishing%2Burl%2Bdataset)

> Note: Dataset files are excluded from this GitHub repository to keep it lightweight. Download the original dataset from the source link above.

## ⚙️ Project Workflow

1. Problem Definition
2. Dataset Collection
3. Data Preprocessing
   - Handling missing values
   - Removing duplicates
   - Encoding categorical variables
   - Feature preparation and scaling where required
4. Exploratory Data Analysis (EDA)
5. Dataset Splitting
6. Feature Extraction
7. Model Training
8. Model Evaluation
9. Model Comparison
10. Threshold Analysis and Tuning
11. Final Model Selection
12. Prediction Interface Development
13. Django Web Application Integration

## 🤖 Machine Learning Development

Multiple Machine Learning algorithms were implemented and evaluated to identify a suitable model for phishing URL classification.

### Models Implemented

| Model | Status |
|---|---|
| Decision Tree | Implemented and evaluated |
| K-Nearest Neighbors (KNN) | Implemented and evaluated |
| Random Forest | Implemented and evaluated |
| XGBoost | Implemented and evaluated |

### Model Evaluation

The models were evaluated using the following performance metrics:

- Accuracy
- Precision
- Recall
- F1-Score
- Average Precision
- Confusion Matrix
- Classification Report

Additional experimentation included:

- Model performance comparison.
- Precision-Recall curve analysis.
- Classification threshold analysis.
- Random Forest feature importance analysis.
- Random Forest hyperparameter tuning.

### Final Model Selection

**Selected Model: Random Forest Classifier**

Random Forest was selected as the final model following the model experimentation and evaluation process.

The trained model is saved as:

`random_forest.pkl`

The prediction interface uses the trained model to classify URLs and return:

- Predicted class (Phishing or Legitimate).
- Phishing probability score.
- Classification threshold.

The classification threshold is configurable through the prediction implementation.

## 🧠 ML Engine Components

The Machine Learning implementation is organized inside the `ml_engine/` directory.

| File / Directory | Purpose |
|---|---|
| `train.py` | Model training and saving |
| `feature_extractor.py` | URL feature extraction |
| `predictor.py` | URL prediction using the trained model |
| `evaluation.py` | Model evaluation |
| `model/` | Stores the trained Random Forest model |
| `notebooks/` | ML experimentation and analysis |
| `results/` | Exported model evaluation results |

### Prediction Interface

The ML prediction module provides a function:

```python
from ml_engine.predictor import predict_url

result = predict_url("https://example.com")

print(result)
```

The function returns the predicted URL classification along with its phishing probability and the applied threshold.

> Note: The prediction probability is a model-generated score, not a guarantee that a URL is malicious or safe.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| Scikit-learn | Machine Learning |
| XGBoost | Gradient boosting model |
| Joblib | Model serialization |
| Google Colab | Model experimentation |
| Jupyter Notebook | ML development and analysis |
| Django | Backend web application |
| HTML/CSS | Frontend development |
| Git & GitHub | Version control |
| Git LFS | Large trained model storage |

## 📁 Project Structure

```text
PhishGuard/
│
├── datasets/
│   ├── raw/
│   │   └── processed/
│   │       ├── train_features.csv
│   │       └── test_features.csv
│   │
│   └── processed/
│
├── docs/
│
├── ml_engine/
│   ├── model/
│   │   └── random_forest.pkl
│   │
│   ├── notebooks/
│   │   └── PhishGuard_ML_Experiments.ipynb
│   │
│   ├── results/
│   │   ├── PhishGuard_Model_Comparison.csv
│   │   ├── PhishGuard_Feature_Importance.csv
│   │   └── PhishGuard_RF_Best_Parameters.csv
│   │
│   ├── train.py
│   ├── predictor.py
│   ├── feature_extractor.py
│   └── evaluation.py
│
├── PhishGuard/
│   └── Django application
│
├── scanner/
│
├── requirements.txt
├── .gitignore
├── .gitattributes
└── README.md
```

*Dataset files are maintained locally and excluded from Git tracking. The trained Random Forest model is managed using Git Large File Storage (Git LFS).*

## 🚀 Installation & Setup

### 1. Clone Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd PhishGuard
```

### 2. Install Git LFS

Git LFS is used to manage the large trained ML model.

```bash
git lfs install
git lfs pull
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Environment (Windows)

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run ML Prediction

After installing the dependencies and obtaining the trained model:

```python
from ml_engine.predictor import predict_url

result = predict_url("https://example.com")
print(result)
```

### 7. Run Django Application

The Django application and ML integration are being developed.

Once the backend implementation and configuration are complete, the application can be started using:

```bash
python manage.py runserver
```

*The Django server command must be executed from the directory containing the configured `manage.py` file.*

## 👥 Team Members

| Member | Responsibilities |
|---|---|
| Member 1 | Dataset collection, preprocessing, exploratory data analysis and feature preparation |
| Member 2 | ML model development, training, evaluation, comparison, threshold tuning and prediction interface |
| Member 3 | Django backend, authentication, database, URL scanning and ML model integration |

### Team Collaboration

The project is developed collaboratively using Git and GitHub. Individual contributions are maintained through separate development branches and integrated through pull requests.

## 📌 Project Status

**Currently in Development**

### Completed

- Dataset preparation and feature processing.
- ML model development and experimentation.
- Decision Tree, KNN, Random Forest and XGBoost evaluation.
- Model comparison and threshold analysis.
- Final Random Forest model selection.
- Model serialization and Git LFS configuration.
- ML prediction interface.
- Experimentation notebook and exported evaluation results.

### In Progress

- Django backend development.
- URL scanning functionality.
- ML model integration with the backend.
- Database and scan history functionality.
- Frontend and application integration.
- End-to-end testing and final demonstration.

## 📄 Deliverables

- Source code and GitHub repository.
- Dataset source and documentation.
- Data preprocessing and analysis.
- ML experimentation notebook.
- Model comparison and evaluation results.
- Trained Random Forest model.
- URL prediction interface.
- Django-based web application.
- Project report and demonstration.

## 📜 License

This project is developed for educational and academic purposes.
