"""Aggregated Altair charts: bounded browser payloads and explicit units."""
import altair as alt
import numpy as np
import pandas as pd

TEAL = "#087F8C"
ORANGE = "#D77741"
INK = "#162F36"


def monthly_chart(frame):
    month = frame.assign(month=frame["arrival_date"].dt.to_period("M").dt.to_timestamp())
    points = month.groupby(["month", "hotel"], observed=True).size().rename("bookings").reset_index()
    return alt.Chart(points).mark_area(opacity=.75).encode(
        x=alt.X("month:T", title="Scheduled arrival month"),
        y=alt.Y("bookings:Q", title="Bookings", stack="zero"),
        color=alt.Color("hotel:N", title="Hotel", scale=alt.Scale(range=[TEAL, ORANGE])),
        tooltip=[alt.Tooltip("month:T", format="%b %Y"), "hotel:N", "bookings:Q"],
    ).properties(height=300)


def group_summary(frame, column, minimum=1):
    group = frame.groupby(column, observed=True, dropna=False)["is_canceled"].agg(bookings="size", cancellations="sum", cancellation_rate="mean").reset_index()
    group[column] = group[column].astype(str)
    group = group.loc[group["bookings"] >= minimum].copy()
    # Wilson 95% binomial intervals for descriptive group rates.
    n, p, z = group["bookings"], group["cancellation_rate"], 1.96
    center = (p + z*z/(2*n)) / (1+z*z/n)
    radius = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1+z*z/n)
    group["lower"], group["upper"] = center-radius, center+radius
    return group


def rate_chart(summary, category, label):
    base = alt.Chart(summary).encode(y=alt.Y(f"{category}:N", title=None, sort="-x"))
    bars = base.mark_bar(color=TEAL).encode(
        x=alt.X("cancellation_rate:Q", title="Observed cancellation rate", axis=alt.Axis(format=".0%"), scale=alt.Scale(domain=[0, 1])),
        tooltip=[alt.Tooltip(f"{category}:N", title=label), "bookings:Q", "cancellations:Q", alt.Tooltip("cancellation_rate:Q", format=".1%"), alt.Tooltip("lower:Q", format=".1%"), alt.Tooltip("upper:Q", format=".1%")],
    )
    intervals = base.mark_rule(color=INK, strokeWidth=2).encode(x="lower:Q", x2="upper:Q")
    return (bars + intervals).properties(height=max(220, min(520, len(summary)*38)))


def confusion_chart(matrix):
    rows = [{"Actual": actual, "Predicted": predicted, "Count": matrix[i][j]} for i, actual in enumerate(["Not cancelled", "Cancelled"]) for j, predicted in enumerate(["Not cancelled", "Cancelled"])]
    base = alt.Chart(pd.DataFrame(rows)).encode(x=alt.X("Predicted:N", sort=["Not cancelled", "Cancelled"], axis=alt.Axis(labelAngle=0)), y=alt.Y("Actual:N", sort=["Not cancelled", "Cancelled"]))
    tiles = base.mark_rect().encode(color=alt.Color("Count:Q", scale=alt.Scale(range=["#E6F1F1", TEAL]), legend=None), tooltip=["Actual:N", "Predicted:N", "Count:Q"])
    labels = base.mark_text(fontSize=24, fontWeight="bold", color=INK).encode(text="Count:Q")
    return (tiles + labels).properties(height=280)


def roc_chart(curves):
    line = alt.Chart(pd.DataFrame(curves["roc"])).mark_line(color=TEAL, strokeWidth=3).encode(x=alt.X("fpr:Q", title="False-positive rate", scale=alt.Scale(domain=[0,1])), y=alt.Y("tpr:Q", title="True-positive rate", scale=alt.Scale(domain=[0,1])))
    diagonal = alt.Chart(pd.DataFrame({"x":[0,1],"y":[0,1]})).mark_line(color="#9AA9AB", strokeDash=[5,5]).encode(x="x:Q",y="y:Q")
    return (line+diagonal).properties(height=280)


def calibration_chart(calibration):
    reliability = alt.Chart(pd.DataFrame(calibration)).mark_line(color=TEAL, point=True, strokeWidth=3).encode(x=alt.X("predicted:Q", title="Mean predicted probability", scale=alt.Scale(domain=[0,1])), y=alt.Y("observed:Q", title="Observed cancellation frequency", scale=alt.Scale(domain=[0,1])), tooltip=[alt.Tooltip("predicted:Q",format=".1%"),alt.Tooltip("observed:Q",format=".1%")])
    line = alt.Chart(pd.DataFrame({"x":[0,1],"y":[0,1]})).mark_line(color="#9AA9AB",strokeDash=[5,5]).encode(x="x:Q",y="y:Q")
    return (reliability+line).properties(height=280)

