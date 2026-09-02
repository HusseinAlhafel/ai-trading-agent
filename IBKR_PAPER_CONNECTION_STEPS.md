# IBKR Paper Connection Steps

1. Start IBKR TWS or IB Gateway.
2. Sign in to the IBKR Paper Trading account.
3. Enable socket/API connections.
4. Set socket port to 7497.
5. In this repository run:

```bash
python scripts/ibkr_paper_preflight.py
```

6. Then run the existing IBKR Paper connection check documented in the README.
7. Keep order placement in Paper mode only.

The repository does not accept or enable a live IBKR endpoint. The preflight refuses ports other than 7497 and does not submit orders.
