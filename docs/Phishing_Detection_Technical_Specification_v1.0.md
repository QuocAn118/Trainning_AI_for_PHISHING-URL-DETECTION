# Phishing URL Detection AI — Technical Specification v1.0

> **Project status:** Initial technical specification  
> **Project direction:** Serious AI project → MVP → potential commercialization  
> **Core task:** Detect phishing websites using URL, domain/reputation, HTML/DOM/behavioral features  
> **Models:** XGBoost + Deep Learning  
> **Deployment target:** FastAPI + Browser Extension  
> **Data collection:** Playwright in an isolated VPS/Docker environment

---

## 1. Project Overview

### 1.1. Problem

The project aims to build an AI-powered phishing website detection system that receives a URL and determines whether the website is:

- `BENIGN` — likely legitimate
- `SUSPICIOUS` — requires additional attention
- `PHISHING` — high-risk phishing website

The system should not rely only on the visible URL. It will combine multiple information sources:

```text
URL
+
Domain information
+
PageRank / reputation
+
HTML / DOM features
+
Redirect / behavioral features
+
Raw URL and HTML representations for Deep Learning
```

### 1.2. Main objectives

1. Build a reliable phishing URL/website dataset.
2. Build a safe crawling pipeline for phishing websites.
3. Extract reproducible URL and HTML features.
4. Prevent data leakage during dataset construction and evaluation.
5. Train an XGBoost model.
6. Train a Deep Learning model using raw URL + HTML representations.
7. Compare the two models under strict evaluation protocols.
8. Build a FastAPI inference service.
9. Build a browser extension for real-world testing.
10. Prepare the architecture for later commercial development.

---

# 2. Final System Architecture

The project will use **one unified feature/data pipeline** and two model branches.

```text
                         USER
                          │
                          ▼
                  Browser Extension
                          │
                          ▼
                       FastAPI
                          │
                          ▼
                  URL / Page Analysis
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
     URL Features    Domain/Reputation   HTML/DOM
          │               │                │
          └───────────────┼────────────────┘
                          │
                          ▼
                    Feature Dataset
                          │
                ┌─────────┴─────────┐
                │                   │
                ▼                   ▼
             XGBoost          Deep Learning
                │                   │
                └─────────┬─────────┘
                          ▼
                     Evaluation
                          │
                          ▼
                    Risk Score
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
        BENIGN        SUSPICIOUS       PHISHING
```

## Important design decision

The system will **not** use the previous "AI Layer 1 → AI Layer 2" architecture as two sequential classifiers.

Instead:

- XGBoost and Deep Learning solve the same classification problem.
- Both are trained/evaluated independently.
- The final production model is selected only after empirical evaluation.
- No model is declared superior in advance.

---

# 3. Research Questions

The project should answer the following questions:

### RQ1
How effectively can URL, domain, reputation, and HTML/DOM features detect phishing websites using XGBoost?

### RQ2
Can a Deep Learning model learn useful phishing representations directly from raw URL and HTML data?

### RQ3
How does Deep Learning compare with XGBoost under:

- domain-disjoint testing;
- temporal testing;
- external/cross-dataset testing?

### RQ4
What is the trade-off between:

- detection performance;
- false positives;
- false negatives;
- inference latency;
- memory usage;
- model size?

### RQ5
Can the resulting model be deployed efficiently through an API and browser extension?

---

# 4. Dataset Strategy

## 4.1. Initial dataset

The initial target is approximately:

```text
5,000 phishing URLs
5,000 benign URLs
-------------------
10,000 URLs
```

This is the initial prototype/MVP dataset, not the final commercial dataset.

The project should later scale toward:

```text
20k
50k
100k+
```

depending on data quality, storage, crawling capacity, and model performance.

## 4.2. Required metadata

Each raw record should preserve:

```text
url
label
source
timestamp_collected
domain
registered_domain
crawl_status
http_status
final_url
redirect_count
```

Additional raw artifacts:

```text
html
response_headers
redirect_chain
```

where safely and legally collectable.

## 4.3. Data sources

Phishing and benign data should be collected from multiple sources where possible.

The source must be recorded for every sample:

```text
source = phishtank
source = tranco
source = other_dataset
source = internal_collection
...
```

Do not merge datasets and discard provenance.

---

# 5. Data Leakage Prevention

This is a core requirement of the project.

A random row-level train/test split is NOT sufficient.

## 5.1. Level 1 — Exact URL deduplication

Normalize and remove exact duplicate URLs.

Example:

```text
https://example.com/login
https://example.com/login
```

must not appear as two independent samples.

## 5.2. Level 2 — Canonical URL deduplication

Create a canonical representation to detect variants such as:

```text
https://example.com/login?a=1
https://example.com/login?a=2
https://example.com/login
```

The exact canonicalization rules must be documented and versioned.

## 5.3. Level 3 — Domain-disjoint split

This is mandatory.

All URLs belonging to the same registered domain/eTLD+1 must stay in the same partition.

Example:

```text
paypal.com/login
paypal.com/account
paypal.com/security
```

must not be distributed across:

```text
TRAIN
VALIDATION
TEST
```

Instead, the entire domain is assigned to exactly one partition.

Recommended starting protocol:

```text
70% TRAIN
15% VALIDATION
15% TEST
```

The percentages refer to domain groups, not individual URLs.

## 5.4. Level 4 — Temporal split

If timestamps are available:

```text
Older data
    ↓
TRAIN

Later data
    ↓
VALIDATION

Newest data
    ↓
TEST
```

This evaluates whether the model can detect newer phishing campaigns.

## 5.5. Level 5 — External/cross-dataset testing

Keep at least one external dataset/source completely isolated from training.

Example:

```text
Dataset A + Dataset B
        ↓
      TRAIN

Dataset C
        ↓
External TEST
```

The purpose is to measure generalization beyond the training distribution.

## 5.6. Leakage audit

Before every training run, produce a report:

```text
exact_duplicate_count
canonical_duplicate_count
shared_domain_count
shared_registered_domain_count
train_test_domain_overlap
validation_test_domain_overlap
source_overlap
temporal_overlap
```

Training must stop if forbidden overlap is detected.

---

# 6. Feature Engineering

Feature engineering will follow the Kaggle reference notebook as the initial feature baseline, then expand it with additional features.

Reference:

Phishing URL EDA and Modelling:
https://www.kaggle.com/code/akashkr/phishing-url-eda-and-modelling/notebook

---

# 7. URL Features

## 7.1. Lexical features

Initial features:

```text
url_length
domain_length
path_length
query_length
fragment_length

dot_count
hyphen_count
underscore_count
slash_count
question_mark_count
equal_count
ampersand_count
at_sign_count
percent_count

digit_count
letter_count
special_character_count

digit_ratio
special_character_ratio
```

## 7.2. Structural features

```text
subdomain_count
path_segment_count
query_parameter_count
fragment_present

has_ip_address
has_port
has_https
has_http
has_at_symbol
has_double_slash_in_path
```

## 7.3. Suspicious lexical features

Maintain a configurable keyword list.

Example categories:

```text
login
signin
verify
verification
secure
account
update
confirm
password
bank
wallet
payment
invoice
support
security
```

Do NOT hard-code the assumption that any keyword automatically means phishing.

Instead create features such as:

```text
suspicious_keyword_count
suspicious_keyword_ratio
keyword_category_count
```

---

# 8. Domain Features

Recommended features:

```text
domain_length
subdomain_count
tld
tld_length
numeric_domain
domain_entropy
```

Optional external/domain-intelligence features:

```text
domain_age
registration_period
registrar
DNS-related information
WHOIS-related information
```

These should be treated as optional because external services can introduce:

- API dependency;
- rate limits;
- cost;
- missing values;
- inference latency.

---

# 9. PageRank / Reputation Features

PageRank will be included as an additional model feature.

Initial feature:

```text
pagerank_score
```

Potential future reputation features:

```text
reputation_score
domain_popularity
external_threat_intelligence_score
```

Important:

> PageRank/reputation is evidence, not a direct phishing rule.

Do not implement:

```text
PageRank < threshold → PHISHING
```

Instead allow the ML model to learn its relationship with other features.

---

# 10. HTML / DOM Features

## 10.1. Basic structure

```text
num_forms
num_inputs
num_password_inputs
num_hidden_inputs
num_iframes
num_scripts
num_links
num_images
num_meta_tags
num_buttons
num_textareas
```

## 10.2. Form behavior

```text
has_password_field
has_login_form
form_action_external
form_action_empty
form_action_about_blank
num_external_forms
external_form_ratio
```

## 10.3. Hyperlink features

```text
num_internal_links
num_external_links
external_link_ratio
empty_href_count
javascript_href_count
anchor_to_external_ratio
```

## 10.4. External resources

```text
num_external_scripts
num_external_images
num_external_css
external_script_ratio
external_resource_ratio
```

## 10.5. DOM suspicious behavior

Potential features:

```text
hidden_element_count
meta_refresh_present
javascript_redirect_present
iframe_external_ratio
```

---

# 11. Redirect / Navigation Features

Capture:

```text
redirect_count
initial_domain
final_domain
domain_changed
initial_url
final_url
redirect_chain_length
```

Potential future features:

```text
cross_domain_redirect_count
shortener_detected
```

---

# 12. HTML Text Features

Extract visible text and relevant HTML text.

Possible features:

```text
text_length
word_count
unique_word_count
login_keyword_count
financial_keyword_count
urgency_keyword_count
credential_keyword_count
```

For the Deep Learning branch, retain the raw/cleaned HTML representation rather than reducing everything to handcrafted statistics.

---

# 13. JavaScript / Behavioral Features

The first version should collect safe, lightweight behavioral indicators.

Possible features:

```text
script_count
inline_script_count
external_script_count
obfuscated_script_indicator
location_redirect_indicator
document_write_indicator
eval_indicator
```

These are indicators, not automatic maliciousness labels.

Avoid executing suspicious JavaScript with access to sensitive host resources.

---

# 14. Crawler Architecture

## 14.1. Tool

Primary crawler:

```text
Python
+
Playwright
```

## 14.2. Execution environment

Recommended:

```text
VPS
 ↓
Docker
 ↓
Crawler container
 ↓
Playwright Chromium
```

The crawler should NOT run directly on the user's main computer.

## 14.3. Security requirements

The crawler environment should:

- run as a non-root user;
- use resource limits;
- use strict timeouts;
- avoid mounting sensitive host directories;
- contain no personal credentials;
- contain no production secrets;
- isolate browser storage;
- limit unnecessary network access;
- save only required artifacts.

## 14.4. Crawler pipeline

```text
Raw URL
   ↓
Normalize
   ↓
Open in isolated browser
   ↓
Wait for DOMContentLoaded
   ↓
Collect response status
   ↓
Collect redirects
   ↓
Extract HTML
   ↓
Extract DOM features
   ↓
Extract URL/domain features
   ↓
Save record
```

---

# 15. Crawling Strategy

Do not attempt to crawl all URLs simultaneously.

Use controlled concurrency:

```text
CONCURRENT_TASKS = 5–10
```

as the initial benchmark.

Then test:

```text
5
10
20
30
```

and record:

```text
CPU
RAM
network usage
crawl success rate
timeout rate
average latency
```

Select the concurrency level based on actual VPS behavior.

## 15.1. Timeout

Initial target:

```text
10–15 seconds per URL
```

This must be configurable.

## 15.2. Resource blocking

Block unnecessary resources when possible:

```text
images
fonts
videos
large downloads
```

However, do not block resources that are required for a feature being measured.

---

# 16. Data Schema

Recommended initial schema:

```text
sample_id
url
label
source
timestamp_collected

domain
registered_domain
tld

http_status
crawl_status
final_url
redirect_count

pagerank_score

url_length
domain_length
path_length
query_length
fragment_length

dot_count
hyphen_count
slash_count
digit_count
special_character_count
subdomain_count

has_ip_address
has_https
has_at_symbol

num_forms
num_inputs
num_password_inputs
num_hidden_inputs
num_iframes
num_scripts
num_links
num_images

num_external_links
external_link_ratio
form_action_external
num_external_forms

meta_refresh_present
javascript_redirect_present

text_length
login_keyword_count
financial_keyword_count
urgency_keyword_count

...
```

The schema should be versioned:

```text
feature_schema_version = 1.0
```

---

# 17. XGBoost Model

## 17.1. Input

XGBoost receives engineered features:

```text
URL
+
Domain
+
PageRank
+
HTML
+
DOM
+
Redirect
+
Behavioral features
```

## 17.2. Baseline

Before XGBoost, optionally train a simple baseline:

```text
Logistic Regression
```

This is only for scientific comparison.

## 17.3. XGBoost

Initial tuning parameters should be explored systematically:

```text
n_estimators
max_depth
learning_rate
subsample
colsample_bytree
min_child_weight
reg_alpha
reg_lambda
```

Use validation data or cross-validation without violating domain separation.

---

# 18. Deep Learning Model

The Deep Learning branch should not simply consume the engineered feature vector.

The main experiment should learn representations from raw data.

## 18.1. URL encoder

```text
Raw URL
   ↓
Character tokenizer
   ↓
Embedding
   ↓
CNN / Transformer encoder
   ↓
URL representation
```

## 18.2. HTML encoder

```text
Raw HTML
   ↓
HTML/text preprocessing
   ↓
Tokenizer
   ↓
Embedding
   ↓
CNN / Transformer encoder
   ↓
HTML representation
```

## 18.3. Fusion

```text
URL representation
        │
        ├───────┐
        │       │
        ▼       ▼
      URL      HTML
       │         │
       └────┬────┘
            ▼
       Fusion Layer
            ↓
       Classification
            ↓
    Phishing probability
```

The first Deep Learning implementation should remain computationally realistic for the available dataset and hardware.

---

# 19. XGBoost vs Deep Learning Experiment

Both models must use the same evaluation protocol.

Compare:

```text
Accuracy
Precision
Recall
F1
ROC-AUC
PR-AUC
FPR
FNR
Inference latency
Memory
Model size
```

Do not select the production model based on accuracy alone.

---

# 20. Evaluation Protocol

Three main evaluations:

## Experiment A — Domain-disjoint

```text
Train domains
     ≠
Validation domains
     ≠
Test domains
```

## Experiment B — Temporal

```text
Older data → TRAIN
Later data → VALIDATION
Newest data → TEST
```

## Experiment C — External dataset

```text
Internal sources → TRAIN
External source → TEST
```

The external test must not influence training or hyperparameter selection.

---

# 21. Error Analysis

After evaluation, inspect false positives and false negatives.

## False Positive

```text
Legitimate website
      ↓
Predicted phishing
```

Investigate:

- new domain;
- low reputation;
- unusual URL;
- login form;
- external resources;
- uncommon TLD;
- redirects.

## False Negative

```text
Phishing website
      ↓
Predicted benign
```

Investigate:

- clean-looking URL;
- compromised legitimate domain;
- dynamic content;
- JavaScript-based phishing;
- missing HTML features;
- unseen phishing pattern.

False-negative analysis is especially important for a security-oriented system.

---

# 22. Explainability

For XGBoost, implement explainability using feature importance and, where appropriate, SHAP.

Example output:

```text
Prediction:
PHISHING

Risk:
0.94

Important contributing signals:
- external_form_action
- suspicious_url_pattern
- redirect_chain
- iframe_count
- low_reputation
```

The explanation must be phrased as model evidence, not as absolute proof of maliciousness.

---

# 23. Risk Score

The API should return a probability/risk score rather than only a binary label.

Example:

```json
{
  "label": "PHISHING",
  "risk_score": 0.94,
  "model_version": "xgb-1.0"
}
```

Suggested product categories:

```text
0.00–0.20 → LOW RISK
0.20–0.50 → MODERATE RISK
0.50–0.80 → SUSPICIOUS
0.80–1.00 → HIGH RISK
```

These thresholds are provisional and must be calibrated using validation data. They are not automatically valid just because they are intuitive.

---

# 24. API Architecture

Backend:

```text
FastAPI
```

Suggested endpoints:

```text
POST /predict
POST /analyze
GET  /health
GET  /model-info
```

Example:

```text
POST /predict
{
    "url": "https://example.com"
}
```

Response:

```json
{
    "label": "BENIGN",
    "risk_score": 0.08,
    "model": "xgboost",
    "model_version": "1.0"
}
```

---

# 25. Browser Extension

Initial architecture:

```text
Browser
   ↓
Extension
   ↓
Current URL
   ↓
FastAPI
   ↓
AI
   ↓
Risk score
   ↓
Extension UI
```

The extension should eventually show:

```text
Website Status
----------------
✓ Low Risk

Risk Score: 0.08

Signals:
- Normal URL structure
- No suspicious form behavior
- Normal redirect behavior
```

For a high-risk site:

```text
⚠ High Risk

Risk Score: 0.94

Signals:
- External login form
- Suspicious redirect
- Unusual URL structure
```

---

# 26. Model Versioning

Every production prediction should be traceable to a model version.

Example:

```text
model_version = xgb_1.0
feature_schema_version = 1.0
dataset_version = dataset_1.0
```

Later:

```text
xgb_1.1
xgb_2.0
dl_1.0
```

Never replace a model without recording its version.

---

# 27. Data and Model Monitoring

For commercial development, monitor:

```text
prediction distribution
unknown/error rate
false-positive reports
false-negative reports
feature distribution drift
domain distribution drift
model latency
API latency
crawler failure rate
```

Potential future concept:

```text
Data Drift Detection
        ↓
Retraining trigger
        ↓
New model
        ↓
Validation
        ↓
Deployment
```

Do not automatically deploy a newly trained model without validation.

---

# 28. Project Directory

Recommended structure:

```text
phishing-detection/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── external/
│   └── splits/
│
├── crawler/
│   ├── playwright/
│   ├── docker/
│   └── configs/
│
├── features/
│   ├── url_features.py
│   ├── html_features.py
│   ├── domain_features.py
│   ├── behavior_features.py
│   └── pagerank.py
│
├── models/
│   ├── xgboost/
│   └── deep_learning/
│
├── evaluation/
│   ├── leakage_audit.py
│   ├── domain_split.py
│   ├── temporal_split.py
│   ├── external_test.py
│   └── metrics.py
│
├── api/
│   └── fastapi/
│
├── extension/
│
├── notebooks/
│
├── configs/
│
├── tests/
│
├── requirements.txt
│
└── README.md
```

---

# 29. Development Roadmap

## Phase 1 — Dataset

- Collect initial phishing URLs.
- Collect benign URLs.
- Preserve source and timestamp.
- Normalize URLs.
- Deduplicate.
- Group by registered domain.

## Phase 2 — Leakage-safe splitting

- Exact duplicate check.
- Canonical duplicate check.
- Domain overlap check.
- Train/validation/test assignment.
- Temporal split.
- External dataset holdout.

## Phase 3 — Crawler

- VPS setup.
- Docker.
- Playwright.
- Timeout.
- Concurrency control.
- HTML extraction.
- Redirect extraction.
- Safe storage.

## Phase 4 — Feature Engineering

Implement:

```text
URL features
Domain features
PageRank
HTML features
DOM features
Redirect features
Text features
```

## Phase 5 — XGBoost

- Train baseline.
- Tune hyperparameters.
- Evaluate.
- Explain model.
- Save model version.

## Phase 6 — Deep Learning

- URL tokenizer.
- URL encoder.
- HTML/text preprocessing.
- HTML encoder.
- Fusion model.
- Train.
- Evaluate.

## Phase 7 — Robustness

Run:

```text
domain-disjoint test
temporal test
external test
```

## Phase 8 — Product

- FastAPI.
- Browser Extension.
- Risk score.
- Explainability.
- Logging.
- Model versioning.

## Phase 9 — MVP

Run controlled real-world testing.

## Phase 10 — Commercialization research

Evaluate:

```text
cost per prediction
API infrastructure cost
crawler cost
model latency
false positive rate
false negative rate
update frequency
data licensing
third-party API costs
privacy requirements
```

---

# 30. Definition of Done

The project should not be considered complete merely because:

```text
Accuracy > 95%
```

The MVP is considered technically successful when:

- Dataset provenance is recorded.
- Duplicate leakage is controlled.
- Domain leakage is controlled.
- Temporal evaluation is available.
- External evaluation is available.
- XGBoost is trained and reproducible.
- Deep Learning model is trained and reproducible.
- Both models are compared using multiple metrics.
- False positives and false negatives are analyzed.
- Inference latency is measured.
- API works.
- Browser extension communicates with API.
- Model and feature versions are recorded.
- Crawling pipeline is isolated.
- Re-training can be repeated from documented data/code.

---

# 31. Long-term Commercial Architecture

Future architecture:

```text
                         Browser Extension
                                │
                                ▼
                           API Gateway
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
                 ▼              ▼              ▼
             Prediction      Cache        Monitoring
               Service
                 │
       ┌─────────┴─────────┐
       │                   │
       ▼                   ▼
    XGBoost             Deep Learning
       │                   │
       └─────────┬─────────┘
                 ▼
             Risk Engine
                 │
                 ▼
           User Explanation

Data Collection
      │
      ▼
Crawler Cluster
      │
      ▼
Feature Pipeline
      │
      ▼
Data Warehouse
      │
      ▼
Training Pipeline
      │
      ▼
Model Registry
      │
      ▼
Validation
      │
      ▼
Production Deployment
```

---

# 32. Key Principles

The project will follow these principles:

### Principle 1
**Do not optimize for a pretty accuracy number.**

### Principle 2
**Prevent data leakage before training.**

### Principle 3
**Treat PageRank as a feature, not a rule.**

### Principle 4
**XGBoost and Deep Learning must be evaluated fairly.**

### Principle 5
**Real-world generalization is more important than random test accuracy.**

### Principle 6
**Crawler security is part of the project, not an optional detail.**

### Principle 7
**Every dataset, feature schema, and model must be versioned.**

### Principle 8
**The production system should remain usable even if optional third-party intelligence services are unavailable.**

### Principle 9
**A prediction is a risk assessment, not absolute proof that a website is malicious.**

### Principle 10
**Build the research pipeline so that it can evolve into an actual product.**

---

# 33. Initial Technology Stack

```text
Language:
Python

Data:
Pandas
NumPy

Machine Learning:
XGBoost
scikit-learn

Deep Learning:
PyTorch

Web Crawling:
Playwright

Backend:
FastAPI
Uvicorn

Container:
Docker

Database:
PostgreSQL
```

Potential future infrastructure:

```text
Redis
Object Storage
MLflow
Celery / task queue
Prometheus
Grafana
```

These should only be introduced when the MVP actually needs them.

---

# 34. First Implementation Order

Do NOT start with Deep Learning.

The correct implementation order is:

```text
1. Dataset schema
        ↓
2. Dataset collection
        ↓
3. Normalization + deduplication
        ↓
4. Leakage-safe split
        ↓
5. Crawler
        ↓
6. Feature extraction
        ↓
7. Feature validation
        ↓
8. XGBoost
        ↓
9. Evaluation
        ↓
10. Deep Learning
        ↓
11. Comparative evaluation
        ↓
12. FastAPI
        ↓
13. Browser Extension
```

The first coding milestone should therefore be:

> **Build the dataset + leakage-control pipeline before training either model.**

This prevents the project from spending weeks optimizing a model on a flawed dataset.

---

# 35. Current Project Decision

The project direction is now fixed as:

```text
                  PHISHING DETECTION
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
       URL             HTML          Reputation
        │                │                │
        └────────────────┼────────────────┘
                         │
                  Feature Pipeline
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
          XGBoost              Deep Learning
             │                       │
             └───────────┬───────────┘
                         ▼
                 Robust Evaluation
                         │
                         ▼
                  Production Model
                         │
                         ▼
                   FastAPI + Web
                    Extension
```

**Final research focus:**

> Compare XGBoost using engineered URL/HTML/domain/reputation features against a Deep Learning model that learns representations from raw URL and HTML data, under leakage-safe domain, temporal, and external-dataset evaluation.

---

# 36. Immediate Next Task

The next implementation task is **Dataset Pipeline v1**.

It should produce:

```text
raw_urls.csv
        ↓
normalized_urls.csv
        ↓
deduplicated_urls.csv
        ↓
domain_groups.csv
        ↓
train.csv
validation.csv
test.csv
external_test.csv
```

Only after this pipeline passes the leakage audit should crawling and model training begin.
