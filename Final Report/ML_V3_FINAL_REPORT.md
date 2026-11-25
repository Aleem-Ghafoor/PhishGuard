# PhishGuard — V3 Machine Learning Model Report

**Project:** PhishGuard — Phishing URL Detection  
**Component:** Machine Learning (ML)  
**Report scope:** V3 dataset, feature set, selected model, evaluation results, and saved artifacts  
**Selected model:** Random Forest Classifier

---

## 1. Executive Summary

PhishGuard's machine-learning component classifies submitted URLs as **Good (legitimate)** or **Bad (phishing)** using numerical features extracted from each URL.

The recorded V3 experiment used a refined dataset, a 21-feature representation, and a group-based 80/20 train/test split. The selected model was a **Random Forest Classifier**.

| Metric | V3 result |
|---|---:|
| Accuracy | **91.47%** |
| Precision | **83.50%** |
| Recall | **77.43%** |
| F1-score | **80.35%** |
| ROC-AUC | **95.90%** |
| Average Precision | **90.20%** |

The model correctly classified 17,701 phishing URLs and 75,082 legitimate URLs in the recorded confusion matrix. It missed 5,159 phishing URLs and incorrectly flagged 3,498 legitimate URLs.

These results describe the recorded V3 test set. They are not a guarantee of performance on every real-world URL or on data collected after training.

## 2. Objective

The objective of the ML component is to analyse URL characteristics and predict whether a URL belongs to one of two classes:

- **Good (0):** URL labelled legitimate in the dataset.
- **Bad (1):** URL labelled phishing in the dataset.

The model receives extracted numerical features rather than processing the URL as natural-language text.

## 3. Dataset and Evaluation Setup

The refined V3 experiment has the following recorded statistics:

| Dataset statistic | Count |
|---|---:|
| Total records | **507,194** |
| URL groups | **100,638** |
| Training records | **405,754** |
| Testing records | **101,440** |
| Train/test group overlap | **0** |

### 3.1 Class distribution

| Class | Training | Testing |
|---|---:|---:|
| Good | 314,316 | 78,580 |
| Bad | 91,438 | 22,860 |
| **Total** | **405,754** | **101,440** |

The split was 80% training and 20% testing. A group-based split was used so that related URLs assigned to the same group would not be distributed across both partitions. The recorded train/test group overlap was zero. This reduces one potential source of overly optimistic evaluation caused by related samples appearing in both partitions.

## 4. V3 Feature Set

The V3 feature set contained **21 features**. The following feature names are confirmed in the available project records:

| Feature | Purpose |
|---|---|
| `URL_Length` | Represents the length of the URL. |
| `Dot_Count` | Counts dots in the URL. |
| `Hyphen_Count` | Counts hyphens in the URL. |
| `Digit_Count` | Counts numeric digits in the URL. |
| `Special_Char_Count` | Counts selected special characters in the URL. |
| `Has_HTTPS` | Indicates whether the URL uses HTTPS. |
| `Has_Punycode` | Indicates the presence of Punycode in the URL/domain. |
| `Has_Encoded_Characters` | Indicates the presence of encoded characters. |
| `Longest_Host_Label_Length` | Measures the length of the longest host label. |

The V3 feature count was 21, but the available records confirm only the nine names above. The remaining twelve names and definitions should be copied from the committed V3 feature-extraction code before publishing a complete feature dictionary; they are intentionally not guessed here.

## 5. Model Selection

The project compared multiple classification approaches during its experiments, including:

- Decision Tree
- Random Forest
- XGBoost

K-Nearest Neighbors (KNN) was explored in earlier work but was disabled in the later comparison because of computational cost.

The model selected for the recorded V3 result was the **Random Forest Classifier**. Random Forest combines predictions from multiple decision trees. The selected model was evaluated using class-sensitive metrics, not accuracy alone.

### Why accuracy alone was not sufficient

- **Precision:** Of the URLs predicted as phishing, how many were actually phishing?
- **Recall:** Of all actual phishing URLs, how many did the model detect?
- **F1-score:** Harmonic mean of precision and recall.
- **ROC-AUC:** Measures class-separation performance across classification thresholds.
- **Average Precision:** Summarises the precision-recall curve.

Recall is especially important because a false negative means a phishing URL was classified as legitimate.

## 6. V3 Test Results

### 6.1 Classification metrics

| Metric | Score |
|---|---:|
| Accuracy | 0.9147 |
| Precision | 0.8350 |
| Recall | 0.7743 |
| F1-score | 0.8035 |
| ROC-AUC | 0.9590 |
| Average Precision | 0.9020 |

### 6.2 Confusion matrix

Class order: **Good (0), Bad (1)**. Rows represent actual labels and columns represent predicted labels.

| Actual \\ Predicted | Good | Bad |
|---|---:|---:|
| **Good** | 75,082 (TN) | 3,498 (FP) |
| **Bad** | 5,159 (FN) | 17,701 (TP) |

Interpretation:

- **TN = 75,082:** legitimate URLs correctly predicted as legitimate.
- **FP = 3,498:** legitimate URLs incorrectly predicted as phishing.
- **FN = 5,159:** phishing URLs incorrectly predicted as legitimate.
- **TP = 17,701:** phishing URLs correctly predicted as phishing.

### 6.3 Metric calculations

Using the confusion-matrix counts:

**Accuracy**  
`(TN + TP) / (TN + FP + FN + TP)`  
`(75,082 + 17,701) / 101,440 = 91.47%`

**Precision**  
`TP / (TP + FP)`  
`17,701 / (17,701 + 3,498) = 83.50%`

**Recall**  
`TP / (TP + FN)`  
`17,701 / (17,701 + 5,159) = 77.43%`

**F1-score**  
`2 × (Precision × Recall) / (Precision + Recall) = 80.35%`

Displayed metrics are rounded to two decimal places.

## 7. Threshold Evaluation

The recorded V3 default-threshold evaluation used a threshold of **0.50**. A second evaluation was recorded at **0.51**.

| Metric | Threshold 0.50 | Threshold 0.51 |
|---|---:|---:|
| Accuracy | 91.4659% | 91.4856% |
| Precision | 83.4992% | 83.9792% |
| Recall | 77.4322% | 76.8854% |
| F1-score | 80.3514% | 80.2759% |

Confusion matrix at threshold 0.51:

| Actual \\ Predicted | Good | Bad |
|---|---:|---:|
| **Good** | 75,227 | 3,353 |
| **Bad** | 5,284 | 17,576 |

At 0.51, accuracy and precision increased slightly, while recall and F1-score decreased slightly. A threshold change affects how predicted probabilities are converted into class labels; it does not, by itself, retrain the Random Forest model.

## 8. Model Artifact and Project Outputs

The recorded trained model artifact is:

`ml_engine/model/random_forest.pkl`

The ML implementation is organised around the following responsibilities. Confirm exact filenames against the current repository tree before changing paths in this report.

| Component | Responsibility |
|---|---|
| Feature extraction module | Converts a URL into the numerical feature representation expected by the model. |
| Training pipeline | Trains the selected model using prepared training data. |
| Prediction module | Loads the trained model and produces a prediction for an input URL. |
| Evaluation pipeline | Calculates classification metrics and evaluation outputs. |
| Saved model | Stores the trained Random Forest artifact as a pickle file. |

The model artifact was approximately **173 MB** in the recorded project work, so Git Large File Storage (Git LFS) was configured. The repository work included adding V3 datasets and the trained model using Git LFS.

**Verification note:** Git LFS tracking alone does not prove that a fresh clone has downloaded the full model object. Run `git lfs pull` on a clean clone and verify the model file before claiming fresh-clone reproducibility.

## 9. Findings

1. The V3 Random Forest achieved **91.47% accuracy** on the recorded test set.
2. Precision was **83.50%**, meaning that most URLs predicted as phishing were phishing examples in this test set.
3. Recall was **77.43%**; the model detected 17,701 of the 22,860 phishing test examples.
4. The model missed **5,159** phishing examples, so false negatives remain an important limitation.
5. ROC-AUC was **95.90%**, indicating strong class-separation performance across thresholds on this test set.
6. The group-based split had zero recorded group overlap between training and testing partitions, reducing one potential source of evaluation leakage.
7. Changing the threshold from 0.50 to 0.51 slightly increased precision and accuracy but reduced recall and F1-score.
8. The V3 feature set contained 21 features. The individual contribution of each feature cannot be established without feature-importance or ablation results, which are not included in the available records.

## 10. Limitations and Reproducibility Notes

- These metrics describe one recorded dataset split and do not guarantee equivalent performance on new, live, or previously unseen phishing campaigns.
- The model can produce false positives and false negatives. In particular, 5,159 phishing test examples were classified as legitimate in the recorded V3 confusion matrix.
- Dataset labels and collection methods affect model quality; this evaluation does not independently establish that every dataset label is correct.
- The complete list of 21 feature names and their exact extraction definitions should be verified against the V3 feature-extraction source code.
- Exact hyperparameter values should be read from the committed training configuration or training script. This report identifies the selected algorithm as Random Forest but intentionally omits unverified parameter values.
- For reproducibility, record the Python version, dependency versions, dataset version/checksum, random seed, split-generation procedure, training command, and Git commit used for the final model.
- For a clean checkout, install dependencies, run `git lfs pull`, and verify that the model file is the actual binary artifact rather than a Git LFS pointer file.

## 11. Conclusion

The V3 PhishGuard ML experiment used a 21-feature URL representation, a refined dataset with 507,194 records, and a group-based 80/20 train/test split. The selected Random Forest Classifier achieved **91.47% accuracy, 83.50% precision, 77.43% recall, and 80.35% F1-score** on the recorded test set.

The results indicate that the V3 model identified a substantial proportion of phishing URLs in the evaluation data. However, the remaining false negatives show that the model should be treated as a detection aid rather than a guarantee that a URL is safe. Further validation on fresh, time-separated, and independently collected URLs is recommended.

---

## Appendix A — V3 Result Snapshot

```text
Model: Random Forest Classifier
Feature count: 21
Dataset records: 507,194
Training records: 405,754
Testing records: 101,440
Train/test group overlap: 0

Accuracy:          91.47%
Precision:         83.50%
Recall:            77.43%
F1-score:          80.35%
ROC-AUC:           95.90%
Average Precision: 90.20%

TN: 75,082
FP:  3,498
FN:  5,159
TP: 17,701

Model artifact: ml_engine/model/random_forest.pkl
```

## Appendix B — Suggested Repository Placement

Suggested path:

`docs/ML_V3_FINAL_REPORT.md`

This report documents the recorded V3 experiment. Before publication, verify the complete feature list, exact source filenames, training hyperparameters, and artifact path against the final committed V3 code.
