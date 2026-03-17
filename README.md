
# Phishing URL Detection (URL Feature Analysis)

A machine learning-based project designed to identify and classify malicious websites by analyzing the structural features of their URLs.

## 👤 Author Information
- **Name:** Nguyễn Quốc An
- **Course:** Python Programming Language
- **Institution:** University of Transport Ho Chi Minh City (UTH)

## 🎯 Project Objectives
* Build a robust dataset of over 9,100 labeled URLs (Safe vs. Phishing).
* Implement automated feature extraction from raw URL strings.
* Develop a classification model using the **Random Forest** algorithm.
* Achieve high-performance metrics (Accuracy, Precision, Recall, and F1-Score) above 90%.

## 📊 Dataset Overview
- **Sources:** PhishTank, Cloudflare Radar, and browsing history.
- **Size:** Approximately 9,171 entries.
- **Labels:** - `0`: Phishing (Malicious)
    - `1`: Safe (Benign)
- **Preprocessing:** Handled missing values and removed duplicate entries to ensure data integrity.

## 🛠 Tech Stack
- **Language:** Python 3
- **Environment:** Google Colab
- **Libraries:** - `Pandas` & `NumPy`: Data manipulation.
    - `Scikit-learn`: Model training and evaluation.
    - `Matplotlib` & `Seaborn`: Data visualization.

## 🚀 Methodology
1.  **Feature Engineering:** Extracted 26-27 key numerical features, including:
    * URL/Hostname length.
    * Count of special characters (`.`, `@`, `?`, `-`, `=`, etc.).
    * Presence of IP addresses in the URL.
    * Entropy levels and digit-to-letter ratios.
2.  **Model Training:** * Data split: 80% Training / 20% Testing.
    * Feature scaling using `StandardScaler`.
    * Algorithm: **Random Forest Classifier** (100 estimators).
3.  **Evaluation:** Used Confusion Matrix and Classification Reports to measure success.

## 📈 Results
The model demonstrated excellent performance on the test set:
* **Accuracy:** ~92.15%
* **Precision:** ~91.34%
* **Recall:** ~92.20%
* **F1-Score:** ~91.77%

## 🔚 Conclusion & Future Work
- **Conclusion:** The project successfully created a pipeline that transforms raw URLs into actionable security insights with over 92% accuracy.
- **Future Enhancements:** - Integrate the model into a real-time Browser Extension.
    - Experiment with Deep Learning architectures (CNN or LSTM).
    - Expand the dataset to include more sophisticated "zero-day" phishing attacks.

---
