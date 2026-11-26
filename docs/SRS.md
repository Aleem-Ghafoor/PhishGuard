# PhishGuard
## Software Requirements Specification (SRS)

**Version:** 1.0  
**Date:** 17 November 2026  
**Status:** Draft

## 1. Introduction

### 1.1 Purpose
PhishGuard is an AI-powered web application intended to identify potentially malicious phishing URLs using Machine Learning. It helps users assess whether a submitted URL appears phishing-related or legitimate.

### 1.2 Scope
The initial release (MVP) will allow guests and registered users to submit URLs for analysis. The system will validate the input, extract URL-based features, pass those features to a trained ML model, and display a classification with a confidence score. Registered users will be able to review their scan history.

### 1.3 Target Users
- **Guest:** Can submit URLs and view scan results.
- **Registered user:** Can scan URLs and access their own scan history.
- **Administrator:** Can manage user accounts and access Django administration functions.

### 1.4 Definitions and Abbreviations
| Term | Definition |
|---|---|
| Phishing | An attempt to deceive users into disclosing sensitive information |
| URL | Uniform Resource Locator |
| ML | Machine Learning |
| Classification | Assigning an input to a predefined category |
| Feature extraction | Converting input characteristics into model-ready values |
| False positive | A legitimate URL classified as phishing |
| False negative | A phishing URL classified as legitimate |
| SRS | Software Requirements Specification |

## 2. System Overview

PhishGuard is a web application built with Django and a separate ML component.

### 2.1 High-Level Workflow
1. A user submits a URL.
2. The application validates the URL format.
3. The feature-extraction component derives URL-based features.
4. The trained ML model predicts a class.
5. The application displays the prediction and model score.
6. The scan and prediction are stored according to the scan-history rules.

The initial version analyzes the URL string only. It does not automatically visit or execute the submitted URL.

## 3. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system shall accept a URL from a guest or registered user. |
| FR-02 | The system shall validate submitted URL input. |
| FR-03 | The system shall extract the URL features required by the selected ML model. |
| FR-04 | The system shall classify valid submissions using a trained ML model. |
| FR-05 | The system shall display a Phishing or Legitimate prediction. |
| FR-06 | The system shall display a model score with a clear explanation of what the score represents. |
| FR-07 | The system shall store scan records. |
| FR-08 | The system shall allow users to register, log in, and log out. |
| FR-09 | The system shall allow authenticated users to view only their own scan history. |
| FR-10 | The system shall provide authorized administrators with user-management functionality. |

## 4. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | The system should return a result within 3 seconds under a documented test environment and workload. |
| NFR-02 | Passwords shall be handled through Django's secure password-hashing facilities. |
| NFR-03 | Users shall not be able to access another user's private scan history. |
| NFR-04 | The application shall separate presentation, business logic, data access, and ML logic. |
| NFR-05 | Invalid input and operational failures shall be handled without an unhandled application crash. |
| NFR-06 | The ML model shall be evaluated using suitable metrics, including precision, recall, F1-score, and a confusion matrix. |
| NFR-07 | The application shall be structured to support future feature expansion. |
| NFR-08 | User-facing errors shall not expose secrets, stack traces, or sensitive implementation details. |

## 5. System Constraints

- Python is the primary programming language.
- Django is the web framework.
- Scikit-learn is the initial ML framework.
- SQLite is the initial development database.
- The initial MVP focuses on URL-based phishing classification.
- The ML model requires a suitable labeled dataset.
- Submitted URLs shall not be automatically visited, fetched, or executed by the initial scanner.
- A model prediction is an estimate and is not a guarantee that a website is safe or malicious.

## 6. Assumptions and Dependencies

### 6.1 Assumptions
- Users can access the web application through a supported browser.
- Users submit URLs for analysis.
- A suitable labeled dataset can be obtained and reviewed.
- The selected model can be trained on URL-derived features.
- Users understand that automated predictions can be incorrect.

### 6.2 Dependencies
- Python runtime.
- Django.
- Scikit-learn.
- Pandas and NumPy.
- Joblib for model persistence.
- SQLite for initial development.
- A labeled phishing URL dataset.

## 7. External Interface Requirements

### 7.1 User Interface
The application shall provide:
- Home page and URL submission form.
- Scan result page or result section.
- Registration and login pages.
- Scan history page for authenticated users.
- User dashboard.
- Administrative interface.

### 7.2 Software Interfaces
- Django views/services shall invoke the ML prediction module.
- The feature extractor shall prepare model input in the exact feature order expected by the model.
- The prediction module shall load a compatible trained model.
- Django ORM shall handle database operations.
- SQLite shall store application data during initial development.

### 7.3 Communication Interfaces
- The application shall use standard HTTP requests and responses.
- HTTPS shall be configured for production deployment.

## 8. Use Case Descriptions

| Use Case | Actor | Description |
|---|---|---|
| Register | Guest | Create an account |
| Login | Registered user / Admin | Authenticate |
| Scan URL | Guest / Registered user | Submit a URL for analysis |
| View result | Guest / Registered user | View classification and score |
| View history | Registered user | View their own previous scans |
| Logout | Registered user / Admin | End the authenticated session |
| Manage users | Admin | Manage accounts through authorized administration functions |

### 8.1 Use Case: Scan URL
**Primary actors:** Guest, Registered user

**Preconditions:**
- The application is available.
- The actor has a URL to submit.

**Main flow:**
1. The actor opens the scanner page.
2. The actor enters a URL.
3. The actor submits the form.
4. The system validates the input.
5. The system extracts the required URL features.
6. The ML model generates a prediction.
7. The system displays the class and score.
8. The system stores the scan according to the user's account status and retention rules.

**Alternative flows:**
- If input is empty or malformed, the system displays a validation message.
- If feature extraction fails, the system reports that the URL could not be analyzed.
- If the model is unavailable or prediction fails, the system displays a service error and does not fabricate a result.

**Postconditions:**
- A successful scan has a recorded result.
- A registered user's scan is associated with that user.
- Guest scan retention follows the application's configured policy.

## 9. User Stories

| ID | User Story |
|---|---|
| US-01 | As a guest, I want to scan a URL without registering so that I can quickly assess a suspicious link. |
| US-02 | As a user, I want to know whether a URL is predicted to be phishing or legitimate. |
| US-03 | As a user, I want to see the model score alongside the prediction. |
| US-04 | As a registered user, I want to view my previous scans. |
| US-05 | As a guest, I want to create an account to access personalized features. |
| US-06 | As an administrator, I want to manage user accounts. |
| US-07 | As a user, I want clear feedback when a submitted URL cannot be analyzed. |

## 10. Acceptance Criteria

| ID | Acceptance criterion |
|---|---|
| AC-01 | A non-empty URL can be submitted through the scanner form. |
| AC-02 | Empty or malformed input produces a validation message. |
| AC-03 | A valid input is passed to feature extraction using the expected feature schema. |
| AC-04 | A successful model inference returns one of the supported classes. |
| AC-05 | The result page displays the class and a clearly labeled model score. |
| AC-06 | An authenticated user can view their own scan records. |
| AC-07 | An authenticated user cannot access another user's scan records. |
| AC-08 | A user can register, log in, and log out successfully. |
| AC-09 | User-management functions are restricted to authorized administrators. |
| AC-10 | Model or database failures are handled without exposing sensitive details or displaying a fabricated prediction. |

## 11. Data Requirements

### 11.1 User Data
The application shall use Django's built-in User model initially. Relevant fields include user ID, username, email, password hash, and date joined.

### 11.2 Scan Data
- Scan ID.
- Submitted URL.
- Optional user reference for guest scans.
- Scan timestamp.
- Scan status.

### 11.3 Prediction Data
- Prediction ID.
- Scan reference.
- Predicted class.
- Model score.
- Model version.
- Creation timestamp.

### 11.4 Data Rules
- Each scan shall have a unique identifier.
- Registered-user scans shall be associated with the submitting user.
- Passwords shall not be stored in plain text.
- A failed scan shall not be represented as a successful prediction.
- The model score shall have a documented meaning and valid range.

## 12. Error Handling Requirements

- Empty input shall produce a validation message.
- Malformed URLs shall be rejected safely.
- Feature-extraction failures shall be reported.
- Model-loading and prediction failures shall be handled gracefully.
- Database failures shall not expose internal details.
- Unexpected input shall not cause the application to execute submitted content.

## 13. Security Requirements

- Django authentication shall be used for account functionality.
- Django password hashing shall be used; passwords shall never be stored in plain text.
- CSRF protection shall remain enabled for applicable forms.
- User input shall be validated.
- Scan-history queries shall enforce ownership checks.
- Administrative functionality shall require appropriate permissions.
- Secret keys and credentials shall be kept outside source control.
- The initial scanner shall analyze URL strings without automatically fetching or executing them.
- Production deployment shall use HTTPS and secure settings.

## 14. Requirement Traceability Matrix

| Functional requirement | Acceptance criteria |
|---|---|
| FR-01 | AC-01 |
| FR-02 | AC-02 |
| FR-03 | AC-03 |
| FR-04 | AC-04 |
| FR-05 | AC-04, AC-05 |
| FR-06 | AC-05 |
| FR-07 | AC-06 |
| FR-08 | AC-08 |
| FR-09 | AC-06, AC-07 |
| FR-10 | AC-09 |

## 15. Out of Scope

The following features are excluded from the initial MVP:
- Browser extension.
- Native mobile application.
- Email phishing detection.
- Real-time network traffic monitoring.
- Automatic website blocking.
- Website content inspection.
- Enterprise security integrations.

These may be considered for future versions.

## 16. Future Enhancements

Potential future improvements include:
- Browser extension integration.
- Email phishing detection.
- Additional ML algorithms and model comparison.
- Integration with reputable URL threat-intelligence sources.
- Detailed scan reports.
- API access for third-party applications.

## 17. Revision History

| Version | Date | Description |
|---|---|---|
| 1.0 | 17 November 2026 | Initial SRS draft |

---

**End of Document**


## 10.1 Scanner protections added in PR #27

- The public POST scan endpoint is limited to 10 requests per client IP per 60-second window; excess requests receive HTTP 429.
- URL validation checks HTTP/HTTPS scheme, hostname, malformed URL syntax, and port syntax/range before model inference.
- Unexpected scan exceptions are logged server-side; clients receive a generic error response.
- The development cache uses Django local-memory cache. A shared cache is required for consistent limits across multiple workers or application instances.
- Automated scanner tests have been added, but PR #27 states they have not yet been executed locally. Test coverage must not be represented as a passing test run until executed.
