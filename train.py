r"""Run: .venv\Scripts\python.exe train.py. No test-based model selection."""
from __future__ import annotations
import json
import hashlib
import platform
import time
from datetime import datetime, timezone
import importlib.metadata as pkg
import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.calibration import calibration_curve
from src.config import ROOT, RAW, DATA, ARTIFACTS, REPORTS, MODEL_PATH, METADATA_PATH, CATEGORICAL, FEATURES, INPUT_FIELDS, EXCLUDED, SEED
from src.data import download_dataset, load_data, chronological_split, sha256_file
from src.features import make_features
from src.model import candidates
from src.evaluation import evaluate, select_threshold, probability_curves


def train_all(progress=print):
    started = time.time()
    for folder in [ARTIFACTS, REPORTS, DATA / "samples"]:
        folder.mkdir(parents=True, exist_ok=True)
    progress("Reading and checking the original hotel dataset…")
    download_dataset()
    data = load_data()
    # Zero-guest / zero-night rows and negative prices are not usable overnight bookings.
    # Keep exact duplicate-looking bookings: no booking ID exists to prove duplication.
    invalid = (data["total_guests"] < 1) | (data["total_nights"] < 1) | (data["adr"] < 0) | data["arrival_date"].isna()
    eligible = data.loc[~invalid].copy()
    groups = chronological_split(eligible)
    X = {name: make_features(part) for name, part in groups.items()}
    y = {name: part["is_canceled"].astype(int) for name, part in groups.items()}
    models = candidates()
    validation_scores = {}
    for name, pipeline in models.items():
        progress(f"Training {name.lower()}…")
        pipeline.fit(X["train"], y["train"])
        probabilities = pipeline.predict_proba(X["validation"])[:, 1]
        validation_scores[name] = evaluate(y["validation"], probabilities)
    # Fixed selection rule, no peeking at future test scores.
    selected = max([n for n in models if n != "Majority baseline"], key=lambda n: (validation_scores[n]["roc_auc"], -validation_scores[n]["brier_score"]))
    pipeline = models[selected]
    validation_probs = pipeline.predict_proba(X["validation"])[:, 1]
    cutoff, thresholds = select_threshold(y["validation"], validation_probs)
    thresholds.to_csv(REPORTS / "validation_thresholds.csv", index=False)
    progress(f"Evaluating the held-out future period with {selected.lower()}…")
    test_probs = pipeline.predict_proba(X["test"])[:, 1]
    test_metrics = evaluate(y["test"], test_probs, cutoff)
    comparison = []
    for name, candidate in models.items():
        vp = candidate.predict_proba(X["validation"])[:, 1]
        tp = candidate.predict_proba(X["test"])[:, 1]
        row = {"model": name, "selected": name == selected}
        row.update({f"validation_{key}": value for key, value in validation_scores[name].items() if key not in ["confusion_matrix", "threshold"]})
        row.update({f"test_{key}": value for key, value in evaluate(y["test"], tp).items() if key not in ["confusion_matrix", "threshold"]})
        comparison.append(row)
    pd.DataFrame(comparison).to_csv(REPORTS / "model_comparison.csv", index=False)
    progress("Measuring validation feature importance…")
    sample = X["validation"].sample(min(2000, len(X["validation"])), random_state=SEED)
    importance = permutation_importance(pipeline, sample, y["validation"].loc[sample.index], n_repeats=3, random_state=SEED, scoring="roc_auc", n_jobs=1)
    imp = pd.DataFrame({"feature": FEATURES, "auc_decrease": importance.importances_mean, "std": importance.importances_std}).sort_values("auc_decrease", ascending=False)
    imp.to_csv(REPORTS / "feature_importance.csv", index=False)
    partitions = {}
    for name, part in groups.items():
        partitions[name] = {"rows": len(part), "cancellation_rate": float(part["is_canceled"].mean()), "start": str(part["booking_date_proxy"].min().date()), "end": str(part["booking_date_proxy"].max().date())}
    freq_true, freq_pred = calibration_curve(y["test"], test_probs, n_bins=10, strategy="uniform")
    known = {name: sorted(groups["train"][name].dropna().astype(str).unique().tolist()) for name in CATEGORICAL}
    code_hash = hashlib.sha256(b"".join(p.read_bytes() for p in sorted((ROOT / "src").glob("*.py")) if p.name != "ui.py") + (ROOT / "train.py").read_bytes()).hexdigest()
    metadata = {
        "model_name": selected, "threshold": cutoff, "seed": SEED,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "raw_rows": len(data), "eligible_rows": len(eligible), "excluded_rows": int(invalid.sum()),
        "immature_cohort_rows_not_used": len(eligible) - sum(len(part) for part in groups.values()),
        "raw_cancellation_rate": float(data["is_canceled"].mean()),
        "exact_duplicate_rows": int(pd.read_csv(RAW).duplicated().sum()),
        "raw_sha256": sha256_file(RAW), "training_code_sha256": code_hash,
        "features": FEATURES, "input_fields": INPUT_FIELDS, "excluded_features": EXCLUDED,
        "known_categories": known, "partitions": partitions,
        "selection_rule": "Highest validation ROC AUC, tie broken by lower validation Brier score. Threshold maximizes validation F1 (0.10–0.90).",
        "validation_metrics_at_selected_threshold": evaluate(y["validation"], validation_probs, cutoff),
        "test_metrics": test_metrics,
        "test_metrics_at_0_5": evaluate(y["test"], test_probs, .5),
        "model_comparison": comparison,
        "test_curves": probability_curves(y["test"], test_probs),
        "calibration": {"observed": freq_true.tolist(), "predicted": freq_pred.tolist()},
        "versions": {name: pkg.version(name) for name in ["numpy", "pandas", "scikit-learn", "streamlit", "joblib"]},
        "python": platform.python_version(), "training_seconds": round(time.time()-started, 2),
        "limitations": [
            "Two Portuguese hotels, arrivals from July 2015 to August 2017. No current or Indian-hotel validation.",
            "Booking creation dates are proxies: arrival date minus lead time. No booking ID verifies repeated-looking rows.",
            "Records lack point-in-time snapshots. A final-status timestamp and planned checkout guard earlier cohorts; prospective deployment performance is not established.",
            "Retained values, including deposit, price and history, are assumed to be known at booking creation. Their timing needs a real PMS audit.",
            "Probabilities are uncalibrated model estimates. The reliability plot and Brier score describe this test sample only.",
            "Cancellation does not equal no-show: some not-cancelled records have final No-Show status.",
        ],
    }
    bundle = {"pipeline": pipeline, "threshold": cutoff, "model_name": selected, "features": FEATURES, "known_categories": known}
    # Atomic replacement means an interrupted training run cannot leave half a model.
    temp_model = MODEL_PATH.with_suffix(".tmp")
    joblib.dump(bundle, temp_model, compress=3)
    temp_model.replace(MODEL_PATH)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2, allow_nan=False), encoding="utf-8")
    predictions = groups["test"][["hotel", "arrival_date", "booking_date_proxy", "is_canceled"]].copy()
    predictions["probability"] = test_probs
    predictions["prediction"] = (test_probs >= cutoff).astype(int)
    predictions.to_csv(REPORTS / "test_predictions.csv", index=False)
    sample_rows = groups["test"].groupby("hotel", group_keys=False).sample(n=5, random_state=SEED).loc[:, INPUT_FIELDS]
    sample_rows.to_csv(DATA / "samples" / "example_bookings.csv", index=False)
    sample_rows.head(0).to_csv(DATA / "samples" / "booking_template.csv", index=False)
    progress(f"Done: {selected}, test ROC AUC {test_metrics['roc_auc']:.3f}, test F1 {test_metrics['f1']:.3f}.")
    return metadata


if __name__ == "__main__":
    train_all()
