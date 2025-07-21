import datetime
import pathlib
import typing

import numpy as np
import pandas as pd

DEFAULT_CACHE = str(pathlib.Path("~/.qlib/qlib_data/forex").expanduser())
__all__ = ["load_data"]

...

    today = datetime.datetime.now().date()
    dt_start = pd.Timestamp(today - datetime.timedelta(days=n_days))
    datetimes = pd.date_range(dt_start, periods=periods, freq="15min", tz="UTC")
    np.random.seed(42)
    base_price = 1.10
    spread = 0.0001
    price_noise = np.random.normal(0, 0.001, size=periods).cumsum()
    close = base_price + price_noise
    open_ = close + np.random.normal(0, 0.0002, size=periods)
    high = np.maximum(open_, close) + np.abs(np.random.normal(0, spread, size=periods))
    low = np.minimum(open_, close) - np.abs(np.random.normal(0, spread, size=periods))
    volume = np.random.randint(100, 500, size=periods)
    df = pd.DataFrame(
        {
            "datetime": datetimes,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )
    return df


def _forward_fill_gaps(df: pd.DataFrame) -> pd.DataFrame:
    # Assume df is sorted by datetime
    df = df.sort_values("datetime").reset_index(drop=True)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    # Calculate time difference between consecutive bars in minutes
    time_deltas = df["datetime"].diff().dt.total_seconds().div(60).fillna(15)
    # Mark rows where gap is more than 15 min
    mask_gap = time_deltas > 15
    # Remove rows after big gaps
    rows_to_drop = mask_gap[mask_gap].index
    df = df.drop(index=rows_to_drop).reset_index(drop=True)
    df = df.ffill()
    return df


def _write_qlib(df: pd.DataFrame, cache_dir: typing.Union[str, pathlib.Path]) -> None:
    try:
        import qlib  # noqa: F401
    except ImportError:
        print("qlib not installed, skipping qlib cache write.")
        return

    cache_dir = pathlib.Path(cache_dir).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    # Qlib expects a folder structure: cache_dir/instruments/forex.txt, cache_dir/{calendar,features}/
    inst_dir = cache_dir / "instruments"
    inst_dir.mkdir(exist_ok=True)
    # Write instrument file (single instrument "EURUSD")
    (inst_dir / "forex.txt").write_text("EURUSD\n")
    # Write calendar file
    calendar_dir = cache_dir / "calendar"
    calendar_dir.mkdir(exist_ok=True)
    calendar_path = calendar_dir / "calendars.txt"
    df_sorted = df.sort_values("datetime")
    calendar_path.write_text("\n".join(df_sorted["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")))
    # Write features file
    features_dir = cache_dir / "features"
    features_dir.mkdir(exist_ok=True)
    features_path = features_dir / "EURUSD.csv"
    features_df = df_sorted.copy()
    features_df = features_df.set_index("datetime")
    features_df.index = features_df.index.tz_localize(None)
    features_df.to_csv(features_path)
    print(f"Qlib-style data written to {cache_dir}")
    return


def load_data(
    path: typing.Optional[str] = None,
    cache_mode: str = "readwrite",
    ensure_qlib: bool = False,
) -> pd.DataFrame:
    # Try to load from path if provided
    df = None
    if path is not None and pathlib.Path(path).exists():
        df = _read_csv(path)
    elif pathlib.Path(DEFAULT_CACHE).expanduser().exists():
        # Try default cache location (CSV expected in there)
        possible_csvs = list(pathlib.Path(DEFAULT_CACHE).expanduser().glob("*.csv"))
        if possible_csvs:
            df = _read_csv(possible_csvs[0])
    if df is None:
        df = _generate_synthetic(n_days=10)

    # Preprocess: timezone to UTC, sort, fill/drop gaps
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df = df.sort_values("datetime").reset_index(drop=True)
    df = _forward_fill_gaps(df)
    # Optionally write to qlib cache and init qlib
    if ensure_qlib:
        _write_qlib(df, DEFAULT_CACHE)
        try:
            import qlib

            qlib.init(provider_uri=DEFAULT_CACHE)
        except ImportError:
            print("qlib not installed, skipping qlib.init().")
    return df