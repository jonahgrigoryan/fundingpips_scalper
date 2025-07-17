# =====================  PROJECT OVERVIEW  =====================
Build a complete, runnable Python repository named **“fundingpips‑scalper”** that develops, optimises and exports a MetaTrader 5 Expert Advisor (EA) for scalping EURUSD on the M15 timeframe.

**Success targets**

* Pass FundingPips One‑Step Evaluation within **5‑7 broker‑server trading days**  
  – Profit ≥ 10 % on $10 000 demo balance  
  – Max daily drawdown < 3 %, overall drawdown < 6 %
* Live‑trading scalability (same rules, but ongoing > 60 % win‑rate, Sharpe > 1.5)

Genie must **autonomously** plan, code, debug and test, but **PAUSE** for my review at three checkpoints (see STOP tokens).

GPU compute is available locally; no cloud provisioning needed.

---

# =====================  REPOSITORY LAYOUT  =====================
fundingpips-scalper/
│
├─ src/
│   ├─ __init__.py
│   ├─ data_prep.py
│   ├─ strategy.py
│   ├─ fundingpips_reward.py
│   ├─ run_self_loop.py
│   └─ inject_params.py
│
├─ config/
│   └─ rdagent.yaml
│
├─ ea/
│   ├─ EA_template.mq5
│   └─ MyOptimizedEA.mq5         # generated
│
├─ tests/
│   ├─ fixtures/EURUSD_M15_sample.csv
│   ├─ test_strategy.py
│   ├─ test_reward.py
│   └─ test_pipeline.py
│
├─ runs/                         # auto‑created
│
├─ environment.yml
├─ requirements-strict.txt
├─ Dockerfile
├─ .gitignore
├─ .env.template
├─ pyproject.toml                # Ruff + Black + PyTest
├─ .github/workflows/ci.yml
├─ CONTRIBUTING.md
└─ README.md

---

# =====================  ENVIRONMENT VERSIONS  =====================
environment.yml (Conda, arm64‑compatible)

```yaml
name: fundingpips
channels: [conda-forge]
dependencies:
  - python=3.11
  - numpy=1.27
  - pandas=3.0
  - ta-lib=0.5.0
  - qlib=0.9
  - rd-agent=0.7.0
  - MetaTrader5=5.0.45
  - scikit-learn
  - requests
  - pytest
  - pytest-cov
  - ruff
  - black
  - pyyaml
  - tqdm

Generate requirements-strict.txt by freezing the solved env for non‑Conda users.

===================== QUALITY & CI RULES =====================
GitHub Actions workflow (ci.yml) defines two jobs Genie must keep green:

pytest (unit + integration tests + pytest --cov=src --cov-fail-under=90)

backtest-ci (headless 1‑day sample back‑test; must finish < 5 min)

CI fails on ANY Ruff error (run ruff check --select E,F).

Genie’s self‑correction loop should watch these job names; iterate until both succeed.

===================== CHECKPOINTS & STOP TOKENS =====================
1. Planning phase – Output full execution plan, then print
---END-PLAN-STOP---
…and wait.
2. Optimisation phase – After completing RD‑Agent optimisation, print
---END-OPTIMISATION-STOP---
…and wait.
3. Export phase – Just before pushing the PR / repo output, print
---END-EXPORT-STOP---
…and wait for my final go‑ahead.
Genie must not continue beyond each STOP until I reply.
===================== DATA PREPARATION RULES =====================
Assume I will supply EURUSD_M15.csv covering Jan 2022 – Jun 2025 for full back‑tests.

For tests/CI, use the committed fixture fixtures/EURUSD_M15_sample.csv (2024‑03‑01 → 03‑03).

Convert data to Qlib format at ~/.qlib/qlib_data/forex with cache_mode="readwrite".

Forward‑fill ≤ 15‑min gaps; drop larger gaps; normalise to UTC.

If no historical data present, generate ≥ 10 synthetic trading days to allow unit tests to run.

===================== STRATEGY AND RISK SPEC =====================
Symbol: "EURUSD" only.

Core logic: EMA crossover (fast 3‑10, slow 5‑15) + RSI filter + engulfing pattern + RandomForest signal filter; confirm H4 bias.

Risk & MM: ATR‑based SL 1‑3×, TP 2‑4×, 0.5‑0.75 % equity risk/trade, max 5 open trades, stop‑profit +2 % / stop‑loss −1.5 % per day, halt EA if equity < 94 % starting balance.

Filters: Spread ≤ 1.5 pips, skip high‑impact EUR/USD news ±10 min (MT5 copy_calendar fallback to ForexFactory).

Drawdown guards: Pause on 3 consecutive losses, enforce daily/server‑based DD < 3 %.

===================== RD‑AGENT CONFIG (config/rdagent.yaml) =====================

version: 1
algorithm: hebo
population_size: 50
mutation_rate: 0.1
budget: 1000
max_runtime_seconds: 7200
objective:
  primary: fundingpips_reward        # defined below
data_split:
  train: 70
  walk_forward: 30
search_space:
  ema_fast: [3, 10]
  ema_slow: [5, 15]
  rsi_period: [10, 20]
  rsi_hi: [70, 80]
  rsi_lo: [20, 30]
  atr_sl: [1, 3]
  atr_tp: [2, 4]
  n_estimators: [50, 200]
  ...
callbacks:
  - ExportBest                       # writes best_params.json

===================== REWARD FUNCTION =====================
Rolling 7‑day windows over ≥ 15 days data.

Reward = net_profit − penalty(drawdowns, volatility, ≤ 35 trades) + bonus(Sharpe>1.5, WinRate>60 %).

Return −1000 if constraints unmet (profit < 10 %, DD limits breached, < 35 trades, < 5 trading days).

===================== EA GENERATION & INJECTOR =====================
EA_template.mq5 contains placeholders for ALL tunable params, including a “ML Toggle”.

inject_params.py reads best_params.json and writes MyOptimizedEA.mq5.

EA must monitor server‑day equity and disable itself if equity < 94 % start_balance.

Add #property strict and compile‑clean on MetaEditor 5.

===================== DOCUMENTATION & SUPPORT =====================
README.md — setup (Mac ARM via Conda), how to supply data, optimisation workflow, FundingPips checklist, live‑scaling steps, MT5 install via PlayOnMac.

CONTRIBUTING.md — how to run tests, lint, optimisation loop, and push PRs.

No licence file required.

===================== EXECUTION ORDER (tickets) =====================

1. Ticket 1 – Repo scaffold
Create all empty/direct‑template files & CI, ensure pytest job passes trivially.
2. Ticket 2 – Data pipeline
Implement data_prep.py, fixture load, Qlib init.
3. Ticket 3 – Strategy logic
Implement strategy.py incl. ML classes, risk filters.
4. Ticket 4 – Reward function
Implement fundingpips_reward.py, integrate with RD‑Agent.
5. Ticket 5 – Optimisation loop
Complete run_self_loop.py, rdagent.yaml, ensure checkpoint STOP.
6. Ticket 6 – EA templating & injection
Fill EA_template.mq5 plus inject_params.py, parity check tests.
7. Ticket 7 – Docs polish & final export
Flesh out README, CONTRIBUTING, generate requirements-strict.txt, compile EA, print STOP.

Genie: work ticket‑by‑ticket, committing and pushing as you proceed. After each ticket group completes, verify CI, then move on.

---END OF PROMPT---