# IBKR Client Portal — Paper Trading

The repository includes a **Paper-only** Client Portal Gateway adapter and a phone-friendly Codespace setup.

IBKR's official Web API uses the Client Portal Gateway for retail Web API authentication. The gateway listens locally on HTTPS port `5000` by default. IBKR requires browser authentication and does not support automated Client Portal Gateway authentication.

## Phone-only workflow

The repository's `.devcontainer/` configuration now:

1. Installs Java 17 for the gateway.
2. Downloads the official Client Portal Gateway directly from Interactive Brokers.
3. Installs the project's Python dependencies.
4. Starts the gateway when the Codespace starts.
5. Forwards port `5000` as **IBKR Paper Client Portal**.
6. Verifies `LOGIN_TYPE=2` after login; IBKR defines `1` as Live and `2` as Paper.

### First time after this update

Rebuild the Codespace container once so the new Java feature and startup configuration are applied. Then open the forwarded port labeled **IBKR Paper Client Portal** in Safari and complete the IBKR **Paper** login manually.

Do **not** paste your IBKR username, password, or 2FA code into this chat or into repository files.

### If port 5000 opens but the page is blank

Check the Codespace port is forwarded to the running container and wait a few seconds for the Java gateway to finish starting. The gateway log is stored at `~/ibkr-clientportal/gateway.log` inside the Codespace. The startup script also refuses to continue if the gateway process exits immediately.

### Connectivity check

After manual login, run the repository's `ibkr-paper-check` command. A successful result must report:

- `connected: True`
- `authenticated: True`
- `established: True`
- `paper_verified: True`
- `login_type: 2`
- `real_orders_enabled: False`

If the session is not authenticated, the checker reports that manual login is required instead of attempting credentials automatically.

## Safety

This adapter is **Paper-only**. It is locked to the local Client Portal Gateway on port `5000`, explicitly verifies the IBKR session as Paper, never stores an IBKR password or 2FA code, and never enables real order submission. IBKR also requires the browser login and API calls to occur on the same machine as the Client Portal Gateway.
