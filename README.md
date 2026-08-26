# AI Trading Agent — Paper Trading + Manual Plus500 Signals

A self-contained trading-agent simulator and market-data signal advisor for research and testing.

**Safety boundary:** the default execution path is `PaperBroker`. The Plus500 path is **signal-only**: it produces BUY/SELL/WAIT guidance for manual review and has no Plus500 login, browser automation, API credentials, or order-submission code.

## What it does

- Loads OHLCV candles from CSV for deterministic paper trading.
- Fetches public market candles for analysis with no broker credentials.
- Builds an explainable signal from trend, momentum, and volatility features.
- Applies risk limits before simulated orders.
- Executes simulated BUY/SELL orders in the in-memory paper broker.
- Tracks cash, position, fees, equity, and trade history.
- Produces a manual-execution signal with reference price, score, and reference SL/TP levels.

## Market-data signal mode

The `market-signal` command fetches public market candles and prints an analysis signal. It never submits an order.

Examples:

```bash
python -m ai_trading_agent.live_signal --symbol EURUSD=X --interval 5m --range 1d
python -m ai_trading_agent.live_signal --symbol BTC-USD --interval 5m --range 1d
python -m ai_trading_agent.live_signal --symbol GC=F --interval 5m --range 1d
```

Supported symbols are the symbols accepted by the public Yahoo Finance chart feed. The displayed price is a market-data reference and may be delayed or differ from Plus500's executable bid/ask.

Output includes:

- `Signal`: BUY, SELL, or WAIT
- `Score`: strategy score
- `Reason`: explainable trend/momentum/volatility rationale
- `Last price`: latest market-data close
- `Reference SL` / `Reference TP`: model-derived reference levels when a directional signal exists
- Execution: always manual; no broker order is sent

## Plus500 boundary

This project does not log in to or automate the ordinary Plus500 CFD application. It is intentionally designed so the agent analyzes market data while the user retains manual control of any real-money action.

Plus500 has separate futures infrastructure with API capabilities, but that is a different product and does not turn an ordinary Plus500 CFD account into an API trading account.

## Paper Trading

```bash
python -m pytest
python -m ai_trading_agent.main --data sample_prices.csv --cash 10000
```

## Project layout

- `ai_trading_agent/broker.py` — paper broker and execution layer.
- `ai_trading_agent/market_data.py` — public market-data adapter; analysis only.
- `ai_trading_agent/live_signal.py` — market-data signal CLI.
- `ai_trading_agent/strategy.py` — explainable signal scoring.
- `ai_trading_agent/risk.py` — position/risk constraints.
- `ai_trading_agent/engine.py` — paper-trading event loop.
- `ai_trading_agent/data.py` — CSV market-data loader.
- `tests/` — safety and behavior tests.

## Important

This project does **not** submit real-money orders to Plus500. Never add Plus500 passwords, one-time codes, session cookies, API keys, or other secrets to GitHub.
