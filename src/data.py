"""Dataset acquisition and derived dates. Never silently replace the raw dataset."""
from __future__ import annotations
import calendar
import hashlib
import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen
import pandas as pd
from .config import DATA, RAW, SOURCE_URL, PAPER_URL, MIRROR_URL, MONTHS


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download_dataset():
    DATA.mkdir(parents=True, exist_ok=True)
    provenance = DATA / "provenance.json"
    if RAW.exists():
        if provenance.exists():
            expected = json.loads(provenance.read_text(encoding="utf-8"))["sha256"]
            if sha256_file(RAW) != expected:
                raise ValueError("The raw dataset differs from its recorded SHA-256. Restore the original or create a new provenance record deliberately.")
        return RAW
    req = Request(SOURCE_URL, headers={"User-Agent": "HotelBookingStudentProject/1.0"})
    with urlopen(req, timeout=90) as response:
        payload = response.read(25_000_001)
    if len(payload) > 25_000_000 or not payload.startswith(b"hotel,is_canceled,"):
        raise ValueError("Download did not match the expected hotel CSV format.")
    temp = RAW.with_suffix(".download")
    temp.write_bytes(payload)
    try:
        frame = pd.read_csv(temp)
        if len(frame) != 119390 or "reservation_status" not in frame:
            raise ValueError("Expected the complete 119,390-row TidyTuesday hotel dataset.")
        temp.replace(RAW)
    finally:
        temp.unlink(missing_ok=True)
    provenance.write_text(json.dumps({
        "title": "Hotel booking demand datasets",
        "authors": "Nuno Antonio, Ana de Almeida and Luis Nunes",
        "publication_year": 2019,
        "paper": PAPER_URL,
        "mirror": MIRROR_URL,
        "download_url": SOURCE_URL,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": sha256_file(RAW),
        "rows": len(frame), "columns": list(frame.columns),
        "license": "CC BY 4.0 (original data article). Preserve original and mirror attribution.",
        "modifications": "Raw mirror CSV unchanged. Dates and features are derived in memory.",
    }, indent=2), encoding="utf-8")
    return RAW


def arrival_dates(frame):
    month_number = frame["arrival_date_month"].map({name: i + 1 for i, name in enumerate(MONTHS)})
    # Construct without locale-dependent month-name parsing.
    return pd.to_datetime(pd.DataFrame({
        "year": pd.to_numeric(frame["arrival_date_year"], errors="coerce"),
        "month": month_number,
        "day": pd.to_numeric(frame["arrival_date_day_of_month"], errors="coerce"),
    }, index=frame.index), errors="coerce")


def load_data(path=RAW):
    frame = pd.read_csv(path)
    frame["arrival_date"] = arrival_dates(frame)
    frame["booking_date_proxy"] = frame["arrival_date"] - pd.to_timedelta(frame["lead_time"], unit="D")
    frame["total_nights"] = frame["stays_in_weekend_nights"] + frame["stays_in_week_nights"]
    frame["total_guests"] = frame["adults"] + frame["children"].fillna(0) + frame["babies"]
    return frame


def chronological_split(frame):
    """Split by estimated booking creation date, never by a random row shuffle."""
    dates = frame["booking_date_proxy"]
    if dates.isna().any():
        raise ValueError("Invalid booking dates prevent a chronological split.")
    # For train and validation, use only cohorts whose planned stays and final
    # recorded outcomes have matured before the next period begins. Outcome
    # timestamps are used only for this availability guard, never as predictors.
    checkout = frame["arrival_date"] + pd.to_timedelta(frame["total_nights"], unit="D")
    status_date = pd.to_datetime(frame["reservation_status_date"], errors="coerce")
    masks = {
        "train": (dates < pd.Timestamp("2016-09-01")) & (checkout < pd.Timestamp("2016-09-01")) & (status_date < pd.Timestamp("2016-09-01")),
        "validation": (dates >= pd.Timestamp("2016-09-01")) & (dates < pd.Timestamp("2017-01-01")) & (checkout < pd.Timestamp("2017-01-01")) & (status_date < pd.Timestamp("2017-01-01")),
        "test": dates >= pd.Timestamp("2017-01-01"),
    }
    groups = {name: frame.loc[mask].sort_values("booking_date_proxy", kind="stable").copy() for name, mask in masks.items()}
    if any(len(part) == 0 or part["is_canceled"].nunique() != 2 for part in groups.values()):
        raise ValueError("Every chronological partition must contain both target classes.")
    return groups

