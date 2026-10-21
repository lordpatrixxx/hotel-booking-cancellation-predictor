# Booked or Cancelled?

## Predicting Hotel Booking Cancellations and Discovering Booking Patterns

VSEC Data Science Laboratory mini project for B.Tech Information Technology, Second Year, Pimpri Chinchwad College of Engineering, Pune.

**Faculty:** JYOTI MANOORKAR Ma'am  
**Team:** Pratik Deepak Phapale (125B1F210), Swastik Sandipkumar Phapale (125B1F212), Nirjar Rupesh Patil (125B1F206)

## Start the project

1. Double-click `SETUP.bat` once. It creates the local environment, installs packages, downloads the public source data, trains the models, generates the report and runs the checks.
2. Double-click `START_PROJECT.bat` to open the GUI in a browser.
3. Use `STOP_PROJECT.bat` only if you need to close a running copy of this project.

Python 3.10 or newer is needed. The first setup needs an internet connection; after it finishes, the model and GUI work locally.

## GUI pages

- **Overview** gives the problem, data coverage, held-out model results and an example workflow.
- **Booking patterns** explores historical rates by channel, deposit, lead time, guest type and stay length.
- **Predict a booking** validates one booking and shows its cancellation probability and review flag.
- **Batch predictions** accepts a CSV, checks the schema, scores up to 10,000 rows and produces a safe downloadable result.
- **Model lab** compares the baseline, logistic regression, random forest and gradient boosting; it also explains leakage controls and errors.
- **Project guide** contains the dataset attribution, CSV schema and downloadable report/notebook.

Use `data/samples/booking_template.csv` for batch input. The supplied `example_bookings.csv` has ten valid rows. The batch tool requires every template field, but it ignores extra outcome and status columns.

## Project structure

```text
app.py                         Streamlit GUI entry point
app_pages/                     Six interactive pages
src/                           Data, feature, model, chart and UI modules
train.py                       Reproducible model experiment
data/                          Unchanged source CSV, checksum and batch examples
artifacts/                     Fitted model and experiment metadata
reports/                       Results, figures and printable project report
Hotel_Booking_Analysis.ipynb   Executed analysis notebook
tests/                         Data, model, safety and GUI tests
```

## Rebuild from the terminal

After running setup, execute these from this folder if you want to rebuild an artifact:

```powershell
.venv\Scripts\python.exe train.py
.venv\Scripts\python.exe scripts\build_deliverables.py
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m streamlit run app.py
```

## Method

The project uses the public Hotel Booking Demand dataset (119,390 historical bookings from a Portuguese city hotel and resort hotel). The target is `is_canceled`.

The model accepts only a conservative set of fields assumed available when a booking is created. It deliberately excludes `reservation_status`, `reservation_status_date`, assigned room, booking-change and other later or high-cardinality fields. The test partition is a later booking period. Model selection and the review threshold use the validation period only.

The model is for an academic demonstration. It describes historical associations and supports human review; it does not prove causes, predict current hotel operations or make booking decisions automatically.

## Attribution

Antonio, N., de Almeida, A. and Nunes, L. (2019), [Hotel booking demand datasets](https://doi.org/10.1016/j.dib.2018.11.126), *Data in Brief*, 22, 41–49, CC BY 4.0. The project downloads the combined CSV from the [TidyTuesday mirror](https://github.com/rfordatascience/tidytuesday/tree/main/data/2020/2020-02-11). The source URL, retrieval time and SHA-256 checksum are recorded in `data/provenance.json`.
