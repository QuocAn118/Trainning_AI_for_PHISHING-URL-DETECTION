import pandas as pd
import numpy as np
import math
from collections import Counter
from urllib.parse import urlparse
import re

print("Loading dataset...")
df = pd.read_csv("KhoLinkSamSetCuaQan - KhoLinkSamSetCuaQan.csv", on_bad_lines='skip')

# Clean headers and values
df.columns = [c.split(';')[0] for c in df.columns]
if 'Labels' in df.columns:
    df['Labels'] = df['Labels'].astype(str).str.split(';').str[0]
    df['Labels'] = pd.to_numeric(df['Labels'], errors='coerce')

df.drop_duplicates(inplace=True)
df.dropna(inplace=True)
df['Labels'] = df['Labels'].astype(int)

# Feature Extraction
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
        'url': url,
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

print("Extracting features for Power BI...")
results = [extract_url_features(url) for url in df['Url']]
df_features = pd.DataFrame(results)
df_features['Label'] = df['Labels'].reset_index(drop=True)

# Save to CSV
output_path = 'extracted_features.csv'
df_features.to_csv(output_path, index=False)
print(f"Successfully saved clean dataset with {df_features.shape[1]} columns to '{output_path}'")
