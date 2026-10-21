import streamlit as st
from src.ui import dataset, metadata, metric_row, table
from src.charts import monthly_chart, group_summary, rate_chart

st.header("Booked or Cancelled?")
st.markdown("Understand booking behaviour, explore cancellation patterns and estimate which reservations may need follow-up.")
data = dataset()
meta = metadata()
metric_row([
    ("Historical bookings", f"{len(data):,}"),
    ("Observed cancellations", f"{data['is_canceled'].mean():.1%}"),
    ("Hotel types", str(data['hotel'].nunique())),
    ("Held-out ROC AUC", f"{meta['test_metrics']['roc_auc']:.3f}"),
])
left, right = st.columns([1.7, 1])
with left:
    st.subheader("Booking arrivals over time")
    st.altair_chart(monthly_chart(data), alt="Monthly booking counts for City Hotel and Resort Hotel, July 2015 through August 2017")
    st.caption("Counts include cancelled reservations. Partial years make simple month-to-month seasonal comparisons uneven.")
with right:
    st.subheader("Cancellation by hotel")
    summary = group_summary(data, "hotel")
    st.altair_chart(rate_chart(summary, "hotel", "Hotel"), alt="Observed cancellation rates for the two hotels with 95 percent Wilson intervals")
st.subheader("A complete analysis workflow")
with st.container(horizontal=True):
    st.markdown("**Explore**\n\nFilter the history and compare booking channels, lead times and deposits.")
    st.markdown("**Predict**\n\nScore a reservation or upload a CSV and download a review list.")
    st.markdown("**Evaluate**\n\nCompare algorithms and inspect errors on a later booking period.")
st.caption("Prediction labels are estimates. ‘Not cancelled’ can include no-shows and does not guarantee that a guest checks in.")
with st.expander("Data quality and model scope"):
    table(__import__('pandas').DataFrame([
        {"Check": "Raw rows", "Result": f"{meta['raw_rows']:,}"},
        {"Check": "Model-eligible overnight bookings", "Result": f"{meta['eligible_rows']:,}"},
        {"Check": "Zero guests, zero nights, invalid dates or negative ADR", "Result": f"{meta['excluded_rows']:,} rows excluded from modelling"},
        {"Check": "Identical-looking rows", "Result": f"{meta['exact_duplicate_rows']:,} retained because no booking ID proves duplication"},
        {"Check": "Earlier cohorts awaiting final outcomes", "Result": f"{meta['immature_cohort_rows_not_used']:,} excluded from temporal partitions"},
    ]), "Dataset quality checks and modelling exclusions")
    st.markdown("Charts on this page describe the full source data. Model metrics use the documented eligible temporal partitions.")

