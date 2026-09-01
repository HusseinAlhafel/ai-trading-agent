"""IBKR Client Portal Gateway adapter locked to Paper Trading.

This adapter supports Paper-session verification without storing credentials.
IBKR requires the user to authenticate the Client Portal Gateway in a browser.
"""

from __future__ import annotations

import argparse
import json
import ssl
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class IBKRPaperOnlyError(RuntimeError):
    """Raised when the gateway is not authenticated as an IBKR Paper session."""


@dataclass(frozen=True)
class ClientPortalConfig:
    base_url: str = "https://127.0.0.1:5000/v1/api"
    timeout_seconds: float = 15.0

    def validate(self) -> None:
        if not self.base_url.startswith("https://"):
            raise ValueError("Client Portal Gateway must use HTTPS")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


class IBKRClientPortalPaper:
    """Client Portal Gateway session checker with a hard Paper-only gate."""

    def __init__(self, config: ClientPortalConfig | None = None) -> None:
        self.config = config or ClientPortalConfig()
        self.config.validate()
        self._ssl = ssl._create_unverified_context()

    def _request(self, method: str, path: str) -> dict | list:
        request = Request(
            self.config.base_url.rstrip("/") + path,
            method=method,
            headers={"Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.config.timeout_seconds, context=self._ssl) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"IBKR gateway HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(
                "Cannot reach the IBKR Client Portal Gateway. Start it and authenticate it in a browser."
            ) from exc
        return json.loads(raw) if raw else {}

    def validate_paper_session(self) -> dict:
        """Return session information only when IBKR reports loginType=2 (Paper)."""
        data = self._request("GET", "/sso/validate")
        if not isinstance(data, dict):
            raise IBKRPaperOnlyError("Unexpected IBKR session response")
        value = data.get("success", {}).get("value", data)
        if value.get("RESULT") is not True:
            raise IBKRPaperOnlyError("IBKR Client Portal session is not authenticated")
        if int(value.get("LOGIN_TYPE", 0)) != 2:
            raise IBKRPaperOnlyError("Refusing non-Paper IBKR session")
        return {
            "authenticated": True,
            "mode": "PAPER_ONLY",
            "paper_username": value.get("PAPER_USER_NAME"),
            "expires_ms": value.get("EXPIRES"),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check IBKR Client Portal Gateway Paper session")
    parser.add_argument("--base-url", default="https://127.0.0.1:5000/v1/api")
    args = parser.parse_args()
    result = IBKRClientPortalPaper(ClientPortalConfig(args.base_url)).validate_paper_session()
    print(json.dumps(result, indent=2))
    print("PAPER ONLY")


if __name__ == "__main__":
    main()
