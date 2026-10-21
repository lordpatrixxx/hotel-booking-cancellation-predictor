"""Bounded caches and small shared GUI helpers."""
import json
import joblib
import pandas as pd
import streamlit as st
from .config import RAW, MODEL_PATH, METADATA_PATH, REPORTS
from .data import load_data


@st.cache_data(max_entries=2, show_spinner="Loading historical bookings…")
def _data(stamp):
    return load_data()


def dataset():
    return _data(RAW.stat().st_mtime_ns)


@st.cache_data(max_entries=2, show_spinner=False)
def _metadata(stamp):
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def metadata():
    return _metadata(METADATA_PATH.stat().st_mtime_ns)


@st.cache_resource(max_entries=2, show_spinner="Loading the trained model…")
def _model(stamp):
    return joblib.load(MODEL_PATH)


def model():
    return _model(MODEL_PATH.stat().st_mtime_ns)


def metric_row(values):
    with st.container(horizontal=True):
        for label, value in values:
            st.metric(label, value, border=True)


def table(frame, description, **kwargs):
    st.dataframe(frame, hide_index=True, alt=description, **kwargs)


def threshold_control(key):
    default = metadata()["threshold"]
    return st.slider("Flag for review at or above", .10, .90, float(default), .01, format="%.2f", key=key, help="Lower thresholds catch more potential cancellations but flag more bookings that will remain active.")


def csv_bytes(frame):
    # Avoid spreadsheet formula execution if arbitrary input categories are exported.
    result = frame.copy()
    for column in result.select_dtypes(include=["object", "string"]).columns:
        result[column] = result[column].map(lambda value: "'" + value if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")) else value)
    return result.to_csv(index=False).encode("utf-8-sig")

