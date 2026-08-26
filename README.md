# AI Trading Agent — Paper Trading First

A self-contained trading-agent simulator for research and testing.

**Safety boundary:** the default execution path is still `PaperBroker`. No Plus500 credentials are stored in this repository and no live order can be submitted by the current Plus500 adapter.

## What it does

- Loads OHLCV candles from CSV.
- Builds an explainable signal from trend, momentum, and volatility features.
- Applies risk limits before every simulated order.
- Executes simulated BUY/SELL orders in the in-memory paper broker.
- Tracks cash, position, fees, equity, and trade history.
- Produces a final paper-trading report.
- Includes a **Plus500 T4 integration boundary** for future provider-approved connectivity.

## Plus500 T4 status

Plus500's official T4 platform documents an open .NET API and an open FIX API for third-party applications. The exact endpoint, credentials, account permissions, and supported instruments are provider/account dependent.

This repository therefore includes `ai_trading_agent/plus500_t4_adapter.py` as a **safe, non-executing adapter boundary**. It validates configuration and translates orders, but deliberately rejects every live submission until an official T4 implementation and account authorization have been verified.

Environment placeholders are in `.env.example`. Keep `PLUS500_T4_LIVE_TRADING=false` and do not place credentials in GitHub files.

## Run

```bash
python -m pytest
python -m ai_trading_agent.main --data sample_prices.csv --cash 10000
```

The sample run is deterministic and suitable for CI and experimentation.

## Project layout

- `ai_trading_agent/broker.py` — paper broker and current execution layer.
- `ai_trading_agent/plus500_t4_adapter.py` — safe Plus500 T4 integration boundary; live submission intentionally blocked.
- `ai_trading_agent/strategy.py` — explainable signal scoring.
- `ai_trading_agent/risk.py` — position/risk constraints.
- `ai_trading_agent/engine.py` — event loop connecting data, strategy, risk, and broker.
- `ai_trading_agent/data.py` — CSV market-data loader.
- `tests/` — safety and behavior tests, including the T4 execution guard.

## Important

This project is **not yet connected to a live Plus500 account**. Plus500 T4 API access is distinct from the ordinary Plus500 retail CFD platform. No real-money trading is enabled here.
