"""IBKR Client Portal Gateway connectivity check, PAPER ONLY.

Retail Web API access uses IBKR's Client Portal Gateway on HTTPS port 5000.
Authentication remains manual in the browser; this module never stores
credentials or 2FA codes and never enables a live endpoint.
"""

from __future__ import annotations

import argparse
import requests
from dataclasses import dataclass


class IBKRPaperOnlyError(RuntimeError):
    """Raised when an unsafe/non-paper configuration is requested."""


@dataclass(frozen=True)
class IBKRPaperConfig:
    base_url: str = "https://127.0.0.1:5000/v1/api"
    timeout_seconds: float = 10.0
    verify_ssl: bool = False

    def validate(self) -> None:
        if not self.base_url.startswith("https://127.0.0.1:5000/v1/api"):
            raise IBKRPaperOnlyError(
                "This project is locked to the local IBKR Client Portal Gateway on port 5000."
            )
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


class IBKRPaperAdapter:
    """Connect to an already-running IBKR Paper Client Portal Gateway."""

    def __init__(self, config: IBKRPaperConfig | None = None) -> None:
        self.config = config or IBKRPaperConfig()
        self.config.validate()
        self.session = requests.Session()
        self.session.verify = self.config.verify_ssl
        self.session.headers.update({
            "Accept": "*/*",
            "User-Agent": "ai-trading-agent-paper/0.4.2",
        })

    def auth_status(self) -> dict[str, object]:
        """Return the current IBKR brokerage-session authentication status."""
        self.config.validate()
        response = self.session.post(
            f"{self.config.base_url}/iserver/auth/status",
            timeout=self.config.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def accounts(self) -> dict[str, object]:
        """Return accounts available to the authenticated paper session."""
        self.config.validate()
        response = self.session.get(
            f"{self.config.base_url}/iserver/accounts",
            timeout=self.config.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def connect_and_check(self) -> dict[str, object]:
        """Check Gateway reachability, authentication, and paper account access."""
        status = self.auth_status()
        value = status.get("success", {}).get("value", {}) if isinstance(status, dict) else {}
        authenticated = bool(value.get("authenticated"))
        connected = bool(value.get("connected"))
        established = bool(value.get("established"))
        result: dict[str, object] = {
            "connected": connected,
            "authenticated": authenticated,
            "established": established,
            "mode": "PAPER_ONLY",
            "endpoint": "127.0.0.1:5000",
        }
        if authenticated and established:
            result["accounts"] = self.accounts()
        else:
            result["accounts"] = []
            result["message"] = "Log in manually through the forwarded IBKR Client Portal Gateway page."
        return result

    @staticmethod
    def paper_endpoint() -> str:
        return "https://127.0.0.1:5000/v1/api (IBKR Client Portal Gateway, PAPER)"


def main() -> None:
    parser = argparse.ArgumentParser(description="Check IBKR Client Portal Paper Gateway connectivity")
    parser.add_argument("--base-url", default="https://127.0.0.1:5000/v1/api")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    result = IBKRPaperAdapter(IBKRPaperConfig(args.base_url, args.timeout)).connect_and_check()
    print(result)
    print("REAL ORDERS DISABLED")


if __name__ == "__main__":
    main()
