from __future__ import annotations

"""Plus500 T4 integration boundary.

This module is intentionally non-executing. Plus500 documents open .NET and FIX APIs
for its T4 futures/options platform, but the exact credentials, endpoint, account
entitlements, and protocol details are account/provider supplied. Until those are
explicitly configured, this adapter can only validate configuration and translate
orders; it cannot submit a live order.
"""

from dataclasses import dataclass
import os

from .models import Order, Side


class Plus500T4NotConfigured(RuntimeError):
    """Raised when T4 integration has not been explicitly configured."""


@dataclass(frozen=True)
class Plus500T4Config:
    enabled: bool = False
    live_trading: bool = False
    host: str = ""
    port: int = 0
    account: str = ""

    @classmethod
    def from_env(cls) -> "Plus500T4Config":
        return cls(
            enabled=os.getenv("PLUS500_T4_ENABLED", "false").lower() == "true",
            live_trading=os.getenv("PLUS500_T4_LIVE_TRADING", "false").lower() == "true",
            host=os.getenv("PLUS500_T4_HOST", ""),
            port=int(os.getenv("PLUS500_T4_PORT", "0")),
            account=os.getenv("PLUS500_T4_ACCOUNT", ""),
        )


class Plus500T4Adapter:
    """Safe integration boundary; live order submission is deliberately disabled."""

    def __init__(self, config: Plus500T4Config | None = None) -> None:
        self.config = config or Plus500T4Config.from_env()

    def status(self) -> dict[str, object]:
        return {
            "provider": "Plus500 T4",
            "enabled": self.config.enabled,
            "live_trading": self.config.live_trading,
            "configured": bool(self.config.host and self.config.port and self.config.account),
            "order_submission": False,
        }

    def submit(self, order: Order) -> None:
        """Reject all live submissions until a reviewed T4 implementation is installed."""
        if order.quantity <= 0 or order.price <= 0:
            raise ValueError("quantity and price must be positive")
        raise Plus500T4NotConfigured(
            "Plus500 T4 order submission is disabled. Configure and review the official "
            "T4 .NET/FIX integration before enabling any execution path."
        )

    @staticmethod
    def describe_order(order: Order) -> dict[str, object]:
        return {
            "side": order.side.value,
            "quantity": order.quantity,
            "price": order.price,
            "timestamp": order.timestamp.isoformat(),
        }
