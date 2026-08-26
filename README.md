# AI Trading Agent — Paper Trading Only

A self-contained, deterministic trading-agent simulator for research and testing.

**Safety boundary:** this repository has no live-trading adapter, no exchange/broker credentials, and no code path that can submit real orders. Every order goes to `PaperBroker` and is filled against local/synthetic prices.

## What it does

- Loads OHLCV candles from CSV.
- Builds an explainable signal from trend, momentum, and volatility features.
- Applies risk limits before every simulated order.
- Executes BUY/SELL orders only in the in-memory paper broker.
- Tracks cash, position, fees, equity, and trade history.
- Produces a final paper-trading report.
- Runs entirely offline with Python's standard library.

## Run

```bash
python -m pytest
python -m ai_trading_agent.main --data sample_prices.csv --cash 10000
```

The sample run is deterministic, so it is suitable for CI and experimentation.

## Project layout

- `ai_trading_agent/broker.py` — paper broker; the only execution layer.
- `ai_trading_agent/strategy.py` — explainable signal scoring.
- `ai_trading_agent/risk.py` — position/risk constraints.
- `ai_trading_agent/engine.py` — event loop connecting data, strategy, risk, and broker.
- `ai_trading_agent/data.py` — CSV market-data loader.
- `tests/` — safety and behavior tests.

## Explicit non-goals

This project does **not** connect to Plus500, a stock/crypto exchange, a bank, or any live broker. Do not add API keys or live order endpoints to this repository.
