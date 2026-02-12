r"""
test_enhanced_model.py
Tests ONLY the enhanced model
"""

import numpy as np
import joblib
import pickle
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from pathlib import Path

MODEL_PATH    = Path("../models/randomforest_enhanced.pkl")
SCALER_PATH   = Path("../models/scaler_enhanced.pkl")
FEATURES_PATH = Path("../models/feature_columns.pkl")

np.random.seed(42)
n_samples = 2000

normal = np.random.normal(
    loc=[60, 100, 150000, 1.67, 2500, 1500, 200, 64, 1518, 0.1, 0.05, 1, 1, 1, 1, 0, 0],
    scale=[30, 50, 75000, 0.5, 1000, 300, 100, 32, 500, 0.05, 0.02, 0, 0, 0, 0, 0, 0],
    size=(n_samples // 2, 17)
)

ddos = np.random.normal(
    loc=[30, 5000, 7500000, 166.67, 250000, 1500, 0, 1500, 1500, 0.006, 0, 1, 10, 1, 1, 0, 0],
    scale=[15, 2000, 3000000, 50, 100000, 0, 0, 0, 0, 0.002, 0, 0, 5, 0, 0, 0, 0],
    size=(n_samples // 2, 17)
)

X_test = np.vstack([normal, ddos])
X_test = np.abs(X_test)
y_test = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))

print("Loading enhanced model...")
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    with open(FEATURES_PATH, "rb") as f:
        features = pickle.load(f)
    print(f"Model LOADED | Features: {model.n_features_in_}")
except Exception as e:
    print(f"FAILED: {e}")
    exit()

X_scaled = scaler.transform(X_test)
y_pred = model.predict(X_scaled)

acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec  = recall_score(y_test, y_pred)
f1   = f1_score(y_test, y_pred)

print("\n" + "="*50)
print("ENHANCED MODEL RESULTS")
print("="*50)
print(f"Accuracy : {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall   : {rec:.4f}")
print(f"F1-Score : {f1:.4f}")
print("-"*50)
print("READY FOR app.py!")