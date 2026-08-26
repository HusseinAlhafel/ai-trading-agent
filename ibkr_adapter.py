"""IBKR execution adapter with a hard live-trading safety gate.

The adapter is intentionally disabled by default. Set IBKR_LIVE_TRADING=true only
when a real IBKR account, API session, permissions, and risk controls have been
independently verified. Paper mode never submits live orders.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


class LiveTradingDisabled(RuntimeError):
    """Raised when live execution is attempted without explicit enablement."""


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
    """Execution boundary for IBKR.

    This first implementation deliberately exposes no automatic live submission.
    It validates intents and produces a broker-neutral order request. Live transport
    must be enabled only after account/API setup and an explicit deployment review.
    """

    def __init__(self, *, live: bool = False) -> None:
        env_live = os.getenv("IBKR_LIVE_TRADING", "false").lower() == "true"
        self.live = bool(live and env_live)

    def validate(self, intent: OrderIntent) -> None:
        if intent.side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if intent.quantity <= 0:
            raise ValueError("quantity must be positive")
        if intent.order_type not in {"MKT", "LMT", "STP", "STP_LMT"}:
            raise ValueError("unsupported order type")

    def submit(self, intent: OrderIntent) -> dict:
        self.validate(intent)
        if not self.live:
            return {
                "status": "PAPER_ONLY",
                "symbol": intent.symbol,
                "side": intent.side,
                "quantity": intent.quantity,
                "order_type": intent.order_type,
                "stop_loss": intent.stop_loss,
                "take_profit": intent.take_profit,
            }
        raise LiveTradingDisabled(
            "Live IBKR execution is not enabled in this build. Complete account, "
            "API session, permissions, risk review, and deployment checks first."
        )
