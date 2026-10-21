import altair as alt
import pandas as pd
import streamlit as st
from src.config import REPORTS, EXCLUDED
from src.ui import metadata, metric_row, table
from src.charts import confusion_chart, roc_chart, calibration_chart, TEAL

meta = metadata()
st.markdown(f"**Selected model: {meta['model_name']}**. Selection uses validation ROC AUC. The default decision threshold, {meta['threshold']:.2f}, maximizes validation F1.")
stats = meta['test_metrics']
metric_row([("Test ROC AUC", f"{stats['roc_auc']:.3f}"), ("Test precision", f"{stats['precision']:.1%}"), ("Test recall", f"{stats['recall']:.1%}"), ("Test F1", f"{stats['f1']:.3f}")])
st.caption(f"Accuracy {stats['accuracy']:.1%}; balanced accuracy {stats['balanced_accuracy']:.1%}; average precision {stats['average_precision']:.3f}; Brier score {stats['brier_score']:.3f} (lower is better). Positive class = cancelled.")
section = st.segmented_control("Evaluation view", ["Errors and curves", "Model comparison", "Feature importance", "Methodology"], default="Errors and curves", key="model_section")
if section == 'Errors and curves':
    left, right = st.columns(2)
    with left:
        st.subheader("Confusion matrix")
        st.altair_chart(confusion_chart(stats['confusion_matrix']), alt="Actual versus predicted cancellations on held-out test bookings")
    with right:
        st.subheader("ROC curve")
        st.altair_chart(roc_chart(meta['test_curves']), alt="Held-out test ROC curve compared with the random-ranking diagonal")
    a, b = st.columns(2)
    with a:
        st.subheader("Probability reliability")
        st.altair_chart(calibration_chart(meta['calibration']), alt="Observed cancellations versus average predicted probability in ten bins")
        st.caption("Closer to the diagonal indicates better calibration in this test sample. No calibration adjustment was fitted.")
    with b:
        st.subheader("Threshold trade-off on validation")
        thresholds = pd.read_csv(REPORTS/'validation_thresholds.csv')
        points = thresholds[['threshold','precision','recall','f1']].melt('threshold',var_name='metric',value_name='value')
        chart = alt.Chart(points).mark_line().encode(x=alt.X('threshold:Q',title='Review threshold'), y=alt.Y('value:Q',title='Score',scale=alt.Scale(domain=[0,1])),color='metric:N',tooltip=['threshold:Q','metric:N',alt.Tooltip('value:Q',format='.3f')]).properties(height=280)
        st.altair_chart(chart, alt="Validation precision, recall and F1 as the review threshold changes")
elif section == 'Model comparison':
    comparison = pd.DataFrame(meta['model_comparison'])
    columns = ['model','selected','validation_roc_auc','test_roc_auc','test_average_precision','test_accuracy','test_precision','test_recall','test_f1','test_brier_score']
    table(comparison[columns].round(4), "Comparison of three classifiers and a majority-class baseline")
    st.caption("Comparison rows use threshold 0.50 for every algorithm. The headline selected-model scores use its validation-selected threshold. Test scores did not decide which model to deploy.")
elif section == 'Feature importance':
    importance = pd.read_csv(REPORTS/'feature_importance.csv')
    chart = alt.Chart(importance.head(12)).mark_bar(color=TEAL).encode(x=alt.X('auc_decrease:Q',title='Decrease in validation ROC AUC when shuffled'), y=alt.Y('feature:N',sort='-x',title=None),tooltip=['feature:N',alt.Tooltip('auc_decrease:Q',format='.4f'),alt.Tooltip('std:Q',format='.4f')]).properties(height=420)
    st.altair_chart(chart, alt="Top twelve features by permutation importance on a validation sample")
    st.caption("Three repeats on up to 2,000 validation bookings. This describes predictive dependence, not causation or an explanation of one individual prediction.")
    table(importance.round(5), "All validation permutation importances and repeat standard deviations")
else:
    st.subheader("Chronological evaluation")
    partitions = pd.DataFrame([{'Partition':name,**details} for name,details in meta['partitions'].items()])
    table(partitions, "Training, validation and test date ranges and class proportions")
    st.markdown("Booking date proxy = scheduled arrival minus lead time. Train: before September 2016. Validation: September–December 2016. Test: January 2017 onward. Earlier cohorts must finish their planned stay and reach their final recorded status before the next period.")
    st.caption(f"{meta['immature_cohort_rows_not_used']:,} eligible records fall outside the mature earlier cohorts. This restricts representativeness, especially for longer lead times. The source also lacks booking-time snapshots.")
    st.subheader("Outcome information cannot enter the model")
    table(pd.DataFrame([{'Excluded field':name,'Reason':reason} for name,reason in EXCLUDED.items()]), "Excluded model fields and leakage or portability reasons")
    st.markdown("Missing-value imputation, scaling and category encoding fit on training data only. The model remains fitted on that partition. The test period never sets hyperparameters, feature choices or the decision threshold.")
    for limitation in meta['limitations']:
        st.caption(limitation)
with st.expander("Reproduce the experiment"):
    st.code(".venv\\Scripts\\python.exe train.py\n.venv\\Scripts\\python.exe scripts\\build_deliverables.py\n.venv\\Scripts\\python.exe -m pytest -q", language='powershell')
    st.caption("Training regenerates project-owned artifacts. Restart the app after retraining. See README.md for setup and exact package versions.")

