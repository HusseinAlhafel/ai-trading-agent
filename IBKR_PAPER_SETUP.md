# IBKR Paper Trading Setup

This project remains paper-only. This document prepares the repository for a later IBKR Paper Trading integration after the account is approved.

## Current state

- The local simulator uses `PaperBroker` only.
- `ibkr_adapter.py` has no live order submission implementation.
- No IBKR credentials are stored in the repository.
- `paper_loop.py` can run an offline replay indefinitely for soak testing.

## Later paper-session stage

Interactive Brokers documents Paper Trading as a simulated environment for testing strategies. The TWS API connects through TWS or IB Gateway.

For a standard TWS paper session, the default socket port is `7497`. IB Gateway's default paper port is `4002`.

Planned configuration:

```text
IBKR_PAPER_HOST=127.0.0.1
IBKR_PAPER_PORT=7497
IBKR_PAPER_CLIENT_ID=7
TRADING_MODE=PAPER
```

These values are configuration placeholders only. The current build does not connect to them.

## Integration gate

Before enabling an IBKR paper connection:

1. IBKR account approval is complete.
2. A Paper Trading account is available.
3. TWS or IB Gateway is installed on the always-on host.
4. API connections are enabled for the paper session.
5. The application confirms the connected account is the paper account.
6. Market-data access is verified.
7. Order submission is tested only in the paper environment.
8. Restart/reconnect behavior is tested.
9. Risk limits and a kill switch are tested.

Live trading is intentionally not part of this build.
