"""EURUSD M15 scalping strategy logic for FundingPips challenge.

Implements EMA crossover, RSI filter, engulfing pattern, RandomForest signal
filter (stub), H4 bias (stub), spread/risk filters (stubs), and core signal
generation. Designed for flexible param injection and easy testing.
"""

import numpy as np
import pandas as pd

__all__ = ["generate_signals", "ema", "rsi", "find_engulfing", "rf_filter_stub"]


def ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential moving average."""
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int) -> pd.Series:
    """Relative Strength Index."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))


def find_engulfing(df: pd.DataFrame) -> pd.Series:
    """Return pd.Series of bool (True if bullish/bearish engulfing pattern found)."""
    # Bullish engulfing: prev red, current green, and current body engulfs prev body
    prev = df.shift(1)
    bullish = (
        (prev["close"] < prev["open"])
        & (df["close"] > df["open"])
        & (df["open"] < prev["close"])
        & (df["close"] > prev["open"])
    )
    bearish = (
        (prev["close"] > prev["open"])
        & (df["close"] < df["open"])
        & (df["open"] > prev["close"])
        & (df["close"] < prev["open"])
    )
    return bullish | bearish


def rf_filter_stub(signals: np.ndarray) -> np.ndarray:
    """RandomForestClassifier filter stub: pass-thru for now, returns input."""
    # Placeholder for actual trained RF model
    return signals


def h4_bias_stub(df: pd.DataFrame) -> pd.Series:
    """Stub: always returns True (for test purposes)."""
    return pd.Series(True, index=df.index)


def spread_filter_stub(df: pd.DataFrame) -> pd.Series:
    """Stub: always returns True (for test purposes)."""
    return pd.Series(True, index=df.index)


def risk_guard_stub(signals: np.ndarray) -> np.ndarray:
    """Stub: always returns input (for test purposes)."""
    return signals


def generate_signals(
    prices: pd.DataFrame = None,
    ema_fast: int = 5,
    ema_slow: int = 10,
    rsi_period: int = 14,
    rsi_hi: int = 70,
    rsi_lo: int = 30,
) -> list:
    """
    Generate scalping signals with EMA crossover, RSI, engulfing, ML, and filters.

    Returns a list of dicts: [{"time": ..., "signal": ...}, ...]
    """
    # For CI, generate synthetic price data if none provided.
    if prices is None:
        idx = pd.date_range("2024-01-01", periods=100, freq="15min", tz="UTC")
        np.random.seed(1)
        close = np.cumsum(np.random.randn(100)) * 0.001 + 1.10
        open_ = close + np.random.normal(0, 0.0001, size=100)
        high = np.maximum(open_, close) + np.abs(np.random.normal(0, 0.0002, size=100))
        low = np.minimum(open_, close) - np.abs(np.random.normal(0, 0.0002, size=100))
        volume = np.random.randint(100, 500, size=100)
        prices = pd.DataFrame(
            dict(
                datetime=idx,
                open=open_,
                high=high,
                low=low,
                close=close,
                volume=volume,
            )
        )
    df = prices.copy()
    df = df.sort_values("datetime").reset_index(drop=True)

    # Core indicators
    df["ema_fast"] = ema(df["close"], ema_fast)
    df["ema_slow"] = ema(df["close"], ema_slow)
    df["rsi"] = rsi(df["close"], rsi_period)
    df["engulfing"] = find_engulfing(df)
    df["h4_bias"] = h4_bias_stub(df)
    df["spread_ok"] = spread_filter_stub(df)

    # Entry logic
    long_entry = (
        (df["ema_fast"] > df["ema_slow"])
        & (df["rsi"] < rsi_hi)
        & df["engulfing"]
        & df["h4_bias"]
        & df["spread_ok"]
    )
    short_entry = (
        (df["ema_fast"] < df["ema_slow"])
        & (df["rsi"] > rsi_lo)
        & df["engulfing"]
        & df["h4_bias"]
        & df["spread_ok"]
    )
    signals = np.zeros(len(df), dtype=int)
    signals[long_entry.values] = 1
    signals[short_entry.values] = -1

    # ML filter (stub)
    signals = rf_filter_stub(signals)

    # Risk guard (stub)
    signals = risk_guard_stub(signals)

    # Output: list of signal dicts
    result = []
    for i, sig in enumerate(signals):
        if sig != 0:
            result.append(
                {
                    "time": df.loc[i, "datetime"],
                    "signal": int(sig),
                }
            )
    return result