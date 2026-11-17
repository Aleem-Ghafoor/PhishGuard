
# 🛡️ PhishGuard – AI-Based Phishing URL Detection

PhishGuard is an AI/ML-based web application designed to detect potentially malicious and phishing URLs. It analyzes URL characteristics and uses Machine Learning models to classify URLs as **Safe** or **Phishing**.

The goal is to help users identify suspicious URLs and reduce the risk of phishing attacks.

## 🎯 Problem Statement

Phishing attacks are a common cybersecurity threat. Attackers create fake websites and malicious URLs to steal sensitive information such as passwords, financial details, and personal data.

PhishGuard aims to address this problem by using Machine Learning techniques to analyze URL features and predict whether a URL is legitimate or potentially malicious.

## ✨ Key Features

- URL-based phishing detection.
- Machine Learning-based classification.
- URL feature extraction and analysis.
- Data preprocessing and exploratory data analysis.
- Comparison of multiple ML models.
- Safe and Phishing prediction results.
- Django-based web application (planned).

## 📊 Dataset

The project uses a dataset containing:

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

**Dataset Source:[archive.ics.uci.edu/dataset/967/phiusil%2Bphishing%2Burl%2Bdataset](https://archive.ics.uci.edu/dataset/967/phiusil%2Bphishing%2Burl%2Bdataset)**

> Note: Dataset files are excluded from this GitHub repository to keep it lightweight. Download the dataset from the source link above.

## ⚙️ Project Workflow

1. Problem Definition
2. Dataset Collection
3. Data Preprocessing
   - Handling missing values
   - Removing duplicates
   - Encoding categorical variables
   - Feature scaling (if required)
4. Exploratory Data Analysis (EDA)
5. Model Training
6. Model Evaluation
7. Model Comparison
8. Best Model Selection
9. Django Web Application Integration

## 🤖 Machine Learning Models

We will train and evaluate 2–4 suitable Machine Learning models.

Model performance will be compared using:

- Accuracy
- Precision
- Recall
- F1-Score
- Confusion Matrix

The best-performing model will be selected based on appropriate evaluation metrics.

## 🛠️ Technologies Used

| Technology       | Purpose                   |
| ---------------- | ------------------------- |
| Python           | Main programming language |
| Pandas           | Data manipulation         |
| NumPy            | Numerical operations      |
| Matplotlib       | Data visualization        |
| Seaborn          | Statistical visualization |
| Scikit-learn     | Machine Learning          |
| Jupyter Notebook | Model development         |
| Django           | Web application           |
| HTML/CSS         | Frontend development      |
| Git & GitHub     | Version control           |

## 📁 Project Structure

```text
PhishGuard/
│
├── datasets/
│   ├── raw/
│   └── processed/
│
├── requirements.txt
├── .gitignore
└── README.md
```

*Dataset folders are maintained locally and excluded from Git tracking.*

## 🚀 Installation & Setup

### 1. Clone Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd PhishGuard
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Environment (Windows)

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Django Application

```bash
python manage.py runserver
```

*The Django application will be available after its implementation and configuration.*

## 👥 Team Members

| Member   | Responsibilities                               |
| -------- | ---------------------------------------------- |
| Member 1 | Dataset, preprocessing and EDA                 |
| Member 2 | Machine Learning model training and evaluation |
| Member 3 | Django web application and model integration   |

## 📌 Project Status

**Currently in Development**

The project is being developed in phases, including dataset analysis, preprocessing, model training, evaluation, and web application integration.

## 📄 Deliverables

- Source code (GitHub repository)
- Dataset source link
- Project documentation/report
- Trained Machine Learning model
- Working web application
- Project demonstration

## 📜 License

This project is developed for educational and academic purposes.
