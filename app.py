"""Local GUI entry point: python -m streamlit run app.py."""
import streamlit as st
from src.config import TITLE, SUBTITLE, RAW, MODEL_PATH, METADATA_PATH, INSTITUTE

st.set_page_config(page_title="Booked or Cancelled?", page_icon=":material/hotel:", layout="wide")
with st.sidebar:
    st.header(TITLE, icon=":material/hotel:")
    st.caption("Hotel booking intelligence")
    st.caption("Historical research data from two Portuguese hotels, 2015–2017.")

if not all(path.exists() for path in [RAW, MODEL_PATH, METADATA_PATH]):
    st.title(TITLE)
    st.info("Run SETUP.bat to install dependencies, download the dataset and train the models.")
    st.code(".venv\\Scripts\\python.exe train.py", language="powershell")
    st.stop()

pages = [
    st.Page("app_pages/overview.py", title="Overview", icon=":material/dashboard:", default=True),
    st.Page("app_pages/patterns.py", title="Booking patterns", icon=":material/query_stats:"),
    st.Page("app_pages/predict.py", title="Predict a booking", icon=":material/hotel:"),
    st.Page("app_pages/batch.py", title="Batch predictions", icon=":material/upload_file:"),
    st.Page("app_pages/models.py", title="Model lab", icon=":material/science:"),
    st.Page("app_pages/guide.py", title="Project guide", icon=":material/menu_book:"),
]
page = st.navigation(pages, position="top")
with st.sidebar:
    st.caption("VSEC Data Science Laboratory mini project")
    st.caption(INSTITUTE)
    st.caption("Local analysis. Uploaded CSVs stay in this app session.")
st.title(page.title, icon=page.icon)
page.run()

