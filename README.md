# Phishing Detection AI

An AI-based system for detecting phishing URLs and websites using URL, domain, HTML/DOM, reputation, and behavioral signals.


---

## Overview

Phishing Detection AI is a security-focused machine learning project designed to identify potentially malicious URLs and phishing websites.

The project combines:

* URL-based features
* Domain-based features
* HTML/DOM features
* Redirect and behavioral signals
* PageRank/reputation information
* XGBoost
* Deep Learning

The long-term goal is to develop the system from a research prototype into a practical security product.

---

## Core Architecture

```text
                    URL / Website
                         │
              ┌──────────┴──────────┐
              │                     │
          URL / Domain          HTML / DOM
           Analysis              Analysis
              │                     │
              └──────────┬──────────┘
                         │
                  Feature Pipeline
                         │
              ┌──────────┴──────────┐
              │                     │
          XGBoost              Deep Learning
              │                     │
              └──────────┬──────────┘
                         │
                  Model Evaluation
                         │
                    Risk Score
                         │
                ┌────────┴────────┐
                │                 │
             BENIGN          PHISHING
                │
             SUSPICIOUS
```

The project uses XGBoost and Deep Learning as two model approaches that are trained and evaluated independently.

The final production model will be selected based on experimental results rather than assumed in advance.

---

## Main Features

### URL Analysis

The system can analyze characteristics such as:

* URL length
* Domain length
* Number of dots
* Number of hyphens
* Number of slashes
* Number of digits
* Special characters
* Subdomain count
* Query parameters
* IP-based URLs
* HTTPS
* URL entropy
* Suspicious URL patterns

### Domain Analysis

Potential domain signals include:

* Registered domain
* TLD
* Domain length
* Subdomain structure
* Numeric characters
* Domain entropy
* Domain age
* DNS-related information

### HTML / DOM Analysis

Potential website-level signals include:

* Forms
* Input fields
* Password fields
* Hidden inputs
* Iframes
* Scripts
* External resources
* External links
* External form actions
* Meta refresh
* JavaScript redirects

### Reputation / PageRank

PageRank and reputation information are treated as supporting features rather than standalone phishing rules.

### Behavioral Signals

The system may analyze:

* Redirect count
* Redirect chains
* Initial URL
* Final URL
* Domain changes during redirects

---

## Machine Learning

The project focuses on two main model families.

### XGBoost

XGBoost is used for structured and engineered features.

Example feature groups:

```text
URL
Domain
PageRank
HTML / DOM
Redirect
JavaScript
Text
```

### Deep Learning

The Deep Learning branch is intended to learn representations from raw URL and HTML content.

Conceptually:

```text
Raw URL
   │
URL Encoder
   │
   ├──────────┐
              │
Raw HTML     │
   │          │
HTML Encoder │
   │          │
   └────┬─────┘
        │
      Fusion
        │
    Classifier
        │
 Risk Probability
```

The Deep Learning model is not intended to be merely an MLP over the same engineered feature vector used by XGBoost.

---

## Data Leakage Prevention

Data leakage is treated as a critical issue in this project.

The pipeline will use:

* Exact URL deduplication
* Canonical URL deduplication
* Registered-domain grouping
* Domain-disjoint train/validation/test splitting
* Temporal evaluation where possible
* External dataset evaluation
* Leakage auditing

URLs belonging to the same registered domain should remain within the same dataset partition.

For example:

```text
example.com/login
example.com/account
example.com/security
```

should not be distributed across both training and testing datasets.

---

## Dataset Pipeline

```text
Raw Dataset
     │
     ▼
Schema Validation
     │
     ▼
URL Normalization
     │
     ▼
Exact Deduplication
     │
     ▼
Canonical Deduplication
     │
     ▼
Registered Domain Extraction
     │
     ▼
Domain Grouping
     │
     ▼
Leakage-Safe Split
     │
     ▼
Leakage Audit
     │
     ▼
Train / Validation / Test
```

The pipeline will prioritize dataset quality and reproducibility before model training.

---

## Web Crawling

HTML and website-level features require web crawling.

Planned technologies:

* Python
* Playwright
* Docker
* Linux VPS

Because phishing websites are untrusted content, crawling will be performed in an isolated environment with controlled resources and browser/network restrictions.

The crawler will be developed after the initial dataset pipeline.

---

## Evaluation

The project will not rely on accuracy alone.

Planned metrics include:

* Accuracy
* Precision
* Recall
* F1-score
* ROC-AUC
* PR-AUC
* False Positive Rate
* False Negative Rate
* Inference latency
* Memory usage
* Model size

Evaluation will include:

1. Domain-disjoint testing
2. Temporal testing
3. External dataset testing
4. False-positive analysis
5. False-negative analysis

---

## Explainability

The project aims to provide interpretable evidence for predictions.

For XGBoost, planned techniques include:

* Feature importance
* SHAP
* Per-prediction feature contribution

Example:

```text
Risk Score: 0.94

Detected signals:
- Suspicious URL structure
- Multiple subdomains
- Password input detected
- External form submission
- Redirected to another domain
```

---

## Future API

The trained model will eventually be exposed through a FastAPI backend.

Planned endpoints:

```text
GET  /health
GET  /model-info
POST /predict
POST /analyze
```

---

## Future Browser Extension

Planned workflow:

```text
User visits website
        │
        ▼
Browser Extension
        │
        ▼
FastAPI
        │
        ▼
AI Model
        │
        ▼
Risk Score
        │
        ▼
Security Result
```

---

## Technology Stack

| Component            | Technology            |
| -------------------- | --------------------- |
| Programming Language | Python                |
| Data Processing      | Pandas, NumPy         |
| Machine Learning     | XGBoost, scikit-learn |
| Deep Learning        | PyTorch               |
| Web Crawling         | Playwright            |
| Backend API          | FastAPI               |
| Server               | Linux VPS             |
| Isolation            | Docker                |
| Database             | PostgreSQL            |
| Optional Cache       | Redis                 |
| Experiment Tracking  | MLflow                |
| Monitoring           | Prometheus, Grafana   |

---

## Repository Structure

```text
phishing-detection-ai/
│
├── README.md
│
├── docs/
│   ├── Phishing_Detection_Technical_Specification_v1.0.md
│   └── ...
│
├── src/
│   ├── data_pipeline/
│   ├── crawler/
│   ├── features/
│   ├── models/
│   │   ├── xgboost/
│   │   └── deep_learning/
│   ├── evaluation/
│   └── api/
│
├── tests/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── splits/
│   └── reports/
│
├── models/
│
├── notebooks/
│
├── deployment/
│
└── extension/
```

---

## Roadmap

### Phase 1 — Dataset Pipeline

* [ ] Dataset schema
* [ ] Data ingestion
* [ ] URL normalization
* [ ] Exact deduplication
* [ ] Canonical deduplication
* [ ] Registered-domain extraction
* [ ] Domain grouping
* [ ] Leakage-safe splitting
* [ ] Leakage audit

### Phase 2 — Web Crawler

* [ ] Playwright crawler
* [ ] HTML collection
* [ ] Redirect collection
* [ ] Crawl status handling
* [ ] Docker isolation
* [ ] VPS deployment

### Phase 3 — Feature Engineering

* [ ] URL features
* [ ] Domain features
* [ ] PageRank/reputation
* [ ] HTML/DOM features
* [ ] Redirect features
* [ ] JavaScript signals
* [ ] Text features

### Phase 4 — XGBoost

* [ ] Training pipeline
* [ ] Hyperparameter tuning
* [ ] Probability calibration
* [ ] Domain-disjoint evaluation
* [ ] Temporal evaluation
* [ ] External evaluation
* [ ] SHAP analysis

### Phase 5 — Deep Learning

* [ ] URL tokenizer
* [ ] HTML preprocessing
* [ ] URL encoder
* [ ] HTML encoder
* [ ] Feature fusion
* [ ] Training
* [ ] Evaluation

### Phase 6 — Robustness

* [ ] Error analysis
* [ ] False-positive analysis
* [ ] False-negative analysis
* [ ] Distribution-shift testing
* [ ] Adversarial/obfuscation cases
* [ ] Model monitoring

### Phase 7 — Product MVP

* [ ] FastAPI
* [ ] Risk scoring
* [ ] Prediction explanation
* [ ] Browser extension
* [ ] Model versioning
* [ ] Monitoring

### Phase 8 — Commercialization Research

* [ ] Dataset licensing review
* [ ] Third-party API licensing
* [ ] Dependency license review
* [ ] Security review
* [ ] Infrastructure cost analysis
* [ ] Privacy requirements
* [ ] Product validation

---

## License

License: **To be determined**

Before commercial deployment, dataset licenses, crawling terms, third-party API terms, open-source dependency licenses, and applicable privacy/security requirements must be reviewed.
