# Project Summary: fundingpips-scalper

The goal of this repository is to build a fully-automated workflow that develops, optimises and exports a MetaTrader 5 Expert Advisor (EA) for scalping the EURUSD pair on the 15-minute chart.  

Key objectives
1. **Pass FundingPips One-Step Evaluation**
   • Achieve ≥ 10 % profit on a $10 000 demo account within 5-7 trading days.  
   • Keep maximum daily drawdown < 3 % and overall drawdown < 6 %.
2. **Maintain live-trading performance**  
   • Target > 60 % win-rate and Sharpe ratio > 1.5 with the same risk limits.

Technical highlights
• Strategy combines EMA crossovers (fast 3-10 / slow 5-15), RSI filter, engulfing candle pattern, RandomForest signal filter, and higher-timeframe (H4) bias.  
• Risk management: ATR-based stop-loss (1-3×) & take-profit (2-4×), 0.5-0.75 % equity risk per trade, max 5 concurrent trades, daily equity guards, and auto-pause after consecutive losses.  
• Data pipeline converts EURUSD M15 CSV to Qlib format, forward-fills ≤ 15-min gaps, synthesises data if none supplied.
• Optimisation handled by RD-Agent (HEBO algorithm, 1 000 trials or 2 h budget) using a custom reward that balances profit with drawdowns, volatility, trade count, and performance ratios.
• Continuous Integration enforces ≥ 90 % test coverage, linting (Ruff), and a < 5 min one-day back-test.
• The best hyper-parameters are injected into an EA template to generate `MyOptimizedEA.mq5`, which must compile cleanly under MetaEditor with `#property strict` and include self-destruct logic if equity < 94 %.

Workflow checkpoints
1. **Planning** – Genie outputs execution plan, waits (`---END-PLAN-STOP---`).
2. **Optimisation** – After RD-Agent completes, waits (`---END-OPTIMISATION-STOP---`).
3. **Export** – Before final push/PR, waits (`---END-EXPORT-STOP---`).

Ticket-based development (scaffold → data → strategy → reward → optimisation loop → EA generation → docs) ensures CI passes after each stage.

Deliverables include full source code (`src/`), tests, CI workflow, Docker/Conda env, documentation, and a compiled, ready-to-trade EA. 