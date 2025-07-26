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
    valid = out.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()

def test_find_engulfing():
    df = pd.DataFrame({
        "open": [1, 2, 2.1, 1.9],
        "close": [2, 1.8, 2.2, 1.7]
    })
    out = strategy.find_engulfing(df)
    assert len(out) == len(df)
    assert out.dtype == bool

def test_rf_filter_basic():
    # Make simple feature set that matches signals
    arr = np.array([1, -1, 1, -1, 1, -1, 1, -1, 1, -1])
    features = np.vstack([arr, -arr, arr**2, np.ones_like(arr)]).T
    # Should learn to predict the pattern after training phase
    out = strategy.rf_filter(arr, features, train_size=6, n_estimators=5)
    # First train_size should match
    assert np.array_equal(out[:6], arr[:6])
    # The rest should be -1 or 1 (never 0)
    assert set(np.unique(out[6:])).issubset({-1, 1})

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
        assert "sl" in s and "tp" in s and "size" in s

def test_generate_signals_params():
    # Check that parameterization works and output structure is correct
    idx = pd.date_range("2024-03-01", periods=20, freq="15min", tz="UTC")
    vals = np.linspace(1.105, 1.115, 20)
    df = pd.DataFrame({
        "datetime": idx,
        "open": vals - 0.0001,
        "high": vals + 0.0002,
        "low": vals - 0.0002,
        "close": vals,
        "volume": np.random.randint(120, 240, 20),
    })
    signals = strategy.generate_signals(
        prices=df,
        ema_fast=3,
        ema_slow=6,
        rsi_period=5,
        atr_period=4,
        atr_sl_mult=1.5,
        atr_tp_mult=2.0,
        equity=5000,
        risk_per_trade=0.75,
    )
    assert isinstance(signals, list)
    if signals:
        for s in signals:
            assert isinstance(s["sl"], float)
            assert isinstance(s["tp"], float)
            assert 0.01 <= s["size"] <= 10

def test_rf_filter_importerror(monkeypatch):
    # Simulate sklearn ImportError and ensure fallback works
    import sys

    def fake_import(name, *a, **kw):
        if name == "sklearn.ensemble":
            raise ImportError()
        return orig_import(name, *a, **kw)

    orig_import = __import__
    monkeypatch.setattr("builtins.__import__", fake_import)
    arr = np.array([1, 1, -1, 0])
    features = np.ones((4, 2))
    out = strategy.rf_filter(arr, features)
    assert np.array_equal(out, arr)