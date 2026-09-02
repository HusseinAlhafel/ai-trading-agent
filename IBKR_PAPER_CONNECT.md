# IBKR Paper connection

The repository is locked to IBKR Paper for this integration.

## What is prepared

- Client Portal Gateway runs locally on port 5000.
- The Codespace configuration provides an internal desktop/browser on port 6080.
- `scripts/ibkr_paper_status.py` verifies the authenticated brokerage session.
- The verification requires `connected=true`, `authenticated=true`, `established=true`, and `LOGIN_TYPE=2` (Paper).
- `real_orders_enabled` is hard-coded to `false` in the verification output.

## User action required

Interactive Brokers does not support automated Client Portal Gateway authentication. The account owner must manually sign in through the browser running on the same machine as the Gateway. Never place an IBKR password or 2FA code in this repository or in chat.

After the internal browser is available, sign in to the **Paper Trading** environment. Then run:

```bash
python scripts/ibkr_paper_status.py
```

A successful result ends with:

```text
IBKR_PAPER_STATUS=READY
```

The project must remain Paper-only until explicitly reviewed and tested. No Live endpoint or Live credentials should be added.
