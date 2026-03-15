import sys
import os
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATASET_DIR = os.path.join(BASE_DIR, "datasets")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

METRICS_DIR = os.path.join(RESULTS_DIR, "metrics")
CM_DIR = os.path.join(RESULTS_DIR, "confusion_matrices")
TABLE_DIR = os.path.join(RESULTS_DIR, "tables")

os.makedirs(METRICS_DIR, exist_ok=True)
os.makedirs(CM_DIR, exist_ok=True)
os.makedirs(TABLE_DIR, exist_ok=True)

train_path = os.path.join(DATASET_DIR, "UNSW_NB15_training-set.parquet")
test_path = os.path.join(DATASET_DIR, "UNSW_NB15_testing-set.parquet")

print("Loading UNSW dataset...")
print("Train path:", train_path)
print("Test path:", test_path)

# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df_train = pd.read_parquet(train_path)
df_test = pd.read_parquet(test_path)

df = pd.concat([df_train, df_test], axis=0)

print("Dataset shape:", df.shape)

# --------------------------------------------------
# Data Cleaning
# --------------------------------------------------

# Replace '-' placeholder
df = df.replace("-", pd.NA)

# Convert categorical dtype to string
for col in df.select_dtypes(include=["category"]).columns:
    df[col] = df[col].astype("string")

# Target
y = df["label"]

# Features
X = df.drop(columns=["label", "attack_cat"], errors="ignore")

# Numeric columns
num_cols = X.select_dtypes(include=["number"]).columns
X[num_cols] = X[num_cols].fillna(0)

# String columns
str_cols = X.select_dtypes(include=["object", "string"]).columns
X[str_cols] = X[str_cols].fillna("unknown")

# Encode categorical
for col in str_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))

print("Feature shape:", X.shape)

# --------------------------------------------------
# Train / Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# --------------------------------------------------
# Train Models
# --------------------------------------------------

print("Training models...")

rf = RandomForestClassifier(
    n_estimators=100,
    n_jobs=-1,
    random_state=42
)

xgb = XGBClassifier(
    tree_method="hist",
    eval_metric="logloss",
    random_state=42
)

rf.fit(X_train, y_train)
xgb.fit(X_train, y_train)

# --------------------------------------------------
# Evaluation
# --------------------------------------------------

print("Evaluating models...")

timestamp = time.strftime("%Y%m%d_%H%M%S")

models = {
    "rf": rf,
    "xgb": xgb
}

summary_rows = []

for name, model in models.items():

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, preds)
    precision = precision_score(y_test, preds)
    recall = recall_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    roc = roc_auc_score(y_test, probs)

    cm = confusion_matrix(y_test, preds)

    print("\n==============================")
    print("Model:", name)
    print("==============================")
    print("accuracy:", acc)
    print("precision:", precision)
    print("recall:", recall)
    print("f1:", f1)
    print("roc_auc:", roc)

    # -----------------------------
    # Save metrics JSON
    # -----------------------------

    metrics = {
        "model": name,
        "dataset": "UNSW-NB15",
        "experiment": "baseline_training",
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc
    }

    metrics_path = os.path.join(
        METRICS_DIR,
        f"{name}_unsw_baseline_{timestamp}.json"
    )

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print("Saved metrics →", metrics_path)

    # -----------------------------
    # Save confusion matrix
    # -----------------------------

    cm_df = pd.DataFrame(cm)

    cm_path = os.path.join(
        CM_DIR,
        f"{name}_unsw_baseline_{timestamp}.csv"
    )

    cm_df.to_csv(cm_path, index=False)

    print("Saved confusion matrix →", cm_path)

    # Add to summary
    summary_rows.append({
        "Model": name,
        "Accuracy": acc,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ROC-AUC": roc
    })

# --------------------------------------------------
# Save summary table
# --------------------------------------------------

summary_df = pd.DataFrame(summary_rows)

summary_path = os.path.join(
    TABLE_DIR,
    f"experiment2_unsw_baseline_{timestamp}.csv"
)

summary_df.to_csv(summary_path, index=False)

print("\nSaved experiment summary →", summary_path)