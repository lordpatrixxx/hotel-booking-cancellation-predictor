"""Metrics and threshold selection, separated from fitting."""
import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
    balanced_accuracy_score, roc_auc_score, average_precision_score, brier_score_loss,
    confusion_matrix, roc_curve, precision_recall_curve)


def evaluate(y, probabilities, threshold=0.5):
    predicted = np.asarray(probabilities) >= threshold
    return {
        "accuracy": float(accuracy_score(y, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predicted)),
        "precision": float(precision_score(y, predicted, zero_division=0)),
        "recall": float(recall_score(y, predicted, zero_division=0)),
        "f1": float(f1_score(y, predicted, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, probabilities)),
        "average_precision": float(average_precision_score(y, probabilities)),
        "brier_score": float(brier_score_loss(y, probabilities)),
        "threshold": float(threshold),
        "confusion_matrix": confusion_matrix(y, predicted, labels=[0, 1]).tolist(),
    }


def threshold_table(y, probabilities):
    rows = []
    for cutoff in np.arange(0.1, 0.91, 0.01):
        stats = evaluate(y, probabilities, float(round(cutoff, 2)))
        stats.pop("confusion_matrix")
        rows.append(stats)
    return pd.DataFrame(rows)


def select_threshold(y, probabilities):
    curve = threshold_table(y, probabilities)
    # Tie break: larger recall, then threshold nearest 0.5. All on validation only.
    ranked = curve.assign(distance=(curve["threshold"] - .5).abs()).sort_values(["f1", "recall", "distance"], ascending=[False, False, True], kind="stable")
    return float(ranked.iloc[0]["threshold"]), curve


def probability_curves(y, probabilities):
    fpr, tpr, _ = roc_curve(y, probabilities)
    precision, recall, _ = precision_recall_curve(y, probabilities)
    # Downsample displayed curves only. Metrics always use all test observations.
    ri = np.unique(np.linspace(0, len(fpr)-1, min(200, len(fpr)), dtype=int))
    pi = np.unique(np.linspace(0, len(recall)-1, min(200, len(recall)), dtype=int))
    return {"roc": {"fpr": fpr[ri].tolist(), "tpr": tpr[ri].tolist()}, "pr": {"recall": recall[pi].tolist(), "precision": precision[pi].tolist()}}

