import pandas as pd
import numpy as np
import math
from collections import Counter
from urllib.parse import urlparse
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import joblib

# 1. Load dataset
print("Loading dataset...")
df = pd.read_csv("KhoLinkSamSetCuaQan - KhoLinkSamSetCuaQan.csv", on_bad_lines='skip')

# Clean headers and values (handles trailing semicolons)
df.columns = [c.split(';')[0] for c in df.columns]
if 'Labels' in df.columns:
    df['Labels'] = df['Labels'].astype(str).str.split(';').str[0]
    df['Labels'] = pd.to_numeric(df['Labels'], errors='coerce')

# 2. Preprocess
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)
df['Labels'] = df['Labels'].astype(int)

# 3. Feature Extraction
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

print("Extracting features...")
results = [extract_url_features(url) for url in df['Url']]
df_features = pd.DataFrame(results)
df_features['Label'] = df['Labels'].reset_index(drop=True)

# 4. Split and Scale
X = df_features.drop(['Label'], axis=1)
Y = df_features['Label']
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# 5. Train Random Forest
print("Training Random Forest Model...")
model_rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model_rf.fit(X_train_scaled, Y_train)

# 6. Train XGBoost
print("Training XGBoost Model...")
model_xgb = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric='logloss'
)
model_xgb.fit(X_train_scaled, Y_train)

# 7. Save
print("Saving models and scaler...")
joblib.dump(model_rf, 'phishing_rf_model.pkl')
joblib.dump(model_xgb, 'phishing_xgb_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("Successfully trained and saved RF and XGBoost models!")
