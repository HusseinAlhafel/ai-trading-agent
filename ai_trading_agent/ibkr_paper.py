"""IBKR Client Portal Gateway connectivity check, PAPER ONLY.

Retail Web API access uses IBKR's Client Portal Gateway on HTTPS port 5000.
Authentication remains manual in the browser; this module never stores
credentials or 2FA codes and never enables a live endpoint.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import requests


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
        self.session.headers.update(
            {
                "Accept": "*/*",
                "User-Agent": "ai-trading-agent-paper/0.4.4",
            }
        )

    def _request_json(self, method: str, endpoint: str, **kwargs: object) -> dict[str, object]:
        self.config.validate()
        response = self.session.request(
            method,
            f"{self.config.base_url}/{endpoint.lstrip('/')}",
            timeout=self.config.timeout_seconds,
            **kwargs,
        )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}

    def auth_status(self) -> dict[str, object]:
        """Return the current IBKR brokerage-session authentication status."""
        try:
            return self._request_json("POST", "iserver/auth/status")
        except requests.HTTPError as exc:
            if exc.response is None or exc.response.status_code != 405:
                raise
            return self._request_json("GET", "iserver/auth/status")

    def session_validation(self) -> dict[str, object]:
        """Validate the SSO session and expose IBKR's live/paper login type."""
        return self._request_json("GET", "sso/validate")

    def initialize_brokerage_session(self) -> dict[str, object]:
        """Ask IBKR to establish the brokerage session after browser login."""
        return self._request_json(
            "POST",
            "iserver/auth/ssodh/init",
            json={"publish": True, "compete": False},
        )

    def accounts(self) -> dict[str, object]:
        """Return accounts available to the authenticated paper session."""
        return self._request_json("GET", "iserver/accounts")

    @staticmethod
    def _success_value(payload: object) -> dict[str, object]:
        if not isinstance(payload, dict):
            return {}
        success = payload.get("success")
        if not isinstance(success, dict):
            return {}
        value = success.get("value")
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _is_authenticated(status: dict[str, object]) -> bool:
        value = IBKRPaperAdapter._success_value(status)
        return bool(value.get("authenticated") and value.get("established", True))

    def connect_and_check(self) -> dict[str, object]:
        """Validate PAPER login, initialize brokerage session, then verify status."""
        try:
            validation = self.session_validation()
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 401:
                return {
                    "connected": False,
                    "authenticated": False,
                    "established": False,
                    "paper_verified": False,
                    "mode": "PAPER_ONLY",
                    "endpoint": "127.0.0.1:5000",
                    "real_orders_enabled": False,
                    "message": (
                        "IBKR Gateway is running, but its authenticated browser session is not "
                        "visible to this API client. Re-authenticate through the Gateway on the "
                        "same machine/session as the Gateway, then run this check again."
                    ),
                }
            raise

        validation_value = self._success_value(validation)
        login_type = validation_value.get("LOGIN_TYPE", validation_value.get("loginType"))
        paper_verified = login_type == 2 and validation_value.get("RESULT") is not False
        if not paper_verified:
            raise IBKRPaperOnlyError(
                "IBKR session is not verified as PAPER. Refusing to continue."
            )

        # Important: initialize the brokerage session BEFORE auth/status.
        # A previous implementation queried auth/status first and could hang
        # there even though the browser SSO login was already valid.
        init = self.initialize_brokerage_session()
        init_value = self._success_value(init)
        authenticated = bool(init_value.get("authenticated"))
        connected = bool(init_value.get("connected"))
        established = bool(init_value.get("established"))

        # Some Gateway versions return only a generic success payload from init.
        # In that case, perform the status check after initialization.
        if not (authenticated and established):
            status = self.auth_status()
            status_value = self._success_value(status)
            authenticated = bool(status_value.get("authenticated"))
            connected = bool(status_value.get("connected"))
            established = bool(status_value.get("established"))

        result: dict[str, object] = {
            "connected": connected,
            "authenticated": authenticated,
            "established": established,
            "mode": "PAPER_ONLY",
            "endpoint": "127.0.0.1:5000",
            "real_orders_enabled": False,
            "paper_verified": True,
            "login_type": 2,
        }

        if not (authenticated and established):
            result["accounts"] = []
            result["message"] = (
                "The IBKR SSO login is verified as PAPER, but the brokerage session is not "
                "established yet. Keep the Gateway running and re-run the check."
            )
            return result

        result["accounts"] = self.accounts()
        return result

    @staticmethod
    def paper_endpoint() -> str:
        return "https://127.0.0.1:5000/v1/api (IBKR Client Portal Gateway, PAPER)"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check IBKR Client Portal Paper Gateway connectivity"
    )
    parser.add_argument("--base-url", default="https://127.0.0.1:5000/v1/api")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    result = IBKRPaperAdapter(IBKRPaperConfig(args.base_url, args.timeout)).connect_and_check()
    print(result)
    print("REAL ORDERS DISABLED")


if __name__ == "__main__":
    main()
