from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix

def compute_metrics(y_true, y_pred):

    metrics = {}

    metrics["accuracy"] = accuracy_score(y_true, y_pred)

    metrics["precision"] = precision_score(y_true, y_pred)

    metrics["recall"] = recall_score(y_true, y_pred)

    metrics["f1"] = f1_score(y_true, y_pred)

    metrics["roc_auc"] = roc_auc_score(y_true, y_pred)

    metrics["confusion_matrix"] = confusion_matrix(y_true, y_pred)

    return metrics