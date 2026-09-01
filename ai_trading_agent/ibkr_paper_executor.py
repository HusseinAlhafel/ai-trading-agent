"""IBKR Paper execution adapter.

This module is locked to IBKR Paper TWS/IB Gateway port 7497. It can connect to
an already-running paper session and submit PAPER orders through ibapi. No live
endpoint is accepted and no credentials are stored here.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any


class IBKRPaperOnlyError(RuntimeError):
    """Raised when a non-paper endpoint/configuration is requested."""


@dataclass(frozen=True)
class IBKRPaperExecutionConfig:
    host: str = "127.0.0.1"
    port: int = 7497
    client_id: int = 7
    timeout_seconds: float = 10.0

    def validate(self) -> None:
        if self.port != 7497:
            raise IBKRPaperOnlyError(
                "This project is locked to IBKR Paper TWS/Gateway port 7497."
            )
        if not self.host:
            raise ValueError("host must not be empty")
        if self.client_id < 0:
            raise ValueError("client_id must be non-negative")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


class IBKRPaperExecution:
    """Connect and submit orders only to an IBKR paper TWS/Gateway session."""

    def __init__(self, config: IBKRPaperExecutionConfig | None = None) -> None:
        self.config = config or IBKRPaperExecutionConfig()
        self.config.validate()
        self._app: Any | None = None
        self._thread: threading.Thread | None = None
        self._connected = threading.Event()
        self._next_order_id: int | None = None
        self._errors: list[tuple[Any, int, str]] = []

    def connect(self) -> dict[str, object]:
        self.config.validate()
        try:
            from ibapi.client import EClient  # type: ignore
            from ibapi.wrapper import EWrapper  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Install the IBKR extra: pip install -e '.[ibkr]'") from exc

        outer = self

        class App(EWrapper, EClient):
            def __init__(self) -> None:
                EClient.__init__(self, self)
                self.accounts: list[str] = []

            def nextValidId(self, orderId: int) -> None:  # noqa: N802
                outer._next_order_id = orderId
                outer._connected.set()

            def managedAccounts(self, accountsList: str) -> None:  # noqa: N802
                self.accounts = [x for x in accountsList.split(",") if x]

            def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):  # noqa: N802
                outer._errors.append((reqId, errorCode, errorString))

        app = App()
        app.connect(self.config.host, self.config.port, clientId=self.config.client_id)
        self._app = app
        self._thread = threading.Thread(target=app.run, daemon=True)
        self._thread.start()

        if not self._connected.wait(self.config.timeout_seconds):
            app.disconnect()
            raise TimeoutError(
                f"IBKR Paper TWS/Gateway did not respond within {self.config.timeout_seconds}s"
            )

        time.sleep(0.2)
        return {
            "connected": True,
            "mode": "PAPER_ONLY",
            "endpoint": f"{self.config.host}:{self.config.port}",
            "next_order_id": self._next_order_id,
            "errors": list(self._errors),
        }

    def disconnect(self) -> None:
        if self._app is not None:
            self._app.disconnect()
        self._app = None
        self._thread = None
        self._connected.clear()

    def place_market_order(self, contract: Any, side: str, quantity: float) -> int:
        """Submit a market order to the connected IBKR PAPER session."""
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if self._app is None or not self._connected.is_set() or self._next_order_id is None:
            raise RuntimeError("IBKR Paper session is not connected")

        try:
            from ibapi.order import Order  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Install the IBKR extra: pip install -e '.[ibkr]'") from exc

        order = Order()
        order.action = side
        order.totalQuantity = quantity
        order.orderType = "MKT"
        order.tif = "DAY"
        order.transmit = True

        order_id = self._next_order_id
        self._app.placeOrder(order_id, contract, order)
        self._next_order_id += 1
        return order_id
