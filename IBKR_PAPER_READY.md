# IBKR Paper Trading Readiness

This repository is prepared for **IBKR Paper Trading only**.

## Safety boundary

- IBKR Paper endpoint/port: **7497**.
- Live IBKR endpoint/port: **not supported by this project**.
- No live credentials are stored in the repository.
- The in-memory `PaperBroker` remains the default simulator.
- Connecting to IBKR Paper must be an explicit local configuration step.

## Before connecting

1. Install and open IBKR Trader Workstation (TWS) or IB Gateway.
2. Log in using an **IBKR Paper Trading** account.
3. Enable API/socket connections in TWS/Gateway.
4. Use socket port **7497**.
5. Keep API order placement disabled until the paper connection check succeeds.
6. Run the repository's paper connection check.

## Validation sequence

Run these in order:

```bash
python -m pytest -q
python -m ai_trading_agent.ibkr_paper
```

Then use the repository's documented IBKR Paper check/executor flow. Do not change the configured port to a live-trading port.

## Important

A successful API connection only proves that the application can communicate with the IBKR Paper session. It does **not** prove that the strategy is profitable or safe for live capital.

The project must remain Paper Trading until performance, execution, risk controls, and operational monitoring have been independently validated.
