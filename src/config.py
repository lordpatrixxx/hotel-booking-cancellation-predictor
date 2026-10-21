"""One shared feature contract for training, prediction, CSVs and documentation."""
from pathlib import Path
import calendar

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "hotel_bookings.csv"
ARTIFACTS = ROOT / "artifacts"
REPORTS = ROOT / "reports"
MODEL_PATH = ARTIFACTS / "cancellation_model.joblib"
METADATA_PATH = ARTIFACTS / "metadata.json"
SEED = 42
TITLE = "Booked or Cancelled?"
SUBTITLE = "Predicting hotel booking cancellations and discovering booking patterns"
INSTITUTE = "Pimpri Chinchwad College of Engineering, Pune"
DEPARTMENT = "Information Technology Department, Second Year"
FACULTY = "JYOTI MANOORKAR Ma'am"
TEAM = [
    ("Pratik Deepak Phapale", "125B1F210"),
    ("Swastik Sandipkumar Phapale", "125B1F212"),
    ("Nirjar Rupesh Patil", "125B1F206"),
]
MONTHS = list(calendar.month_name)[1:]

# A deliberately conservative subset. These fields must be available at scoring time.
NUMERIC = [
    "lead_time", "arrival_month", "arrival_day", "stays_in_weekend_nights",
    "stays_in_week_nights", "adults", "children", "babies", "is_repeated_guest",
    "previous_cancellations", "previous_bookings_not_canceled", "adr",
]
CATEGORICAL = [
    "hotel", "meal", "market_segment", "distribution_channel", "reserved_room_type",
    "deposit_type", "customer_type",
]
FEATURES = NUMERIC + CATEGORICAL
INPUT_FIELDS = [
    "hotel", "lead_time", "arrival_date_year", "arrival_date_month",
    "arrival_date_day_of_month", "stays_in_weekend_nights", "stays_in_week_nights",
    "adults", "children", "babies", "meal", "market_segment", "distribution_channel",
    "is_repeated_guest", "previous_cancellations", "previous_bookings_not_canceled",
    "reserved_room_type", "deposit_type", "customer_type", "adr",
]
EXCLUDED = {
    "reservation_status": "Reveals cancellation / check-out / no-show outcome.",
    "reservation_status_date": "Final status timestamp occurs after the prediction point.",
    "assigned_room_type": "May be assigned after booking creation.",
    "booking_changes": "Aggregates later booking modifications.",
    "days_in_waiting_list": "Can accumulate after booking creation.",
    "required_car_parking_spaces": "Request timing is not verified.",
    "total_of_special_requests": "Request timing is not verified.",
    "agent": "Identifier with portability and high-cardinality concerns.",
    "company": "Identifier with portability and high-cardinality concerns.",
    "country": "Used for descriptive analysis only, excluded from scoring.",
    "arrival_date_year": "Used to construct dates and splits, excluded from scoring.",
    "arrival_date_week_number": "Redundant calendar field, excluded from scoring.",
}
LABELS = {0: "Not cancelled", 1: "Cancelled"}
CHOICES = {
    "hotel": ["City Hotel", "Resort Hotel"],
    "meal": ["BB", "HB", "FB", "SC", "Undefined"],
    "market_segment": ["Online TA", "Offline TA/TO", "Direct", "Groups", "Corporate", "Complementary", "Aviation", "Undefined"],
    "distribution_channel": ["TA/TO", "Direct", "Corporate", "GDS", "Undefined"],
    "reserved_room_type": list("ABCDEFGHLP"),
    "deposit_type": ["No Deposit", "Non Refund", "Refundable"],
    "customer_type": ["Transient", "Transient-Party", "Contract", "Group"],
}
SOURCE_URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2020/2020-02-11/hotels.csv"
PAPER_URL = "https://doi.org/10.1016/j.dib.2018.11.126"
MIRROR_URL = "https://github.com/rfordatascience/tidytuesday/tree/main/data/2020/2020-02-11"

