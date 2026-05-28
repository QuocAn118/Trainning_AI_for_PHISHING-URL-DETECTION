import numpy as np
import pandas as pd
import math
from collections import Counter
from urllib.parse import urlparse
import re
import joblib
import gradio as gr

# 1. Load models and scaler
print("Loading models and scaler...")
model_rf = joblib.load('phishing_rf_model.pkl')
model_xgb = joblib.load('phishing_xgb_model.pkl')
scaler = joblib.load('scaler.pkl')

# 2. Define feature extraction
def calculate_entropy(s):
    if not s:
        return 0
    counts = Counter(s)
    total_length = len(s)
    entropy = 0
    for count in counts.values():
        probability = count / total_length
        entropy -= probability * math.log2(probability)
    return entropy

def extract_url_features(url):
    if pd.isna(url):
        url = ""
    else:
        url = str(url)
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'buff.ly']
    tlds = [".com", ".org", ".net", ".edu", ".gov", ".us", ".uk", ".ca", ".au", ".de",
            ".fr", ".it", ".es", ".nl", ".se", ".ch", ".jp", ".cn", ".kr", ".sg", ".hk",
            ".tw", ".in", ".br", ".mx", ".ru", ".pl", ".vn", ".id", ".th", ".my", ".ph", ".za"]

    features = {
        'qty_dot': url.count('.'),
        'qty_underline': url.count('_'),
        'ip_present': 1 if ip_pattern.search(url) else 0,
        'qty_and': url.count('&'),
        'qty_questionmark': url.count('?'),
        'path_length': len(parsed.path),
        'qty_equal': url.count('='),
        'qty_at': url.count('@'),
        'qty_digits': sum(c.isdigit() for c in url),
        'qty_hyphen': url.count('-'),
        'qty_plus': url.count('+'),
        'qty_asterisk': url.count('*'),
        'qty_slash': url.count('/'),
        'qty_dollar': url.count('$'),
        'url_length': len(url),
        'hostname_length': len(hostname),
        'shortener_present': 1 if any(s in hostname for s in shorteners) else 0,
        'qty_uppercase': sum(c.isupper() for c in url),
        'qty_exclamation': url.count('!'),
        'qty_space': url.count(' '),
        'qty_hastag': url.count('#'),
        'qty_tilde': url.count('~'),
        'qty_comma': url.count(','),
        'qty_percent': url.count('%'),
        'tld_present': 1 if any(t in url for t in tlds) else 0,
        'port_present': 1 if parsed.port else 0,
        'entropy': calculate_entropy(url)
    }
    return features

# 3. Prediction function
def predict_url(url, model_choice):
    if url.strip() == "":
        return "Please enter a valid URL."

    features_dict = extract_url_features(url)
    features_array = np.array([list(features_dict.values())])
    features_scaled = scaler.transform(features_array)

    # Select model based on user input
    if model_choice == "XGBoost":
        model = model_xgb
    else:
        model = model_rf

    probabilities = model.predict_proba(features_scaled)[0]
    prob_phish = probabilities[0] * 100
    prob_safe  = probabilities[1] * 100

    pred = model.predict(features_scaled)[0]

    if pred == 1:
        return f"SAFE\n\nModel used: {model_choice}\nSafety Score: {prob_safe:.2f}%"
    else:
        return f"PHISHING WARNING!\n\nModel used: {model_choice}\nDanger Score: {prob_phish:.2f}%"

# 4. Gradio UI
ui = gr.Interface(
    fn=predict_url,
    inputs=[
        gr.Textbox(
            label="Enter the URL to check",
            placeholder="https://example.com"
        ),
        gr.Dropdown(
            choices=["Random Forest", "XGBoost"],
            value="XGBoost",
            label="Select Machine Learning Model"
        )
    ],
    outputs=gr.Textbox(label="Result"),
    title="🔍 Hệ thống kiểm tra URL an toàn",
    description="Nhập một liên kết bất kỳ và chọn mô hình phân loại để kiểm tra độ an toàn.",
)

if __name__ == '__main__':
    ui.launch()
