import json
import joblib
import numpy as np
import pandas as pd
import pytest
from src.config import ROOT, DATA, FEATURES, MODEL_PATH, EXCLUDED
from src.data import load_data, chronological_split
from src.features import make_features, validate_bookings
from src.model import score_bookings
from src.ui import csv_bytes


@pytest.fixture(scope='module')
def examples():
    return pd.read_csv(DATA/'samples/example_bookings.csv')


@pytest.fixture(scope='module')
def bundle():
    return joblib.load(MODEL_PATH)


def test_outcome_fields_never_change_predictions(examples,bundle):
    baseline,_=score_bookings(bundle,examples)
    adversarial=examples.assign(is_canceled=1,reservation_status='Canceled',reservation_status_date='2035-12-31',booking_changes=999,assigned_room_type='Z',country='XXX',total_of_special_requests=200)
    changed,_=score_bookings(bundle,adversarial)
    np.testing.assert_allclose(baseline.cancellation_probability,changed.cancellation_probability)
    assert set(make_features(adversarial)) == set(FEATURES)
    assert set(EXCLUDED).isdisjoint(make_features(adversarial).columns)


@pytest.mark.parametrize('column,value', [('lead_time',-1),('adults',1.5),('adr',np.inf),('adr',-3),('arrival_date_month','january'),('is_repeated_guest',2),('hotel','Unknown hotel')])
def test_bad_values_rejected(examples,column,value):
    frame=examples.head(1).copy()
    frame[column]=value
    with pytest.raises(ValueError): validate_bookings(frame)


def test_invalid_calendar_date(examples):
    row=examples.head(1).assign(arrival_date_month='February',arrival_date_day_of_month=30)
    with pytest.raises(ValueError,match='does not exist'): validate_bookings(row)


def test_zero_stays_and_zero_guests_rejected(examples):
    with pytest.raises(ValueError,match='overnight'): validate_bookings(examples.head(1).assign(stays_in_weekend_nights=0,stays_in_week_nights=0))
    with pytest.raises(ValueError,match='guest'): validate_bookings(examples.head(1).assign(adults=0,children=0,babies=0))


def test_missing_schema_and_empty_input(examples):
    with pytest.raises(ValueError,match='Missing columns'): validate_bookings(examples.drop(columns='adr'))
    with pytest.raises(ValueError,match='no booking rows'): validate_bookings(examples.head(0))


def test_missing_children_and_unknown_category_are_supported(examples,bundle):
    frame=examples.head(1).assign(children=np.nan,meal='NEW_MEAL')
    result,warnings=score_bookings(bundle,frame)
    assert len(result)==1 and np.isfinite(result.cancellation_probability.iloc[0])
    assert any('unseen' in item for item in warnings)
    assert any('median' in item for item in warnings)


def test_threshold_does_not_change_probabilities(examples,bundle):
    low,_=score_bookings(bundle,examples,.1)
    high,_=score_bookings(bundle,examples,.9)
    # Parallel tree aggregation can differ only at machine-precision level.
    np.testing.assert_allclose(low.cancellation_probability,high.cancellation_probability)
    assert low.review_flag.sum() >= high.review_flag.sum()
    with pytest.raises(ValueError): score_bookings(bundle,examples,float('nan'))


def test_batch_matches_individual_rows(examples,bundle):
    batch,_=score_bookings(bundle,examples)
    single=np.array([score_bookings(bundle,examples.iloc[[i]])[0].cancellation_probability.iloc[0] for i in range(len(examples))])
    np.testing.assert_allclose(batch.cancellation_probability,single)
    assert list(batch.input_row)==list(range(1,len(examples)+1))


def test_split_chronology_and_outcome_availability():
    data=load_data()
    eligible=data.loc[(data.total_guests>=1)&(data.total_nights>=1)&(data.adr>=0)&data.arrival_date.notna()]
    groups=chronological_split(eligible)
    assert groups['train'].booking_date_proxy.max() < groups['validation'].booking_date_proxy.min()
    assert groups['validation'].booking_date_proxy.max() < groups['test'].booking_date_proxy.min()
    assert not (set(groups['train'].index)&set(groups['test'].index))
    for name,cutoff in [('train','2016-09-01'),('validation','2017-01-01')]:
        rows=groups[name]
        assert (pd.to_datetime(rows.reservation_status_date)<pd.Timestamp(cutoff)).all()
        assert (rows.arrival_date+pd.to_timedelta(rows.total_nights,unit='D')<pd.Timestamp(cutoff)).all()


def test_spreadsheet_export_escapes_formulas():
    result=csv_bytes(pd.DataFrame({'category':['=HYPERLINK("x")','ordinary']})).decode('utf-8-sig')
    assert "'=HYPERLINK" in result

