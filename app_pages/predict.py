from datetime import date
import pandas as pd
import streamlit as st
from src.config import CHOICES
from src.ui import model, threshold_control, metric_row, csv_bytes, table
from src.model import score_bookings

st.markdown("Enter information available when a reservation is created. Nightly prices use the original dataset’s currency, EUR.")
threshold = threshold_control("predict_threshold")
with st.form("booking_form"):
    left, right = st.columns(2)
    with left:
        st.subheader("Stay and guests")
        hotel = st.selectbox("Hotel type", CHOICES['hotel'])
        arrival = st.date_input("Arrival date", date(2017,5,15), min_value=date(2013,1,1), max_value=date(2035,12,31))
        lead = st.number_input("Lead time (days)", 0, 1000, 60, help="Days between entering the booking and scheduled arrival.")
        week = st.number_input("Weekday nights", 0, 200, 3)
        weekend = st.number_input("Weekend nights", 0, 100, 1)
        adults = st.number_input("Adults", 0, 100, 2)
        children = st.number_input("Children", 0, 30, 0)
        babies = st.number_input("Babies", 0, 20, 0)
    with right:
        st.subheader("Booking details")
        adr = st.number_input("Average daily rate (EUR)", 0.0, 10000.0, 110.0, step=5.0)
        segment = st.selectbox("Market segment", CHOICES['market_segment'])
        channel = st.selectbox("Distribution channel", CHOICES['distribution_channel'])
        deposit = st.selectbox("Deposit type", CHOICES['deposit_type'])
        customer = st.selectbox("Customer type", CHOICES['customer_type'])
        meal = st.selectbox("Meal plan", CHOICES['meal'], help="BB: breakfast; HB: half board; FB: full board; SC: self catering.")
        room = st.selectbox("Reserved room code", CHOICES['reserved_room_type'], help="Anonymized dataset codes do not identify room categories in another hotel.")
    with st.expander("Previous booking history"):
        repeated = st.checkbox("Guest has booked before")
        previous_cancel = st.number_input("Previous cancellations", 0, 1000, 0)
        previous_kept = st.number_input("Previous bookings not cancelled", 0, 1000, 0)
    submitted = st.form_submit_button("Estimate cancellation risk", type="primary", icon=":material/analytics:", key="predict_submit")

if submitted:
    row = dict(hotel=hotel, lead_time=lead, arrival_date_year=arrival.year, arrival_date_month=arrival.strftime('%B'), arrival_date_day_of_month=arrival.day, stays_in_weekend_nights=weekend, stays_in_week_nights=week, adults=adults, children=children, babies=babies, meal=meal, market_segment=segment, distribution_channel=channel, is_repeated_guest=int(repeated), previous_cancellations=previous_cancel, previous_bookings_not_canceled=previous_kept, reserved_room_type=room, deposit_type=deposit, customer_type=customer, adr=adr)
    try:
        result, messages = score_bookings(model(), pd.DataFrame([row]), threshold)
        st.session_state['prediction_result'] = result
        st.session_state['prediction_messages'] = messages
    except ValueError as error:
        st.session_state.pop('prediction_result', None)
        st.error(str(error))
if 'prediction_result' in st.session_state:
    result = st.session_state['prediction_result'].copy()
    probability = float(result.iloc[0].cancellation_probability)
    # Threshold changes update the decision without mutating the saved input.
    result['review_flag'] = result.cancellation_probability >= threshold
    result['prediction'] = result.review_flag.map({True:'Likely cancelled',False:'Likely not cancelled'})
    result['threshold'] = threshold
    st.subheader("Last submitted booking")
    metric_row([("Estimated cancellation probability", f"{probability:.1%}"), ("Prediction", result.iloc[0].prediction), ("Review threshold", f"{threshold:.0%}")])
    st.progress(probability, text="Estimated cancellation probability")
    if probability >= threshold:
        st.info("Flag for a staff review or confirmation follow-up. A prediction does not change the reservation.", icon=":material/fact_check:")
    else:
        st.success("Below the selected review threshold. Keep normal booking procedures.")
    st.caption("This is an uncalibrated historical-model estimate, not certainty. Current hotel performance needs separate validation.")
    for message in st.session_state.get('prediction_messages', []):
        st.caption(message)
    st.download_button("Download this prediction", csv_bytes(result), "booking_prediction.csv", "text/csv", icon=":material/download:")
    with st.expander("Submitted input and result"):
        table(result, "Last submitted booking fields and predicted cancellation probability")

