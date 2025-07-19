import src.data_prep
from pathlib import Path

def test_load_data():
    assert src.data_prep.load_data()

def test_fixture_exists():
    f = Path("tests/fixtures/EURUSD_M15_sample.csv")
    assert f.exists()

def test_load_sample_fixture_direct():
    # User feedback: load sample file by explicit path
    assert src.data_prep.load_data("tests/fixtures/EURUSD_M15_sample.csv")