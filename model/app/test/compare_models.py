r"""
compare_models.py
Evaluates: randomforest_enhanced.pkl (with scaler)
Shows: Accuracy, Precision, Recall, F1 on synthetic test data
"""

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from pathlib import Path

# ================================
# 1. PATHS
# ================================
ENHANCED_MODEL_PATH = Path("../models/randomforest_enhanced.pkl")
SCALER_PATH         = Path("../models/scaler_enhanced.pkl")

# ================================
# 2. GENERATE TEST DATA (same as training)
# ================================
np.random.seed(42)
n_samples = 2000

# Normal traffic
normal = np.random.normal(
    loc=[60, 100, 150000, 1.67, 2500, 1500, 200, 64, 1518, 0.1, 0.05, 1, 1, 1, 1, 0, 0],
    scale=[30, 50, 75000, 0.5, 1000, 300, 100, 32, 500, 0.05, 0.02, 0, 0, 0, 0, 0, 0],
    size=(n_samples // 2, 17)
)

# DDoS traffic
ddos = np.random.normal(
    loc=[30, 5000, 7500000, 166.67, 250000, 1500, 0, 1500, 1500, 0.006, 0, 1, 10, 1, 1, 0, 0],
    scale=[15, 2000, 3000000, 50, 100000, 0, 0, 0, 0, 0.002, 0, 0, 5, 0, 0, 0, 0],
    size=(n_samples // 2, 17)
)

X_test = np.vstack([normal, ddos])
X_test = np.abs(X_test)
y_test = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))

# ================================
# 3. LOAD MODEL + SCALER
# ================================
print("Loading enhanced model and scaler...\n")

model = joblib.load(ENHANCED_MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

print(f"Enhanced Model: LOADED ({model.n_features_in_} features)")
print(f"Scaler: LOADED")

# ================================
# 4. PREDICT
# ================================
X_scaled = scaler.transform(X_test)
y_pred = model.predict(X_scaled)

# ================================
# 5. CALCULATE METRICS
# ================================
accuracy  = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall    = recall_score(y_test, y_pred)
f1        = f1_score(y_test, y_pred)
cm        = confusion_matrix(y_test, y_pred)

# ================================
# 6. PRINT RESULTS
# ================================
print("\n" + "="*60)
print("ENHANCED MODEL PERFORMANCE (randomforest_enhanced.pkl)")
print("="*60)
print(f"{'Metric':<12} {'Score':<10} {'%'}")
print("-"*60)
print(f"{'Accuracy':<12} {accuracy:.4f}     {(accuracy*100):.2f}%")
print(f"{'Precision':<12} {precision:.4f}     {(precision*100):.2f}%")
print(f"{'Recall':<12} {recall:.4f}     {(recall*100):.2f}%")
print(f"{'F1-Score':<12} {f1:.4f}     {(f1*100):.2f}%")
print("-"*60)
print("Confusion Matrix:")
print(f"[[TN: {cm[0,0]}   FP: {cm[0,1]} ]")
print(f" [FN: {cm[1,0]}   TP: {cm[1,1]} ]]")
print("-"*60)

# ================================
# 7. RECOMMENDATION
# ================================
if accuracy >= 0.98:
    print("EXCELLENT! Model is ready for production.")
elif accuracy >= 0.95:
    print("VERY GOOD! Safe to deploy with monitoring.")
elif accuracy >= 0.90:
    print("GOOD! Test on real traffic before full use.")
else:
    print("NEEDS WORK! Retrain with more real DDoS data.")

print("\nTo use in app.py:")
print("   MODEL_PATH = \"../models/randomforest_enhanced.pkl\"")
print("   SCALER_PATH = \"../models/scaler_enhanced.pkl\"")
print("   → Load scaler and apply .transform() before predict()")