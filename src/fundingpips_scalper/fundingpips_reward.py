"""FundingPips reward function for strategy optimization."""

__all__ = ["evaluate"]

import numpy as np
import pandas as pd

def calculate_net_profit(trades):
    """Net profit in percent."""
    pnl = np.array([t["pnl"] for t in trades])
    start_equity = trades[0].get("start_equity", 10000) if trades else 10000
    return_pct = 100 * pnl.sum() / start_equity if start_equity > 0 else 0.0
    return return_pct

def calculate_drawdowns(trades):
    """Overall and daily drawdown."""
    pnl = np.array([t["pnl"] for t in trades])
    timestamps = np.array([pd.Timestamp(t["timestamp"]) for t in trades])
    if pnl.size == 0:
        return 0.0, 0.0  # pragma: no cover
    start_equity = trades[0].get("start_equity", 10000)
    equity_curve = start_equity + np.cumsum(pnl)
    # Overall drawdown
    peak = np.maximum.accumulate(equity_curve)
    dd = (peak - equity_curve) / peak
    max_dd = np.max(dd) if dd.size > 0 else 0.0
    # Daily max drawdown
    df = pd.DataFrame({"equity": equity_curve, "timestamp": timestamps})
    df["day"] = df["timestamp"].dt.date
    max_daily_dd = 0.0
    for _, group in df.groupby("day"):
        eq = group["equity"].values
        peak = np.maximum.accumulate(eq)
        dd = (peak - eq) / peak
        max_daily_dd = max(max_daily_dd, np.max(dd) if dd.size > 0 else 0.0)
    return max_dd, max_daily_dd

def calculate_sharpe(trades):
    """Sharpe ratio (daily returns, risk-free=0)."""
    if len(trades) < 2:
        return 0.0  # pragma: no cover
    pnl = np.array([t["pnl"] for t in trades])
    start_equity = trades[0].get("start_equity", 10000)
    equity_curve = start_equity + np.cumsum(pnl)
    returns = np.diff(equity_curve) / equity_curve[:-1]
    if returns.std() == 0:
        return 0.0  # pragma: no cover
    sharpe = returns.mean() / (returns.std() + 1e-8) * np.sqrt(252)
    return sharpe

def win_rate(trades):
    """Win rate percent."""
    if not trades:
        return 0.0  # pragma: no cover
    wins = sum(1 for t in trades if t["pnl"] > 0)
    return 100 * wins / len(trades)

def volatility(trades):
    """Standard deviation of trade returns."""
    if len(trades) < 2:
        return 0.0  # pragma: no cover
    pnl = np.array([t["pnl"] for t in trades])
    return np.std(pnl)

def trading_days(trades):
    if not trades:
        return 0  # pragma: no cover
    ts = pd.to_datetime([t["timestamp"] for t in trades])
    return ts.dt.normalize().nunique()

def evaluate(trades=None) -> float:
    """
    FundingPips reward:
    - If constraints (profit, drawdown, trade count, days) not met: -1000.
    - Else, reward = net_profit - penalty(drawdown, volatility, ≤35 trades) + bonus(Sharpe>1.5, winrate>60%).
    """
    if trades is None:
        return 0.0
    if len(trades) == 0:
        return 0.0
    # Constraints
    min_profit = 10.0  # percent
    max_dd = 0.06
    max_daily_dd = 0.03
    min_trades = 35
    min_days = 5

    n_trades = len(trades)
    n_days = trading_days(trades)
    net_profit = calculate_net_profit(trades)
    dd, daily_dd = calculate_drawdowns(trades)

    # Hard constraints
    if (
        n_trades < min_trades
        or n_days < min_days
        or net_profit < min_profit
        or dd > max_dd
        or daily_dd > max_daily_dd
    ):
        return -1000.0

    # Metrics for reward
    sharpe = calculate_sharpe(trades)
    win = win_rate(trades)
    vol = volatility(trades)

    # Penalties
    penalty = 0.0
    if dd > 0.04:
        penalty += 10 * (dd - 0.04) * 100  # heavier penalty for >4% dd
    if vol > 0.005:
        penalty += (vol - 0.005) * 1000
    if n_trades < 40:
        penalty += 5 * (40 - n_trades)

    # Bonuses
    bonus = 0.0
    if sharpe > 1.5:
        bonus += 10 * (sharpe - 1.5)
    if win > 60:
        bonus += (win - 60) / 2

    reward = net_profit - penalty + bonus
    return reward