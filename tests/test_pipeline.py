import pandas as pd
from pathlib import Path
from fundingpips_scalper import data_prep

def test_load_data():
    df = data_prep.load_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_fixture_exists():
    f = Path("tests/fixtures/EURUSD_M15_sample.csv")
    assert f.exists()


def test_load_sample_fixture_direct():
    df = data_prep.load_data("tests/fixtures/EURUSD_M15_sample.csv")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_synthetic_generation():
    df = data_prep.load_data(path="definitely_missing_file_123.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 10