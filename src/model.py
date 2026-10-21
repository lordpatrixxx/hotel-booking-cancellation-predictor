"""Serializable sklearn pipelines. No external service or model-upload endpoint."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from .config import NUMERIC, CATEGORICAL, SEED
from .features import make_features, validate_bookings


def make_pipeline(estimator):
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessing = ColumnTransformer([("numeric", numeric, NUMERIC), ("categorical", categorical, CATEGORICAL)])
    return Pipeline([("preprocess", preprocessing), ("classifier", estimator)])


def candidates():
    return {
        "Majority baseline": make_pipeline(DummyClassifier(strategy="most_frequent")),
        "Logistic regression": make_pipeline(LogisticRegression(max_iter=1500, C=1.0, random_state=SEED)),
        "Random forest": make_pipeline(RandomForestClassifier(n_estimators=140, max_depth=16, min_samples_leaf=5, n_jobs=4, random_state=SEED)),
        "Gradient boosting": make_pipeline(HistGradientBoostingClassifier(max_iter=180, max_leaf_nodes=23, learning_rate=0.08, l2_regularization=2.0, early_stopping=False, random_state=SEED)),
    }


def score_bookings(bundle, frame, threshold=None):
    cutoff = bundle["threshold"] if threshold is None else float(threshold)
    if not np.isfinite(cutoff) or not 0 < cutoff < 1:
        raise ValueError("Threshold must be strictly between 0 and 1.")
    rows, warnings = validate_bookings(frame, bundle.get("known_categories"))
    probabilities = bundle["pipeline"].predict_proba(make_features(rows))[:, 1]
    result = rows.copy()
    result.insert(0, "input_row", np.arange(1, len(rows) + 1))
    result["cancellation_probability"] = probabilities
    result["prediction"] = np.where(probabilities >= cutoff, "Likely cancelled", "Likely not cancelled")
    result["review_flag"] = probabilities >= cutoff
    result["threshold"] = cutoff
    return result, warnings

