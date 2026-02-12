"""
train_model.py
Generates:
  - ../models/randomforest_enhanced.pkl
  - ../models/scaler_enhanced.pkl
  - ../models/feature_columns.pkl

Run: python model/app/train_model.py
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import pickle
from pathlib import Path

# -------------------------------
# 1. Feature columns (MUST match ml_detection.py)
# -------------------------------
FEATURE_COLUMNS = [
    'duration', 'total_packets', 'total_bytes', 'packets_per_second',
    'bytes_per_second', 'avg_packet_size', 'std_packet_size',
    'min_packet_size', 'max_packet_size', 'avg_iat', 'std_iat',
    'unique_src_ports', 'unique_dst_ports', 'unique_protocols',
    'is_tcp', 'is_udp', 'is_icmp'
]

# -------------------------------
# 2. Generate synthetic data
# -------------------------------
np.random.seed(42)
n_samples = 10000

# Normal traffic
normal = np.random.normal(
    loc=[60, 100, 150000, 1.67, 2500, 1500, 200, 64, 1518, 0.1, 0.05, 1, 1, 1, 1, 0, 0],
    scale=[30, 50, 75000, 0.5, 1000, 300, 100, 32, 500, 0.05, 0.02, 0, 0, 0, 0, 0, 0],
    size=(n_samples // 2, len(FEATURE_COLUMNS))
)

# DDoS traffic
ddos = np.random.normal(
    loc=[30, 5000, 7500000, 166.67, 250000, 1500, 0, 1500, 1500, 0.006, 0, 1, 10, 1, 1, 0, 0],
    scale=[15, 2000, 3000000, 50, 100000, 0, 0, 0, 0, 0.002, 0, 0, 5, 0, 0, 0, 0],
    size=(n_samples // 2, len(FEATURE_COLUMNS))
)

X = np.vstack([normal, ddos])
X = np.abs(X)
y = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))

# -------------------------------
# 3. Train model
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train_scaled, y_train)

accuracy = model.score(X_test_scaled, y_test)
print(f"Model Accuracy: {accuracy:.4f}")

# -------------------------------
# 4. Save to ../models/
# -------------------------------
MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_DIR.mkdir(exist_ok=True)

joblib.dump(model, MODEL_DIR / "randomforest_enhanced.pkl")
joblib.dump(scaler, MODEL_DIR / "scaler_enhanced.pkl")
with open(MODEL_DIR / "feature_columns.pkl", "wb") as f:
    pickle.dump(FEATURE_COLUMNS, f)

print(f"Model saved to: {MODEL_DIR}")