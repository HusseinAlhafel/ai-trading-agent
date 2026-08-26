"""IBKR execution boundary for the paper-trading build.

This build is intentionally PAPER-ONLY. It does not contain a live-order
transport and cannot be enabled through an environment variable. Any attempt
to construct the adapter with ``live=True`` is rejected immediately.
"""

from __future__ import annotations

from dataclasses import dataclass


class LiveTradingDisabled(RuntimeError):
    """Raised whenever live execution is requested in this build."""


@dataclass(frozen=True)
class OrderIntent:
    symbol: str
    side: str
    quantity: float
    order_type: str = "MKT"
    limit_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None


class IBKRAdapter:
    """Broker boundary that is deliberately locked to paper trading."""

    def __init__(self, *, live: bool = False) -> None:
        if live:
            raise LiveTradingDisabled(
                "Live IBKR trading is disabled in this build. "
                "Use the paper-trading broker only."
            )
        self.live = False

    def validate(self, intent: OrderIntent) -> None:
        if intent.side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if intent.quantity <= 0:
            raise ValueError("quantity must be positive")
        if intent.order_type not in {"MKT", "LMT", "STP", "STP_LMT"}:
            raise ValueError("unsupported order type")

    def submit(self, intent: OrderIntent) -> dict:
        self.validate(intent)
        return {
            "status": "PAPER_ONLY",
            "symbol": intent.symbol,
            "side": intent.side,
            "quantity": intent.quantity,
            "order_type": intent.order_type,
            "stop_loss": intent.stop_loss,
            "take_profit": intent.take_profit,
        }
