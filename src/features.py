"""Strict external-input validation plus an allowlist that blocks target leakage."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .config import INPUT_FIELDS, FEATURES, NUMERIC, CATEGORICAL, MONTHS, EXCLUDED
from .data import arrival_dates

INTEGER_LIMITS = {
    "lead_time": (0, 1000), "arrival_date_year": (2013, 2035),
    "arrival_date_day_of_month": (1, 31), "stays_in_weekend_nights": (0, 100),
    "stays_in_week_nights": (0, 200), "adults": (0, 100), "children": (0, 30),
    "babies": (0, 20), "is_repeated_guest": (0, 1),
    "previous_cancellations": (0, 1000), "previous_bookings_not_canceled": (0, 1000),
}


def make_features(frame):
    """Training and inference share this exact transformation."""
    result = frame.copy()
    result["arrival_month"] = result["arrival_date_month"].map({m: n+1 for n, m in enumerate(MONTHS)})
    result["arrival_day"] = result["arrival_date_day_of_month"]
    result = result.loc[:, FEATURES].copy()
    for name in NUMERIC:
        result[name] = pd.to_numeric(result[name], errors="coerce").astype(float)
    for name in CATEGORICAL:
        # Ordinary Python strings / np.nan work consistently across pandas/sklearn.
        result[name] = result[name].astype(object).where(result[name].notna(), np.nan)
    return result


def validate_bookings(frame, known_categories=None):
    """Return normalized rows and non-fatal warnings; fail the entire batch on bad input.

    Blank children counts are allowed and use the training-only median imputer.
    Outcome columns can appear in historical CSVs, but never enter make_features.
    """
    if frame.empty:
        raise ValueError("The CSV contains no booking rows.")
    if len(frame) > 10000:
        raise ValueError("Upload at most 10,000 bookings per batch.")
    if frame.columns.duplicated().any():
        raise ValueError("CSV column names must be unique.")
    missing = sorted(set(INPUT_FIELDS) - set(frame.columns))
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    rows = frame.loc[:, INPUT_FIELDS].copy()
    problems = []
    warnings = []
    for name, (low, high) in INTEGER_LIMITS.items():
        values = pd.to_numeric(rows[name], errors="coerce")
        nullable = name == "children"
        bad = (values.isna() if not nullable else (rows[name].notna() & values.isna()))
        bad |= values.notna() & (~np.isfinite(values) | (values < low) | (values > high) | (values != values.round()))
        if bad.any():
            examples = ", ".join(str(i+2) for i in np.flatnonzero(bad.to_numpy())[:4])
            problems.append(f"{name}: integer {low}–{high} required (CSV lines {examples})")
        rows[name] = values
    rate = pd.to_numeric(rows["adr"], errors="coerce")
    bad_rate = rate.isna() | ~np.isfinite(rate) | (rate < 0) | (rate > 10000)
    if bad_rate.any():
        problems.append("adr: provide a finite nightly rate from 0 to 10,000 EUR")
    rows["adr"] = rate
    for name in CATEGORICAL + ["arrival_date_month"]:
        rows[name] = rows[name].astype("string").str.strip()
        if rows[name].isna().any() or rows[name].eq("").any():
            problems.append(f"{name}: blank categories are not allowed")
    if not rows["hotel"].isin(["City Hotel", "Resort Hotel"]).all():
        problems.append("hotel: use City Hotel or Resort Hotel")
    if not rows["arrival_date_month"].isin(MONTHS).all():
        problems.append("arrival_date_month: use full English month names, e.g. January")
    if problems:
        raise ValueError("\n".join(problems))
    if arrival_dates(rows).isna().any():
        raise ValueError("An arrival date does not exist, e.g. February 30.")
    if (rows[["adults", "children", "babies"]].fillna(0).sum(axis=1) == 0).any():
        raise ValueError("Each booking needs at least one guest.")
    if (rows["stays_in_weekend_nights"] + rows["stays_in_week_nights"] == 0).any():
        raise ValueError("Each booking needs at least one overnight stay.")
    if rows["children"].isna().any():
        warnings.append("Blank children counts use the median learned on training data.")
    ignored = sorted(set(frame.columns) & (set(EXCLUDED) - {"arrival_date_year"}))
    if ignored or "is_canceled" in frame:
        warnings.append("Historical outcome and excluded fields are ignored by the model.")
    if known_categories:
        for name in CATEGORICAL:
            unseen = sorted(set(rows[name].dropna()) - set(known_categories.get(name, [])))
            if unseen:
                warnings.append(f"{name}: unseen categories {', '.join(unseen[:4])} use the trained encoder's unknown-category behavior.")
    if ((rows["arrival_date_year"] < 2015) | (rows["arrival_date_year"] > 2017)).any():
        warnings.append("These arrival years are outside the historical 2015–2017 dataset. Performance on current bookings is unverified.")
    if rows["adr"].gt(1000).any() or rows["lead_time"].gt(737).any():
        warnings.append("Some values extend beyond common training ranges, so estimates may be less reliable.")
    return rows, warnings

