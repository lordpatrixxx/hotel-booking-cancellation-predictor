import altair as alt
import pandas as pd
import streamlit as st
from src.ui import dataset, metric_row, table, csv_bytes
from src.charts import monthly_chart, group_summary, rate_chart, TEAL

st.markdown("Explore observed relationships in the historical data. Filters affect every chart and summary below.")
data = dataset()
with st.container(horizontal=True):
    hotels = st.multiselect("Hotel", sorted(data['hotel'].unique()), default=sorted(data['hotel'].unique()), key="patterns_hotels")
    years = st.multiselect("Arrival year", sorted(data['arrival_date_year'].unique()), default=sorted(data['arrival_date_year'].unique()), key="patterns_years")
    minimum = st.number_input("Minimum bookings per group", 1, 5000, 30, step=10, key="patterns_minimum")
filtered = data.loc[data.hotel.isin(hotels) & data.arrival_date_year.isin(years)].copy()
if filtered.empty:
    st.info("Select at least one hotel and arrival year to explore bookings.")
    st.stop()
metric_row([("Bookings in view", f"{len(filtered):,}"), ("Cancellation rate", f"{filtered.is_canceled.mean():.1%}"), ("Median lead time", f"{filtered.lead_time.median():.0f} days"), ("Median nightly ADR", f"€{filtered.adr.median():.2f}")])
st.altair_chart(monthly_chart(filtered), alt="Booking arrival counts over time under the selected filters")
dimension = st.selectbox("Compare cancellation patterns by", ["Booking channel", "Lead time", "Deposit type", "Customer type", "Repeat guest", "Stay length"], key="patterns_dimension")
column = {"Booking channel":"market_segment", "Lead time":"lead_band", "Deposit type":"deposit_type", "Customer type":"customer_type", "Repeat guest":"repeat_status", "Stay length":"stay_band"}[dimension]
filtered['lead_band'] = pd.cut(filtered.lead_time, [-1,7,30,90,180,365,1000], labels=["0–7 days","8–30 days","31–90 days","91–180 days","181–365 days","Over 365 days"])
filtered['stay_band'] = pd.cut(filtered.total_nights, [-1,0,2,5,10,400], labels=["Zero nights","1–2 nights","3–5 nights","6–10 nights","Over 10 nights"])
filtered['repeat_status'] = filtered.is_repeated_guest.map({0:"First-time guest",1:"Repeat guest"})
summary = group_summary(filtered, column, int(minimum))
st.subheader(f"Cancellation by {dimension.lower()}")
if summary.empty:
    st.info("No groups meet the minimum group size. Reduce the minimum or broaden the filters.")
else:
    st.altair_chart(rate_chart(summary, column, dimension), alt=f"Observed cancellation rates by {dimension.lower()} with group counts and Wilson confidence intervals")
    table(summary.rename(columns={column:dimension}), "Group cancellation counts, rates and uncertainty intervals")
    st.download_button("Download grouped analysis", csv_bytes(summary), "booking_patterns.csv", "text/csv", icon=":material/download:")
st.caption("Bars show associations, not causal effects. Deposit rules and booking channels can reflect different commercial policies. Intervals assume independent bookings and may understate dependence within groups.")
with st.expander("Nightly price distribution"):
    prices = filtered.loc[filtered.adr.between(0,1000)]
    counts = prices.assign(price_band=pd.cut(prices.adr, bins=list(range(0,1050,50)), include_lowest=True)).groupby(['price_band','hotel'], observed=True).size().rename('bookings').reset_index()
    counts['price_band'] = counts.price_band.astype(str)
    chart = alt.Chart(counts).mark_bar().encode(x=alt.X('price_band:N', title='Nightly ADR (EUR)', sort=None), y=alt.Y('bookings:Q',title='Bookings'), color='hotel:N',tooltip=['price_band:N','hotel:N','bookings:Q']).properties(height=280)
    st.altair_chart(chart, alt="Nightly rate distribution in 50-euro bands")
    st.caption(f"Plot includes {len(prices):,} records with ADR from €0 to €1,000; {len(filtered)-len(prices):,} outside that display range remain in other summaries.")

