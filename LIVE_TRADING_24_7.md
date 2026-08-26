# 24/7 live-trading deployment plan

The project is prepared for an IBKR execution boundary, but **live trading remains disabled**.

IBKR officially supports automated trading through its Web API and TWS API, including programmatic order placement. Paper Trading can be used first with simulated funds.

## Required before live activation

1. Open and approve an IBKR account with the required market-data and trading permissions.
2. Create/enable an IBKR paper account and verify the strategy there first.
3. Run the agent on a persistent server or managed VM; an iPhone alone is not a suitable 24/7 execution host.
4. Configure API authentication/session securely; never commit credentials to GitHub.
5. Set conservative position and daily-loss limits.
6. Verify order-status, rejection, fill, disconnect, and emergency-stop handling.
7. Keep `IBKR_LIVE_TRADING=false` until all checks are complete.

The agent must never infer that an API connection means live trading is permitted. Live execution requires an explicit deployment decision and working broker permissions.
