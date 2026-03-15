from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix


def compute_metrics(y_true, y_pred):

    metrics = {}

    # Basic classification metrics
    metrics["accuracy"] = accuracy_score(y_true, y_pred)

    metrics["precision"] = precision_score(y_true, y_pred, zero_division=0)

    metrics["recall"] = recall_score(y_true, y_pred, zero_division=0)

    metrics["f1"] = f1_score(y_true, y_pred, zero_division=0)

    # ROC-AUC may fail if only one class predicted
    try:
        metrics["roc_auc"] = roc_auc_score(y_true, y_pred)
    except:
        metrics["roc_auc"] = 0.5

    # Convert confusion matrix to list for JSON saving
    cm = confusion_matrix(y_true, y_pred)
    metrics["confusion_matrix"] = cm.tolist()

    return metrics


# Wrapper used by experiment scripts
def evaluate_model(y_true, y_pred):
    return compute_metrics(y_true, y_pred)