"""Generate figures, a printable report and an actually executed notebook."""
from __future__ import annotations
import base64
import html
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import nbformat
from nbclient import NotebookClient
from src.config import DATA, REPORTS, ARTIFACTS, EXCLUDED, INPUT_FIELDS, PAPER_URL, MIRROR_URL, TEAM, FACULTY, INSTITUTE
from src.data import load_data, chronological_split
from src.charts import group_summary

FIGURES = REPORTS / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)
META = json.loads((ARTIFACTS/'metadata.json').read_text(encoding='utf-8'))
data = load_data()
stats = META['test_metrics']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.labelcolor':'#162F36','text.color':'#162F36'})
TEAL, ORANGE = '#087F8C', '#D77741'


def save(name):
    plt.tight_layout()
    plt.savefig(FIGURES/name, dpi=140, bbox_inches='tight')
    plt.close()


monthly = data.assign(month=data.arrival_date.dt.to_period('M').dt.to_timestamp()).groupby(['month','hotel']).size().unstack(fill_value=0)
ax=monthly.plot(figsize=(10,3.6),color=[TEAL,ORANGE],linewidth=2.2)
ax.set(xlabel='Scheduled arrival month',ylabel='Bookings',title='Booking arrivals in the historical dataset')
save('monthly_arrivals.png')
group = group_summary(data,'market_segment',30).sort_values('cancellation_rate')
plt.figure(figsize=(9,3.8)); plt.barh(group.market_segment,group.cancellation_rate,color=TEAL); plt.xlabel('Observed cancellation rate'); plt.xlim(0,1); plt.gca().xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1)); plt.title('Observed cancellation by booking channel'); save('channel_patterns.png')
matrix=np.array(stats['confusion_matrix']); fig,ax=plt.subplots(figsize=(6,4)); ax.imshow(matrix,cmap='GnBu');
for (i,j),value in np.ndenumerate(matrix): ax.text(j,i,f'{value:,}',ha='center',va='center',fontsize=18,color='#162F36')
ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['Not cancelled','Cancelled'],yticklabels=['Not cancelled','Cancelled'],xlabel='Predicted',ylabel='Actual',title='Held-out confusion matrix'); save('confusion_matrix.png')
curve=META['test_curves']['roc']; plt.figure(figsize=(6,4)); plt.plot(curve['fpr'],curve['tpr'],color=TEAL,label=f"ROC AUC {stats['roc_auc']:.3f}"); plt.plot([0,1],[0,1],'--',color='#9AA9AB'); plt.xlabel('False-positive rate'); plt.ylabel('True-positive rate'); plt.title('Held-out test ROC curve'); plt.legend(); save('roc_curve.png')
importance=pd.read_csv(REPORTS/'feature_importance.csv'); view=importance.head(10).iloc[::-1]; plt.figure(figsize=(9,4)); plt.barh(view.feature,view.auc_decrease,xerr=view['std'],color=TEAL); plt.xlabel('Decrease in validation ROC AUC after shuffling'); plt.title('Validation permutation importance'); save('feature_importance.png')
reliability=META['calibration']; plt.figure(figsize=(6,4)); plt.plot(reliability['predicted'],reliability['observed'],'o-',color=TEAL); plt.plot([0,1],[0,1],'--',color='#9AA9AB'); plt.xlabel('Mean predicted probability'); plt.ylabel('Observed cancellation frequency'); plt.xlim(0,1); plt.ylim(0,1); plt.title('Test probability reliability'); save('calibration.png')


def markdown_table(frame):
    frame=frame.copy().fillna('')
    def fmt(value):
        return f'{value:.4f}' if isinstance(value,(float,np.floating)) else str(value)
    rows=['| '+' | '.join(map(str,frame.columns))+' |','| '+' | '.join(['---']*len(frame.columns))+' |']
    rows += ['| '+' | '.join(fmt(v).replace('|','/') for v in row)+' |' for row in frame.itertuples(index=False,name=None)]
    return '\n'.join(rows)


partitions=pd.DataFrame([{'Partition':name,**values} for name,values in META['partitions'].items()])
comparison=pd.DataFrame(META['model_comparison'])[['model','validation_roc_auc','test_roc_auc','test_accuracy','test_precision','test_recall','test_f1','test_brier_score']]
metrics=pd.DataFrame([{'Metric':name.replace('_',' ').title(),'Result':round(value,4)} for name,value in stats.items() if name not in ['confusion_matrix','threshold']])
hotel_group=group_summary(data,'hotel')
source=json.loads((DATA/'provenance.json').read_text(encoding='utf-8'))
team_lines = "\n".join(f'- {name} (PRN {prn})' for name, prn in TEAM)
content=f'''# Booked or Cancelled?
## Predicting Hotel Booking Cancellations and Discovering Booking Patterns

VSEC Data Science Laboratory mini project. B.Tech Information Technology, Second Year.
{INSTITUTE}. Faculty: {FACULTY}.

### Team

{team_lines}

## Abstract

This project studies hotel cancellations as a binary classification problem and explores historical booking patterns. It combines an interactive Streamlit GUI, reproducible Python pipelines, a real public dataset and an executed notebook. The source contains {META['raw_rows']:,} bookings, of which {META['raw_cancellation_rate']:.1%} have a cancellation outcome. A fixed chronological protocol compares logistic regression, random forest and gradient boosting with a majority-class baseline. {META['model_name']} has the highest validation ROC AUC and achieves test ROC AUC {stats['roc_auc']:.3f}. At the validation-selected threshold of {META['threshold']:.2f}, test precision is {stats['precision']:.1%}, recall is {stats['recall']:.1%} and F1 is {stats['f1']:.3f}. These results describe a historical cohort rather than verified performance at a current hotel.

## 1. Problem statement and objectives

Hotels need to understand cancellation patterns and prioritize reservations for confirmation. The application estimates whether a booking may be cancelled using information assumed available at creation time. It supports staff review and exploratory analysis. It does not modify reservations, estimate guaranteed revenue, forecast occupancy, or equate non-cancellation with attendance.

The objectives are to clean and inspect data, visualize observed patterns, compare multiple algorithms, evaluate future-period errors, and provide single and batch prediction through a usable GUI. The positive target is is_canceled = 1. The negative target includes records marked No-Show, so “not cancelled” must not be renamed “checked in.”

## 2. Dataset and attribution

The original work is Antonio, N., de Almeida, A. and Nunes, L. (2019), Hotel booking demand datasets, Data in Brief 22, 41–49. DOI: {PAPER_URL}. The data describe a resort hotel and a city hotel in Portugal, with arrivals from July 2015 through August 2017. The combined CSV is provided by the TidyTuesday mirror ({MIRROR_URL}), prepared by Thomas Mock and Antoine Bichat. The original data article uses CC BY 4.0. The local raw file is unchanged. Retrieval and checksum details appear in data/provenance.json.

Raw SHA-256: {source['sha256']}

The modelling subset contains {META['eligible_rows']:,} overnight bookings. We exclude {META['excluded_rows']:,} records with zero guests, zero nights, invalid dates or negative prices. Children has a small number of missing values and uses a median learned on training data. Categorical missing values use the most frequent training category. We retain {META['exact_duplicate_rows']:,} exact duplicate-looking rows because the dataset has no booking ID to distinguish repeated snapshots from separate similar reservations. Dependence between bookings remains a limitation.

## 3. Methodology

Booking creation date is approximated as arrival date minus lead_time. Training bookings begin before 1 September 2016, validation bookings begin from September through December 2016, and test bookings begin in January 2017 or later. For earlier partitions, planned checkout and the final recorded status date must precede the next period. This avoids making an earlier model depend on labels that were still unresolved. It leaves {META['immature_cohort_rows_not_used']:,} otherwise eligible observations outside these mature cohorts and can reduce representation of long-lead reservations.

{markdown_table(partitions)}

The predictor uses {len(META['features'])} numeric and categorical features. Numerical values use training-only median imputation and scaling. Categorical values use training-only mode imputation and one-hot encoding, with unknown categories ignored. The same feature transformation and fitted pipeline serve the GUI and batch inputs. The test set never determines model choice or threshold. The fitted model remains trained on the training partition so the reported evaluation corresponds to the distributed artifact.

Model choice maximizes validation ROC AUC. A tie uses lower validation Brier score. Thresholds from 0.10 through 0.90 in increments of 0.01 are compared on validation F1, with documented tie breaks. The chosen threshold is {META['threshold']:.2f}. The GUI allows another review threshold without changing model probabilities. This does not imply the F1 optimum matches every hotel’s operational costs.

Outcome status, final status timestamp and later modification fields cannot enter the predictor. Final timestamps have a separate, evaluation-only label-availability role. The selected fields, including ADR, deposit rules and guest history, are assumed to have booking-time values; the source does not supply immutable point-in-time snapshots to verify this assumption. The experiment is not proof that all temporal leakage has been eliminated.

## 4. Algorithms and results

The experiment uses a majority-class DummyClassifier, logistic regression, a 140-tree random forest and histogram gradient boosting. Random seed is 42. The comparison table uses threshold 0.50 for all models so those rows are directly comparable.

{markdown_table(comparison)}

Selected model at its validation-selected threshold:

{markdown_table(metrics)}

The confusion matrix uses rows for actual and columns for predicted outcomes, ordered not-cancelled then cancelled. A false positive flags a booking that remains uncancelled. A false negative misses a booking that cancels. Precision measures the fraction of flags that really cancel. Recall measures the fraction of cancellations detected. ROC AUC evaluates ranking across thresholds. Average precision is informative with an imbalanced target. Brier score measures probability error, and the reliability chart shows whether estimated probability bands match observed frequencies. No calibration correction has been fitted.

![Held-out confusion matrix](figures/confusion_matrix.png)
![Held-out ROC curve](figures/roc_curve.png)
![Probability reliability](figures/calibration.png)

## 5. Booking-pattern discovery

The GUI filters the complete source history by hotel and arrival year. It compares booking channels, lead-time bands, deposit types, repeat status, customer types and stay length. Every rate displays sample counts and can suppress small groups. Wilson 95% intervals describe sampling uncertainty under an independence assumption. They do not account for dependence between related bookings.

{markdown_table(hotel_group[['hotel','bookings','cancellations','cancellation_rate']])}

![Scheduled arrivals over time](figures/monthly_arrivals.png)
![Booking channel cancellation rates](figures/channel_patterns.png)

The period contains partial years. Monthly volume can reflect coverage as well as seasonality. Cancellation differences by deposits and channels are associations and may reflect commercial policy. They are not evidence that changing a deposit causes the same change in cancellation risk. Feature importance also measures predictive dependence, not causal effect or an individual guest’s reason for cancelling.

![Validation permutation importance](figures/feature_importance.png)

## 6. Software architecture and GUI

The data layer loads the unchanged CSV and constructs dates. The feature layer validates inputs and enforces a column allowlist. The training layer fits and compares complete scikit-learn pipelines. Artifacts store the selected pipeline, metrics, version information and checksums. The GUI caches immutable data and model resources, then provides six views: Overview, Booking patterns, Predict a booking, Batch predictions, Model lab and Project guide.

Single prediction uses a form with stay, price, booking and history fields. Batch scoring accepts a UTF-8 CSV containing the supplied template columns, rejects invalid rows with useful error messages, and preserves input row numbers. Exports contain probabilities, predictions, flags and the threshold. Unknown categories receive an explicit notice. Extra outcome columns are ignored. Arbitrary guest identifiers are not echoed into output. Formula-like strings are escaped in spreadsheet-oriented CSV downloads. The GUI accepts no model files.

## 7. Testing and reproducibility

Automated tests cover date and numeric validation, unknown categories, invalid stays, outcome-field invariance, consistent batch scoring, threshold changes and temporal partition constraints. Streamlit AppTest exercises all six pages, form submission, batch examples, empty filters and evaluation views. The notebook executes analysis cells using a kernel tied to the current Python environment. Model and raw-data hashes are recorded. Tests are run separately from report generation; reports do not imply that a skipped test succeeded.

Reproduce with SETUP.bat, then START_PROJECT.bat. To rebuild: python train.py, python scripts/build_deliverables.py, and python -m pytest -q from the project environment. Package versions are recorded in requirements-lock.txt and artifacts/metadata.json. Once dependencies, raw data and model artifacts are present, normal analysis and prediction work offline.

## 8. Limitations and future work

The hotels, geography, historical period and commercial policies are narrow. Neither current Indian hotels nor new hotel chains have been evaluated. Final-record data do not prove booking-time availability for every field. The proxy creation date has day-level precision. Earlier mature-cohort filtering and missing booking identifiers limit representativeness and independence. Estimated probabilities are uncalibrated and should not be treated as certainty. No prospective operating trial or causal intervention was performed.

Future work should collect immutable booking snapshots, stable anonymized booking IDs and timestamped outcomes. Evaluate rolling origin periods and genuinely separate hotels, then calibrate probabilities on a separate calibration partition. Follow-up costs and missed-cancellation costs could inform an operational threshold. A real deployment needs appropriate data handling and policy checks before connecting to a PMS.

## 9. Conclusion

The project delivers a functioning cancellation classifier and an interactive way to inspect booking patterns. Its value is the complete, reproducible workflow and explicit interpretation of model errors. The results show useful historical ranking performance while leaving the limitations visible.

## References

1. Antonio, de Almeida and Nunes (2019). Hotel booking demand datasets. {PAPER_URL}
2. TidyTuesday, 11 February 2020. {MIRROR_URL}
3. scikit-learn, Common pitfalls. https://scikit-learn.org/stable/common_pitfalls.html
4. scikit-learn, Model evaluation. https://scikit-learn.org/stable/modules/model_evaluation.html
5. Streamlit documentation. https://docs.streamlit.io/
'''
(REPORTS/'PROJECT_REPORT.md').write_text(content,encoding='utf-8')
(REPORTS/'RESULTS.md').write_text('# Experiment results\n\n'+markdown_table(metrics)+'\n\n'+markdown_table(comparison)+'\n\n'+markdown_table(partitions),encoding='utf-8')

# Render the printable report, then embed its figures so the HTML is portable.
import markdown
rendered=markdown.markdown(content, extensions=['tables'])
for filename in FIGURES.glob('*.png'):
    encoded=base64.b64encode(filename.read_bytes()).decode('ascii')
    rendered=rendered.replace(f'src="figures/{filename.name}"',f'src="data:image/png;base64,{encoded}"')
html_doc='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Booked or Cancelled? Project report</title><style>
body{font-family:Segoe UI,Arial,sans-serif;color:#162f36;background:#f6f5f1;line-height:1.6;margin:0}main{max-width:1000px;margin:32px auto;padding:50px;background:white}h1{font-size:42px;color:#087f8c;line-height:1.15}h2{margin-top:38px;line-height:1.3}table{border-collapse:collapse;width:100%;font-size:12px;display:block;overflow-x:auto}td,th{border:1px solid #d6e0e0;padding:8px;text-align:left}th{background:#e8f1f1}img{max-width:100%;height:auto}a{color:#087f8c;overflow-wrap:anywhere}p{overflow-wrap:anywhere}code{background:#eef3f3} @media print{body{background:white}main{margin:0;padding:0;max-width:none}h2{break-after:avoid}table,figure,img{break-inside:avoid}a{color:inherit}h1{font-size:30px}body{font-size:10pt}img{max-height:140mm;object-fit:contain}}
</style></head><body><main>'''+rendered+'</main></body></html>'
(REPORTS/'PROJECT_REPORT.html').write_text(html_doc,encoding='utf-8')

# This notebook contains runnable analysis, an actual training example, metrics
# computed again from the distributed model, and embedded Matplotlib figures.
cells=[]
def md(value): cells.append(nbformat.v4.new_markdown_cell(value))
def code(value): cells.append(nbformat.v4.new_code_cell(value))
md('# Booked or Cancelled?\n## Predicting hotel booking cancellations and discovering booking patterns\n\nVSEC Data Science Laboratory. Use the project Python environment. This notebook reads the full real dataset and executes analysis code. All results refer to historical data.')
code("from pathlib import Path\nimport sys, json\nROOT = Path.cwd()\nif not (ROOT / 'src').exists():\n    ROOT = ROOT.parent\nassert (ROOT / 'src').exists(), 'Start Jupyter in the project directory.'\nsys.path.insert(0, str(ROOT))\nimport numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport joblib\nfrom src.data import load_data, chronological_split\nfrom src.features import make_features\nfrom src.config import MODEL_PATH, METADATA_PATH, REPORTS, SEED\nfrom src.model import make_pipeline\nfrom src.evaluation import evaluate\nfrom sklearn.linear_model import LogisticRegression\ndata = load_data()\nmetadata = json.loads(METADATA_PATH.read_text(encoding='utf-8'))\nprint(data.shape)\ndata.head()")
md('## 1. Target and data quality\nOne row describes a reservation. is_canceled=1 indicates cancellation. is_canceled=0 is not a guaranteed check-in. Identical-looking rows remain because a booking identifier is unavailable.')
code("pd.DataFrame({'dtype': data.dtypes.astype(str), 'missing': data.isna().sum()})")
code("print('Raw cancellation rate:', round(data.is_canceled.mean(),4))\nprint('Exact duplicate-looking source rows:', metadata['exact_duplicate_rows'])\nprint('Model exclusions:', metadata['excluded_rows'])\ndata.groupby('hotel').is_canceled.agg(['size','mean'])")
md('## 2. Observed booking patterns\nCalendar coverage is incomplete in 2015 and 2017. Group associations are descriptive rather than causal.')
code("monthly = data.assign(month=data.arrival_date.dt.to_period('M').dt.to_timestamp()).groupby(['month','hotel']).size().unstack(fill_value=0)\nmonthly.plot(figsize=(11,4), color=['#087f8c','#d77741'], title='Scheduled arrival bookings by month')\nplt.ylabel('Bookings')\nplt.show()")
code("channels = data.groupby('market_segment').is_canceled.agg(bookings='size', cancellations='sum', rate='mean').sort_values('rate')\nchannels['rate'].plot.barh(figsize=(8,4),color='#087f8c',title='Observed cancellation rate by channel')\nplt.xlabel('Cancellation rate')\nplt.show()\nchannels")
md('## 3. Chronological partitions and label availability\nBooking date proxy = arrival minus lead time. Earlier cohorts require completed planned stays and recorded outcomes before the next period. This removes unresolved earlier records and limits cohort coverage. Final status dates serve this evaluation guard only.')
code("invalid = (data.total_guests < 1) | (data.total_nights < 1) | (data.adr < 0) | data.arrival_date.isna()\nparts = chronological_split(data.loc[~invalid].copy())\npd.DataFrame([{'partition':k,'rows':len(v),'start':v.booking_date_proxy.min(),'end':v.booking_date_proxy.max(),'cancelled':v.is_canceled.mean()} for k,v in parts.items()])")
code("X_train = make_features(parts['train'])\ny_train = parts['train'].is_canceled.astype(int)\nX_validation = make_features(parts['validation'])\ny_validation = parts['validation'].is_canceled.astype(int)\nassert 'reservation_status' not in X_train\nassert 'reservation_status_date' not in X_train\nassert parts['train'].booking_date_proxy.max() < parts['validation'].booking_date_proxy.min()\nassert parts['validation'].booking_date_proxy.max() < parts['test'].booking_date_proxy.min()\nX_train.head()")
md('## 4. Train an interpretable baseline\nThe pipeline fits imputers, numeric scaling and one-hot encoding on training data only. The complete three-algorithm experiment lives in train.py. This cell really fits logistic regression rather than displaying saved results.')
code("logistic = make_pipeline(LogisticRegression(max_iter=1500,C=1.0,random_state=SEED))\nlogistic.fit(X_train,y_train)\nvalidation_probability = logistic.predict_proba(X_validation)[:,1]\nevaluate(y_validation,validation_probability)")
md('## 5. Compare algorithms\nSaved comparison rows all use threshold 0.50. Model choice uses validation ROC AUC. Test scores are reported after selection.')
code("comparison = pd.read_csv(REPORTS/'model_comparison.csv')\ncomparison[['model','selected','validation_roc_auc','test_roc_auc','test_f1','test_brier_score']]")
md('## 6. Re-evaluate the distributed model\nThis recomputes held-out metrics from the saved fitted pipeline. The threshold comes from validation, not from the test period.')
code("bundle = joblib.load(MODEL_PATH)\nX_test = make_features(parts['test'])\ny_test = parts['test'].is_canceled.astype(int)\nprobability = bundle['pipeline'].predict_proba(X_test)[:,1]\nscores = evaluate(y_test,probability,bundle['threshold'])\nprint(bundle['model_name'], 'threshold', bundle['threshold'])\nscores")
code("from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay\nfig, axes = plt.subplots(1,2,figsize=(11,4))\nConfusionMatrixDisplay.from_predictions(y_test,probability>=bundle['threshold'],display_labels=['Not cancelled','Cancelled'],ax=axes[0],colorbar=False,cmap='GnBu')\nRocCurveDisplay.from_predictions(y_test,probability,ax=axes[1])\nplt.tight_layout()\nplt.show()")
md('## 7. Explain model dependence\nPermutation importance shuffles one feature and measures validation AUC loss. It does not establish causal effects or explain an individual cancellation.')
code("importance = pd.read_csv(REPORTS/'feature_importance.csv')\nimportance.head(10).iloc[::-1].plot.barh(x='feature',y='auc_decrease',legend=False,color='#087f8c',figsize=(9,4))\nplt.xlabel('Decrease in validation ROC AUC')\nplt.show()\nimportance.head(10)")
md('## 8. Score a batch through the same inference path as the GUI')
code("from src.model import score_bookings\nexamples = pd.read_csv(ROOT/'data/samples/example_bookings.csv')\npredictions, warnings = score_bookings(bundle,examples)\nprint(warnings)\npredictions[['input_row','hotel','lead_time','cancellation_probability','prediction']]")
md('## 9. Limitations and next steps\n'+ '\n'.join('- '+v for v in META['limitations'])+'\n\nReproduce the full model experiment with `python train.py`. Run checks with `python -m pytest -q`. For a real hotel, collect timestamped snapshots, use a genuinely separate deployment cohort, and validate probability calibration before using an operational threshold.')
md(f'## References\nOriginal data: {PAPER_URL}\n\nCombined CSV and data dictionary: {MIRROR_URL}\n\nScikit-learn: https://scikit-learn.org/stable/common_pitfalls.html')
notebook=nbformat.v4.new_notebook(cells=cells, metadata={'kernelspec':{'display_name':'Hotel booking project (Python)','language':'python','name':'hotel-bookings'},'language_info':{'name':'python'}})
kernel_root=ROOT/'work/jupyter'
kernel_dir=kernel_root/'kernels/hotel-bookings'
kernel_dir.mkdir(parents=True,exist_ok=True)
(kernel_dir/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Hotel booking project (Python)','language':'python'}),encoding='utf-8')
os.environ['JUPYTER_PATH']=str(kernel_root)+os.pathsep+os.environ.get('JUPYTER_PATH','')
print('Executing analysis notebook…',flush=True)
client=NotebookClient(notebook,timeout=240,kernel_name='hotel-bookings',resources={'metadata':{'path':str(ROOT)}})
client.execute()
nbformat.write(notebook,ROOT/'Hotel_Booking_Analysis.ipynb')
print('Wrote executed notebook, report and six figures.',flush=True)

