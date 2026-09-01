# IBKR Client Portal — Paper Trading

The repository includes a Paper-only Client Portal Gateway adapter and a phone-friendly Codespace setup.

IBKR's official Web API uses the Client Portal Gateway for retail Web API authentication and the gateway listens locally at `https://localhost:5000/v1/api` by default. IBKR explicitly requires browser authentication and does not support automated Client Portal Gateway authentication.

## Phone-only workflow

The repository now includes `.devcontainer/` automation that installs the official Client Portal Gateway, installs the project's IBKR dependency, starts the gateway when the Codespace starts, and forwards port 5000.

After the Codespace rebuilds its container, no terminal command needs to be pasted. Open the forwarded port labeled **IBKR Paper Client Portal** and complete the IBKR Paper login in Safari. The project then verifies that IBKR reports `LOGIN_TYPE=2`; a Live session is rejected.

## Safety

This adapter is Paper-only. It never stores an IBKR password or 2FA code, and the gateway authentication step remains manual as required by IBKR.
