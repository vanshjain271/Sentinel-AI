import pandas as pd
import numpy as np
import json
import joblib
import os
from datetime import datetime

from preprocessing.dataset_loader import load_dataset
from preprocessing.feature_mapper import map_features
from preprocessing.scaler_loader import load_scaler

from models.model_loader import load_models
from models.inference import run_inference

from evaluation.metrics import compute_metrics


# ---------------------------------------------------------
# Create results folders
# ---------------------------------------------------------

os.makedirs("results/metrics", exist_ok=True)
os.makedirs("results/confusion_matrices", exist_ok=True)
os.makedirs("results/tables", exist_ok=True)
os.makedirs("results/logs", exist_ok=True)


# ---------------------------------------------------------
# Helper functions to save results
# ---------------------------------------------------------

def save_metrics(model_name, metrics):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    path = f"results/metrics/{model_name}_{timestamp}.json"

    metrics_copy = metrics.copy()

    # convert confusion matrix to list for JSON
    metrics_copy["confusion_matrix"] = metrics_copy["confusion_matrix"].tolist()

    with open(path, "w") as f:
        json.dump(metrics_copy, f, indent=4)

    print(f"Saved metrics → {path}")


def save_confusion_matrix(model_name, cm):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    path = f"results/confusion_matrices/{model_name}_{timestamp}.csv"

    np.savetxt(path, cm, delimiter=",")

    print(f"Saved confusion matrix → {path}")


# ---------------------------------------------------------
# Load UNSW dataset
# ---------------------------------------------------------

train_path = "datasets/UNSW_NB15_training-set.parquet"
test_path = "datasets/UNSW_NB15_testing-set.parquet"

df_train = load_dataset(train_path)
df_test = load_dataset(test_path)

df = pd.concat([df_train, df_test], ignore_index=True)

# ---------------------------------------------------------
# Encode categorical features
# ---------------------------------------------------------

categorical_cols = df.select_dtypes(include=["object"]).columns

print("\nEncoding categorical columns:", list(categorical_cols))

for col in categorical_cols:
    df[col] = df[col].astype("category").cat.codes

print("\nCombined dataset shape:", df.shape)


# ---------------------------------------------------------
# Inspect dataset columns
# ---------------------------------------------------------

print("\nDataset columns:")
print(df.columns)


# ---------------------------------------------------------
# Load Sentinel feature list
# ---------------------------------------------------------

sentinel_features = joblib.load("../models/5g_feature_names.pkl")

print("\nSentinel model features:")
print(sentinel_features)


# ---------------------------------------------------------
# Feature mapping (basic example)
# ---------------------------------------------------------

mapping = {

    "proto": "protocol",
    "spkts": "packets_per_second",
    "sbytes": "bytes_per_second",
    "sjit": "jitter"

}

df = map_features(df, mapping)


# ---------------------------------------------------------
# Align dataset features with Sentinel features
# ---------------------------------------------------------

X = df.reindex(columns=sentinel_features, fill_value=0)

# label column
y = df["label"]
y = (y != 0).astype(int)


# ---------------------------------------------------------
# Load scaler
# ---------------------------------------------------------

scaler = load_scaler("../models/5g_ddos_scaler.pkl")

X_scaled = scaler.transform(X)


# ---------------------------------------------------------
# Load models
# ---------------------------------------------------------

models = load_models()


# ---------------------------------------------------------
# Run inference
# ---------------------------------------------------------

predictions = {}

for name, model in models.items():

    print("\nRunning model:", name)

    # skip sequence models
    if name in ["lstm", "autoencoder"]:
        print(f"Skipping {name} (requires sequence input)")
        continue

    y_pred = model.predict(X_scaled)

    predictions[name] = y_pred


# ---------------------------------------------------------
# Evaluate models
# ---------------------------------------------------------

results_summary = []

for model_name, pred in predictions.items():

    metrics = compute_metrics(y, pred)

    print("\n==============================")
    print("Model:", model_name)
    print("==============================")

    for key, value in metrics.items():
        print(f"{key}: {value}")

    # save metrics
    save_metrics(model_name, metrics)

    save_confusion_matrix(
        model_name,
        metrics["confusion_matrix"]
    )

    results_summary.append({
        "model": model_name,
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1": metrics["f1"],
        "roc_auc": metrics["roc_auc"]
    })


# ---------------------------------------------------------
# Save summary table
# ---------------------------------------------------------

summary_df = pd.DataFrame(results_summary)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

summary_path = f"results/tables/experiment_summary_{timestamp}.csv"

summary_df.to_csv(summary_path, index=False)

print("\nSaved experiment summary →", summary_path)