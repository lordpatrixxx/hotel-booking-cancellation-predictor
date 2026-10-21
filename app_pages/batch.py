import io
import csv
import pandas as pd
import streamlit as st
from src.config import DATA
from src.ui import model, threshold_control, metric_row, table, csv_bytes
from src.model import score_bookings

st.markdown("Upload up to 10,000 bookings, score the batch, and download a review list. The sample file is ready for a classroom demonstration.")
with st.container(horizontal=True):
    st.download_button("Download CSV template", (DATA/'samples/booking_template.csv').read_bytes(), "booking_template.csv", "text/csv", icon=":material/download:")
    st.download_button("Download example bookings", (DATA/'samples/example_bookings.csv').read_bytes(), "example_bookings.csv", "text/csv", icon=":material/download:")
threshold = threshold_control("batch_threshold")
source = st.segmented_control("Input source", ["Included examples", "Upload CSV"], default="Included examples", key="batch_source")
uploaded = st.file_uploader("Booking CSV", type=['csv'], max_upload_size=20, key="batch_upload") if source == 'Upload CSV' else None
if source == 'Upload CSV' and uploaded is None:
    st.info("Choose a CSV with the template columns.")
    st.stop()
raw = uploaded.getvalue() if uploaded is not None else (DATA/'samples/example_bookings.csv').read_bytes()
try:
    decoded = raw.decode('utf-8-sig')
    header = next(csv.reader(io.StringIO(decoded)))
    if len(header) != len(set(header)):
        raise ValueError("CSV column names must be unique.")
    frame = pd.read_csv(io.StringIO(decoded), nrows=10001)
except (UnicodeError, ValueError, pd.errors.ParserError, StopIteration) as error:
    st.error(f"Unable to read CSV: {error}")
    st.stop()
table(frame.head(20), "Preview of the first twenty input bookings")
if st.button("Score bookings", type="primary", icon=":material/analytics:", key="batch_score"):
    try:
        with st.spinner("Scoring bookings…"):
            result, messages = score_bookings(model(), frame, threshold)
        # Only the feature allowlist is echoed, never arbitrary guest identifiers.
        st.session_state['batch_result'] = result
        st.session_state['batch_input_hash'] = __import__('hashlib').sha256(raw).hexdigest()
        st.session_state['batch_messages'] = messages
    except ValueError as error:
        st.session_state.pop('batch_result', None)
        st.error(str(error))
if 'batch_result' in st.session_state and st.session_state.get('batch_input_hash') == __import__('hashlib').sha256(raw).hexdigest():
    result = st.session_state['batch_result'].copy()
    result['review_flag'] = result.cancellation_probability >= threshold
    result['prediction'] = result.review_flag.map({True:'Likely cancelled',False:'Likely not cancelled'})
    result['threshold'] = threshold
    metric_row([("Bookings scored", f"{len(result):,}"), ("Flagged for review", f"{result.review_flag.sum():,}"), ("Mean estimated probability", f"{result.cancellation_probability.mean():.1%}")])
    only_flagged = st.checkbox("Show flagged bookings only", key="batch_only_flagged")
    view = result.loc[result.review_flag] if only_flagged else result
    table(view.sort_values('cancellation_probability', ascending=False), "Scored bookings ordered by estimated cancellation probability")
    with st.container(horizontal=True):
        st.download_button("Download all predictions", csv_bytes(result), "all_predictions.csv", "text/csv", icon=":material/download:")
        st.download_button("Download flagged review list", csv_bytes(result.loc[result.review_flag]), "booking_review_list.csv", "text/csv", icon=":material/download:")
    for message in st.session_state.get('batch_messages', []):
        st.caption(message)
    st.caption("Flags support manual follow-up. The app does not cancel, charge or alter reservations.")

