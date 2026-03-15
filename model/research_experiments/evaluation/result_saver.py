import os
import json
import pandas as pd
from datetime import datetime

BASE_RESULTS_DIR = "model/research_experiments/results"


def save_results(model_name, metrics, y_true, y_pred, dataset):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    metrics_dir = os.path.join(BASE_RESULTS_DIR, "metrics")
    cm_dir = os.path.join(BASE_RESULTS_DIR, "confusion_matrices")
    tables_dir = os.path.join(BASE_RESULTS_DIR, "tables")

    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(cm_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)

    # Save metrics JSON
    metrics_file = f"{model_name}_{timestamp}.json"
    metrics_path = os.path.join(metrics_dir, metrics_file)

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"Saved metrics → {metrics_path}")

    # Save confusion matrix
    cm_file = f"{model_name}_{timestamp}.csv"
    cm_path = os.path.join(cm_dir, cm_file)

    cm_df = pd.DataFrame(metrics["confusion_matrix"])
    cm_df.to_csv(cm_path, index=False)

    print(f"Saved confusion matrix → {cm_path}")

    # Save summary table
    summary = {
        "model": model_name,
        "dataset": dataset,
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1": metrics["f1"],
        "roc_auc": metrics["roc_auc"]
    }

    table_path = os.path.join(tables_dir, f"{model_name}_{timestamp}.csv")

    pd.DataFrame([summary]).to_csv(table_path, index=False)

    print(f"Saved summary → {table_path}")