from fundingpips_scalper import fundingpips_reward

def make_trades(n=40, profit=1200, start_equity=10000, days=7, dd=0.02):
    """Generate synthetic trades spread over days, with total profit and drawdown."""
    import numpy as np
    import pandas as pd

    np.random.seed(42)
    # Spread profit equally, add noise
    base_pnl = profit / n
    pnls = np.random.normal(base_pnl, abs(base_pnl) * 0.1, size=n)
    # Simulate timestamps over days
    ts = pd.date_range("2024-03-01", periods=days, freq="D")
    timestamps = np.random.choice(ts, size=n)
    # Simulate drawdown by creating a dip at day 3
    if dd > 0:
        dip_idx = np.random.choice(n, max(1, n // 10), replace=False)
        pnls[dip_idx] -= start_equity * dd
    trades = [
        {
            "pnl": float(p),
            "timestamp": str(t),
            "start_equity": start_equity,
        }
        for p, t in zip(pnls, timestamps)
    ]
    return trades

def test_evaluate_positive():
    # 40 trades, profit 12%, 7 days, low dd. Should pass and reward > 0.
    trades = make_trades(n=40, profit=1200, start_equity=10000, days=7, dd=0.02)
    reward = fundingpips_reward.evaluate(trades)
    assert reward > 0

def test_evaluate_too_few_trades():
    trades = make_trades(n=30, profit=1200, start_equity=10000, days=7, dd=0.02)
    reward = fundingpips_reward.evaluate(trades)
    assert reward == -1000

def test_evaluate_drawdown_breach():
    # Drawdown breach
    trades = make_trades(n=40, profit=1200, start_equity=10000, days=7, dd=0.10)
    reward = fundingpips_reward.evaluate(trades)
    assert reward == -1000

def test_evaluate_empty():
    assert fundingpips_reward.evaluate([]) == 0.0
    assert fundingpips_reward.evaluate() == 0.0