import json
import pandas as pd
import streamlit as st
from src.config import ROOT, DATA, REPORTS, INPUT_FIELDS, PAPER_URL, MIRROR_URL, TEAM, FACULTY
from src.ui import table

st.markdown("### Booked or Cancelled?\nPredicting hotel booking cancellations and discovering booking patterns")
st.markdown("A VSEC Data Science Laboratory mini project for Second Year B.Tech Information Technology, Pimpri Chinchwad College of Engineering, Pune.")
st.caption("Team: " + " · ".join(f"{name} (PRN {prn})" for name, prn in TEAM))
st.caption(f"Faculty: {FACULTY}")
st.subheader("Demonstration in five minutes")
st.markdown("1. Open **Overview** to introduce the dataset and target.\n2. In **Booking patterns**, compare lead-time groups and booking channels.\n3. In **Predict a booking**, submit a reservation and change the review threshold.\n4. In **Batch predictions**, score the included CSV and download the review list.\n5. In **Model lab**, explain temporal splitting, the confusion matrix and the leakage exclusions.")
st.subheader("Project files")
for label, name, mime in [
    ('Download project report (HTML)', 'PROJECT_REPORT.html', 'text/html'),
    ('Download project report (Markdown)', 'PROJECT_REPORT.md', 'text/markdown'),
    ('Download model comparison', 'model_comparison.csv', 'text/csv'),
]:
    path = REPORTS/name
    if path.exists():
        st.download_button(label,path.read_bytes(),name,mime,icon=":material/download:")
notebook = ROOT/'Hotel_Booking_Analysis.ipynb'
if notebook.exists():
    st.download_button('Download analysis notebook',notebook.read_bytes(),notebook.name,'application/x-ipynb+json',icon=":material/download:")
with st.expander("CSV schema"):
    table(pd.DataFrame({'Required column':INPUT_FIELDS}),"Required booking CSV columns")
    st.caption("Use the batch page’s template and examples. is_canceled and reservation-status columns are never required for prediction.")
st.subheader("Data attribution")
st.markdown(f"Antonio, N., de Almeida, A. & Nunes, L. (2019). [Hotel booking demand datasets]({PAPER_URL}). *Data in Brief*, 22, 41–49. CC BY 4.0.\n\nThe combined CSV comes from the [TidyTuesday mirror]({MIRROR_URL}), prepared by Thomas Mock and Antoine Bichat. The raw file remains unchanged.")
provenance = json.loads((DATA/'provenance.json').read_text(encoding='utf-8'))
st.caption(f"Raw dataset SHA-256: {provenance['sha256']}")
st.subheader("Interpreting predictions")
st.markdown("The app estimates the target **is_canceled**, rather than guest attendance or profit. Human staff decide how to follow up. Patterns describe historical associations. Local policies, modern demand and a new hotel may differ substantially from this dataset.")
