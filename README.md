# AI Trading Agent — Paper Trading + IBKR Paper Execution

A self-contained trading-agent simulator and market-data signal advisor for research and testing.

**Safety boundary:** the project supports two non-live execution paths: the in-memory `PaperBroker` and an IBKR **Paper** TWS/IB Gateway adapter locked to port `7497`. No live IBKR endpoint is accepted and no Plus500 order automation is included.

## What it does

- Loads OHLCV candles from CSV for deterministic paper trading.
- Fetches public market candles for analysis with no broker credentials.
- Builds an explainable signal from trend, momentum, and volatility features.
- Applies risk limits before simulated orders.
- Executes simulated orders in the in-memory paper broker.
- Can connect to an already-running IBKR Paper TWS/IB Gateway session.
- Can submit market orders to the IBKR Paper session through the dedicated paper executor.
- Tracks cash, position, fees, equity, and trade history in the local simulator.
- Produces manual-execution signals with reference price, score, and reference SL/TP levels.

## IBKR Paper connection

The repository now contains a real `ibapi` transport for **IBKR Paper only**. The executor rejects every port other than `7497`, so the application cannot be pointed at the normal live TWS/Gateway endpoint.

Install the optional dependency:

```bash
pip install -e '.[ibkr]'
```

Start **IBKR Paper Trading** TWS or IB Gateway with API socket access enabled, using port `7497`. Then verify the connection from the project:

```bash
ibkr-paper-check --host 127.0.0.1 --port 7497 --client-id 7
```

For a Codespace or other remote host, `127.0.0.1` means that remote machine. TWS/Gateway must therefore be reachable from the same host (or through a deliberately configured private network); do not expose the API port publicly.

The code does not store an IBKR username, password, API key, session cookie, or other secret in GitHub.

## Market-data signal mode

The `market-signal` command fetches public market candles and prints an analysis signal. It never submits an order.

Examples:

```bash
market-signal --symbol EURUSD=X --interval 5m --range 1d
market-signal --symbol BTC-USD --interval 5m --range 1d
market-signal --symbol GC=F --interval 5m --range 1d
```

Supported symbols are the symbols accepted by the public Yahoo Finance chart feed. The displayed price is a market-data reference and may be delayed or differ from IBKR's executable bid/ask.

## 24/7 public-data Paper Trading

The `live-paper` command continuously polls public market data and runs the strategy against an in-memory `PaperBroker`. It does not submit IBKR orders.

```bash
live-paper --symbol GC=F --interval 5m --range 1d --cash 1000
```

A continuously running process still requires a host that stays online; a normal Codespace is not a guaranteed 24/7 hosting service.

## Paper Trading

```bash
python -m pytest
paper-trader --data sample_prices.csv --cash 10000
paper-replay --data sample_prices.csv --cash 10000
```

For the €1,000 test case:

```bash
paper-trader --data sample_prices.csv --cash 1000
```

## Project layout

- `ai_trading_agent/broker.py` — in-memory paper broker and execution layer.
- `ai_trading_agent/market_data.py` — public market-data adapter; analysis only.
- `ai_trading_agent/live_signal.py` — market-data signal CLI.
- `ai_trading_agent/live_paper_loop.py` — continuous public-data paper-trading loop.
- `ai_trading_agent/ibkr_paper.py` — IBKR Paper connectivity check.
- `ai_trading_agent/ibkr_paper_executor.py` — IBKR Paper `ibapi` connection and order transport, locked to port 7497.
- `ai_trading_agent/strategy.py` — explainable signal scoring.
- `ai_trading_agent/risk.py` — position/risk constraints.
- `ai_trading_agent/engine.py` — paper-trading event loop.
- `ai_trading_agent/data.py` — CSV market-data loader.
- `tests/` — safety and behavior tests.

## Important

This project remains **paper-only**. Never add IBKR passwords, one-time codes, session cookies, API keys, or other secrets to GitHub. The IBKR executor is intentionally locked to Paper TWS/IB Gateway port `7497` and does not provide a live-trading switch.
