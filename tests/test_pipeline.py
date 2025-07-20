from fundingpips_scalper import data_prep
from pathlib import Path

def test_load_data():
    assert data_prep.load_data()

def test_fixture_exists():
    f = Path("tests/fixtures/EURUSD_M15_sample.csv")
    assert f.exists()

def test_load_sample_fixture_direct():
    assert data_prep.load_data("tests/fixtures/EURUSD_M15_sample.csv")