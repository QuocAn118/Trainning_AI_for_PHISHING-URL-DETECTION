import re
import math
from collections import Counter
from urllib.parse import urlparse

import joblib
import numpy as np
from flask import Flask, render_template, request

# ----------------------------------------------------------------------
# 1. Load mô hình và bộ chuẩn hóa đã lưu từ notebook
# ----------------------------------------------------------------------
model = joblib.load("model_xgb.pkl")
scaler = joblib.load("scaler.pkl")


# ----------------------------------------------------------------------
# 2. Hàm trích xuất đặc trưng — PHẢI giống hệt hàm trong notebook
#    (cùng thứ tự cột, cùng cách tính) thì model mới dự đoán đúng
# ----------------------------------------------------------------------
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
    url = "" if url is None else str(url)
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
        'entropy': calculate_entropy(url),
    }
    return features


def predict_url(url):
    features_dict = extract_url_features(url)
    features_array = np.array([list(features_dict.values())])
    features_scaled = scaler.transform(features_array)

    probabilities = model.predict_proba(features_scaled)[0]
    prob_phish = probabilities[0] * 100   # nhãn 0 = Phishing
    prob_safe = probabilities[1] * 100    # nhãn 1 = Safe
    pred = int(model.predict(features_scaled)[0])

    if pred == 1:
        return {"label": "AN TOÀN", "safe": True, "score": round(prob_safe, 2)}
    else:
        return {"label": "CẢNH BÁO PHISHING", "safe": False, "score": round(prob_phish, 2)}


# ----------------------------------------------------------------------
# 3. Flask web app
# ----------------------------------------------------------------------
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    url = ""
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if url:
            result = predict_url(url)
    return render_template("index.html", result=result, url=url)


if __name__ == "__main__":
    app.run(debug=True)
