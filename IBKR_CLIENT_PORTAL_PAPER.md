# IBKR Client Portal — Paper Trading

The repository now includes a Paper-only Client Portal Gateway session adapter.

IBKR's official Web API documentation says retail clients use the Client Portal Gateway, and the gateway listens locally at `https://localhost:5000/v1/api` by default. Authentication must be completed manually in a browser; the repository never stores an IBKR password or 2FA code.

## Phone-only workflow

1. Run the project in a cloud development environment such as GitHub Codespaces.
2. Start the IBKR Client Portal Gateway in that environment.
3. Forward the gateway port to your phone through the Codespace port-forwarding feature.
4. Open the forwarded gateway URL in Safari and complete IBKR Paper login manually.
5. Run:

```bash
python -m ai_trading_agent.ibkr_client_portal
```

The adapter accepts the session only when IBKR reports `LOGIN_TYPE=2`, which identifies the Paper session. A Live session is rejected.

## Safety

This adapter is Paper-only. It does not store credentials and does not place Live orders.
