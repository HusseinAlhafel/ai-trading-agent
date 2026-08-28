"""IBKR Paper Trading adapter.

This module is intentionally PAPER-ONLY. It connects only to the IBKR paper
TWS/IB Gateway port (7497 by default) and refuses any other port or a live mode.
It never stores credentials in the repository.
"""

from __future__ import annotations

from dataclasses import dataclass


class IBKRPaperOnlyError(RuntimeError):
    """Raised when an unsafe/non-paper configuration is requested."""


@dataclass(frozen=True)
class IBKRPaperConfig:
    host: str = "127.0.0.1"
    port: int = 7497
    client_id: int = 7

    def validate(self) -> None:
        if self.port != 7497:
            raise IBKRPaperOnlyError(
                "This project is locked to IBKR Paper TWS/Gateway port 7497."
            )
        if not self.host:
            raise ValueError("host must not be empty")
        if self.client_id < 0:
            raise ValueError("client_id must be non-negative")


class IBKRPaperAdapter:
    """Thin, opt-in adapter for an IBKR Paper TWS/Gateway session.

    No connection is attempted during construction. A local TWS or IB Gateway
    configured for the Paper account must be running before connect() is called.
    """

    def __init__(self, config: IBKRPaperConfig | None = None) -> None:
        self.config = config or IBKRPaperConfig()
        self.config.validate()
        self._ib = None

    def connect(self) -> None:
        self.config.validate()
        try:
            from ibapi.client import EClient  # type: ignore  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "IBKR API package is not installed. Install the official IBKR API "
                "components before connecting."
            ) from exc
        raise RuntimeError(
            "IBKR paper connection is deliberately not started automatically. "
            "Run TWS/IB Gateway in PAPER mode first, then use the explicit paper "
            "connection command."
        )

    @staticmethod
    def paper_endpoint() -> str:
        return "127.0.0.1:7497 (IBKR Paper TWS/Gateway)"
