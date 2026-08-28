"""IBKR Paper Trading connectivity check.

This module is intentionally PAPER-ONLY. It connects only to the IBKR paper
TWS/IB Gateway port (7497 by default) and refuses any other port. Credentials
are never stored in the repository.
"""

from __future__ import annotations

import argparse
import threading
import time
from dataclasses import dataclass


class IBKRPaperOnlyError(RuntimeError):
    """Raised when an unsafe/non-paper configuration is requested."""


@dataclass(frozen=True)
class IBKRPaperConfig:
    host: str = "127.0.0.1"
    port: int = 7497
    client_id: int = 7
    timeout_seconds: float = 10.0

    def validate(self) -> None:
        if self.port != 7497:
            raise IBKRPaperOnlyError("This project is locked to IBKR Paper TWS/Gateway port 7497.")
        if not self.host:
            raise ValueError("host must not be empty")
        if self.client_id < 0:
            raise ValueError("client_id must be non-negative")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


class IBKRPaperAdapter:
    """Connect to an already-running IBKR Paper TWS/Gateway session."""

    def __init__(self, config: IBKRPaperConfig | None = None) -> None:
        self.config = config or IBKRPaperConfig()
        self.config.validate()

    def connect_and_check(self) -> dict[str, object]:
        """Connect to paper TWS/Gateway, wait for the handshake, then disconnect."""
        self.config.validate()
        try:
            from ibapi.client import EClient  # type: ignore
            from ibapi.wrapper import EWrapper  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Install the IBKR extra first: pip install -e '.[ibkr]'") from exc

        class App(EWrapper, EClient):
            def __init__(self) -> None:
                EClient.__init__(self, self)
                self.next_order_id = None
                self.accounts: list[str] = []
                self.errors: list[tuple] = []
                self.connected_event = threading.Event()

            def nextValidId(self, orderId: int) -> None:  # noqa: N802
                self.next_order_id = orderId
                self.connected_event.set()

            def managedAccounts(self, accountsList: str) -> None:  # noqa: N802
                self.accounts = [x for x in accountsList.split(",") if x]

            def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):  # noqa: N802
                self.errors.append((reqId, errorCode, errorString))

        app = App()
        app.connect(self.config.host, self.config.port, clientId=self.config.client_id)
        thread = threading.Thread(target=app.run, daemon=True)
        thread.start()
        try:
            if not app.connected_event.wait(self.config.timeout_seconds):
                raise TimeoutError(f"IBKR Paper TWS/Gateway did not respond within {self.config.timeout_seconds}s")
            time.sleep(0.2)
            return {
                "connected": True,
                "mode": "PAPER_ONLY",
                "endpoint": f"{self.config.host}:{self.config.port}",
                "accounts": app.accounts,
                "next_order_id": app.next_order_id,
                "errors": app.errors,
            }
        finally:
            app.disconnect()

    @staticmethod
    def paper_endpoint() -> str:
        return "127.0.0.1:7497 (IBKR Paper TWS/Gateway)"


def main() -> None:
    parser = argparse.ArgumentParser(description="Check IBKR Paper TWS/Gateway connectivity")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7497)
    parser.add_argument("--client-id", type=int, default=7)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    result = IBKRPaperAdapter(IBKRPaperConfig(args.host, args.port, args.client_id, args.timeout)).connect_and_check()
    print(result)
    print("REAL ORDERS DISABLED")


if __name__ == "__main__":
    main()
