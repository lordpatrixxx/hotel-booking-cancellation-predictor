from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]


def app():
    return AppTest.from_file(str(ROOT/'app.py'),default_timeout=45).run()


@pytest.mark.parametrize('page',['overview','patterns','predict','batch','models','guide'])
def test_every_page_renders(page):
    at=app()
    if page!='overview': at.switch_page(f'app_pages/{page}.py').run()
    assert not at.exception


def test_single_prediction_and_reject_zero_nights():
    at=app().switch_page('app_pages/predict.py').run()
    at.button(key='predict_submit').click().run()
    assert not at.exception and 'prediction_result' in at.session_state
    at.number_input[1].set_value(0)
    at.number_input[2].set_value(0)
    at.button(key='predict_submit').click().run()
    assert not at.exception and at.error


def test_batch_examples_and_empty_pattern_filters():
    at=app().switch_page('app_pages/batch.py').run()
    at.button(key='batch_score').click().run()
    assert not at.exception
    assert len(at.session_state['batch_result'])==10
    at.switch_page('app_pages/patterns.py').run()
    at.multiselect(key='patterns_hotels').set_value([]).run()
    assert not at.exception and at.info


def test_model_views():
    at=app().switch_page('app_pages/models.py').run()
    for section in ['Model comparison','Feature importance','Methodology','Errors and curves']:
        at.session_state['model_section']=section
        at.run()
        assert not at.exception
