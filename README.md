# AI Trading Agent — Paper Trading + Manual Plus500 Signals

A self-contained trading-agent simulator and signal advisor for research and testing.

**Safety boundary:** the default execution path is `PaperBroker`. The Plus500 path is **signal-only**: it produces BUY/SELL/WAIT guidance for manual execution and has no Plus500 login, browser automation, API credentials, or order-submission code.

## What it does

- Loads OHLCV candles from CSV.
- Builds an explainable signal from trend, momentum, and volatility features.
- Applies risk limits before simulated orders.
- Executes simulated BUY/SELL orders in the in-memory paper broker.
- Tracks cash, position, fees, equity, and trade history.
- Produces a final paper-trading report.
- Produces a **manual Plus500 signal** with confidence, reference price, position fraction, and stop-loss/take-profit reference levels.
- Keeps all real-money execution outside the application.

## Manual Plus500 mode

The command below analyzes the supplied market data and prints a signal that you can review and, if you choose, enter manually in Plus500.

```bash
python -m ai_trading_agent.signal_main --data sample_prices.csv --symbol DEMO
```

Example output fields:

- `Signal`: BUY, SELL, or WAIT
- `Confidence`: strategy score converted to a 0–100% confidence indicator
- `Reference price`: latest candle close used by the model
- `Position fraction`: suggested fraction of the configured trading budget
- `Stop-loss reference` / `Take-profit ref.`: calculated reference levels
- `Execution`: always `MANUAL ONLY`

The program explicitly prints `No Plus500 order was submitted.`

## Plus500 compatibility boundary

The ordinary Plus500 CFD platform is not treated as an API execution target by this project. Plus500 user agreements for its CFD services prohibit automated data-entry systems and require transactions to be completed manually.

Plus500 T4/Futures is a separate product with API capabilities, but that does not make its API applicable to an ordinary Plus500 CFD account. This repository therefore does not attempt to bypass the CFD platform's manual-execution requirement.

## Paper Trading

```bash
python -m pytest
python -m ai_trading_agent.main --data sample_prices.csv --cash 10000
```

The sample run is deterministic and suitable for CI and experimentation.

## Project layout

- `ai_trading_agent/broker.py` — paper broker and current execution layer.
- `ai_trading_agent/signal_advisor.py` — signal-only advisor for manual Plus500 execution.
- `ai_trading_agent/signal_main.py` — command-line signal generator.
- `ai_trading_agent/plus500_t4_adapter.py` — safe Plus500 T4 integration boundary; live submission intentionally blocked.
- `ai_trading_agent/strategy.py` — explainable signal scoring.
- `ai_trading_agent/risk.py` — position/risk constraints.
- `ai_trading_agent/engine.py` — event loop connecting data, strategy, risk, and broker.
- `ai_trading_agent/data.py` — CSV market-data loader.
- `tests/` — safety and behavior tests.

## Important

This project does **not** submit real-money orders to Plus500. Never add Plus500 passwords, one-time codes, session cookies, or other secrets to GitHub.
