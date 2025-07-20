import pandas as pd
import pandas as pd
from fundingpips_scalper import data_prep
from pathlib import Path

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
    # Use a path that surely does not exist
    df = data_prep.load_data(path="definitely_missing_file_123.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 10  # Should have at least n_days=10 rows
from pathlib import Path

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
    # Use a path that surely does not exist
    df = data_prep.load_data(path="definitely_missing_file_123.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 10  # Should have at least n_days=10 rows