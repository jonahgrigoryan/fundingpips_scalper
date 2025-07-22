import numpy as np
import pandas as pd
from fundingpips_scalper import strategy

def test_ema():
    s = pd.Series([1, 2, 3, 4, 5])
    out = strategy.ema(s, span=2)
    assert np.allclose(out.iloc[0], s.iloc[0])

def test_rsi():
    s = pd.Series([1, 2, 4, 2, 1, 3, 6, 2, 1, 4, 2, 1, 2, 3, 2])
    out = strategy.rsi(s, 5)
    assert len(out) == len(s)
    assert (out >= 0).all() and (out <= 100).all()

def test_find_engulfing():
    df = pd.DataFrame({
        "open": [1, 2, 2.1, 1.9],
        "close": [2, 1.8, 2.2, 1.7]
    })
    out = strategy.find_engulfing(df)
    assert len(out) == len(df)
    assert out.dtype == bool

def test_rf_filter_stub():
    arr = np.array([1, -1, 0, 1])
    out = strategy.rf_filter_stub(arr)
    assert np.array_equal(arr, out)

def test_generate_signals_synthetic():
    # Should run and return a list (likely non-empty on default random data)
    signals = strategy.generate_signals()
    assert isinstance(signals, list)
    assert all(isinstance(d, dict) and "time" in d and "signal" in d for d in signals)

def test_generate_signals_toydata():
    # Construct toy data with engineered signals
    idx = pd.date_range("2024-01-01", periods=10, freq="15min", tz="UTC")
    base = np.linspace(1.10, 1.12, 10)
    df = pd.DataFrame({
        "datetime": idx,
        "open": base - 0.0002,
        "high": base + 0.0003,
        "low": base - 0.0003,
        "close": base,
        "volume": np.random.randint(100, 200, size=10)
    })
    signals = strategy.generate_signals(prices=df)
    assert isinstance(signals, list)
    for s in signals:
        assert "time" in s and "signal" in s and s["signal"] in (-1, 1)