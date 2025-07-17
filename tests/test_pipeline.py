import src.data_prep
from pathlib import Path

def test_load_data():
    assert src.data_prep.load_data()

def test_fixture_exists():
    f = Path("tests/fixtures/EURUSD_M15_sample.csv")
    assert f.exists()