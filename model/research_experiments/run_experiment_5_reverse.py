from preprocessing.load_cic_ddos import load_cic_dataset
from preprocessing.load_unsw_nb15 import load_unsw_dataset
from preprocessing.universal_feature_mapper import extract_universal_features

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

from evaluation.metrics import compute_metrics

print("\n==============================")
print("Experiment 5: Reverse Cross-Dataset Evaluation")
print("==============================\n")


# -------------------------
# TRAIN ON CIC
# -------------------------

print("Loading CIC dataset for training...")
cic_df = load_cic_dataset()

print("\nExtracting universal features (CIC)...")
X_train = extract_universal_features(cic_df)

y_train = cic_df["Label"].apply(lambda x: 0 if x == "BENIGN" else 1)

print("Feature matrix shape:", X_train.shape)


print("\nTraining RandomForest on CIC dataset...\n")

model = RandomForestClassifier(
    n_estimators=200,
    n_jobs=-1,
    random_state=42
)

model.fit(X_train, y_train)


# -------------------------
# TEST ON UNSW
# -------------------------

print("\nLoading UNSW dataset for testing...")
unsw_df = load_unsw_dataset()

print("\nExtracting universal features (UNSW)...")
X_test = extract_universal_features(unsw_df)

y_test = unsw_df["label"]

print("\nRunning cross-dataset evaluation...\n")

y_pred = model.predict(X_test)

print(classification_report(y_test, y_pred))


metrics = compute_metrics(y_test, y_pred)

import json
import pandas as pd
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

metrics_path = f"model/research_experiments/results/metrics/universal_rf_reverse_{timestamp}.json"
cm_path = f"model/research_experiments/results/confusion_matrices/universal_rf_reverse_{timestamp}.csv"
table_path = f"model/research_experiments/results/tables/universal_rf_reverse_{timestamp}.csv"

# save metrics
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=4)

# save confusion matrix
pd.DataFrame(metrics["confusion_matrix"]).to_csv(cm_path, index=False)

# save summary
summary = {
    "accuracy": metrics["accuracy"],
    "precision": metrics["precision"],
    "recall": metrics["recall"],
    "f1": metrics["f1"],
    "roc_auc": metrics["roc_auc"]
}

pd.DataFrame([summary]).to_csv(table_path, index=False)

print(f"Saved metrics → {metrics_path}")
print(f"Saved confusion matrix → {cm_path}")
print(f"Saved summary → {table_path}")