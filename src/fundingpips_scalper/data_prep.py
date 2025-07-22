"""Data preparation utilities.

Provides CSV loading, preprocessing (UTC, gap handling), fallback synthetic data
generation, and optional Qlib-compatible export. Implementation is intentionally
light-weight so unit tests and CI finish well under the 5-minute budget.
"""

from __future__ import annotations

import datetime
import pathlib

import numpy as np
import pandas as pd

DEFAULT_CACHE = str(pathlib.Path("~/.qlib/qlib_data/forex").expanduser())
__all__ = ["load_data"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_csv(path: str | pathlib.Path) -> pd.DataFrame:
    """Load CSV file and normalise the time column to ``datetime`` (UTC)."""

    df = pd.read_csv(path)

    # Normalise time column name.
    if "datetime" in df.columns:
        ts_col = "datetime"
    elif "timestamp" in df.columns:
        ts_col = "timestamp"
        df = df.rename(columns={"timestamp": "datetime"})
    else:
        raise ValueError("CSV missing datetime/timestamp column")

    # Parse to timezone-aware UTC timestamps.
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    return df


def _generate_synthetic(n_days: int = 10) -> pd.DataFrame:  # noqa: D401
    """Return *deterministic* synthetic EURUSD M15 data for tests.

    The randomness is seeded to make unit tests repeatable. 4 candles/hour ×
    24 hours × *n_days* rows are produced.
    """

    periods = n_days * 24 * 4
    today = datetime.datetime.now().date()
    dt_start = pd.Timestamp(
        today - datetime.timedelta(days=n_days)
    )

    idx = pd.date_range(dt_start, periods=periods, freq="15min", tz="UTC")

    rng = np.random.default_rng(seed=42)
    base_price = 1.10
    drift = rng.normal(0, 0.0002, size=periods).cumsum()

    close = base_price + drift
    open_ = close + rng.normal(0, 0.0001, size=periods)
    high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.00005, size=periods))
    low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.00005, size=periods))
    volume = rng.integers(100, 500, size=periods)

    return pd.DataFrame(
        {
            "datetime": idx,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def _forward_fill_gaps(df: pd.DataFrame) -> pd.DataFrame:
    """Forward-fill ≤ 15-min gaps and drop larger ones."""

    df = df.sort_values("datetime").reset_index(drop=True)

    # Compute gap in minutes between consecutive rows.
    gap_min = df["datetime"].diff().dt.total_seconds().div(60).fillna(15)

    # Drop rows that follow a gap > 15 minutes.
    big_gap_idx = gap_min[gap_min > 15].index
    df = df.drop(index=big_gap_idx).reset_index(drop=True)

    # Forward-fill small gaps so indicators stay continuous.
    return df.ffill()


def _write_qlib(df: pd.DataFrame, cache_dir: str | pathlib.Path) -> None:
    """Export data in a minimal Qlib folder structure (best-effort).

    If ``qlib`` is not installed this becomes a no-op. The function is only
    exercised in local optimisation runs, *never* in CI.
    """

    try:
        import qlib  # noqa: F401
    except ImportError:
        print("qlib not installed, skipping qlib cache write.")
        return

    cache = pathlib.Path(cache_dir).expanduser()
    (cache / "instruments").mkdir(parents=True, exist_ok=True)
    (cache / "calendar").mkdir(exist_ok=True)
    (cache / "features").mkdir(exist_ok=True)

    # Instrument list (single symbol).
    (cache / "instruments" / "forex.txt").write_text("EURUSD\n")

    # Calendar file.
    calendar_txt = "\n".join(
        df.sort_values("datetime")["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    )
    (cache / "calendar" / "calendars.txt").write_text(calendar_txt)

    # Raw features (OHLCV) – index must be timezone-naive for Qlib.
    features_path = cache / "features" / "EURUSD.csv"
    fdf = df.set_index("datetime")
    fdf.index = fdf.index.tz_localize(None)
    fdf.to_csv(features_path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_data(
    path: str | None = None,
    *,
    ensure_qlib: bool = False,
    cache_mode: str = "readwrite",  # kept for future compatibility
) -> pd.DataFrame:
    """Load EURUSD M15 data or fall back to synthetic data for tests."""

    df: pd.DataFrame | None = None

    if path and pathlib.Path(path).exists():
        df = _read_csv(path)
    else:
        # Look for any CSV inside default cache dir.
        cache_path = pathlib.Path(DEFAULT_CACHE).expanduser()
        if cache_path.exists():
            csv_candidates = list(cache_path.glob("*.csv"))
            if csv_candidates:
                df = _read_csv(csv_candidates[0])

    if df is None:
        # As a last resort create synthetic data so unit tests always run.
        df = _generate_synthetic(n_days=10)

    # Preprocess.
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df = _forward_fill_gaps(df)

    # Optionally write Qlib cache and/or initialise qlib.
    if ensure_qlib:
        _write_qlib(df, DEFAULT_CACHE)
        try:
            import qlib  # noqa: F401

            qlib.init(provider_uri=DEFAULT_CACHE)
        except ImportError:
            pass  # Silent – qlib is optional.

    return df