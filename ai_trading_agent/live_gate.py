"""Fail-closed gate for any future live deployment.

This module does not place orders. It only validates that a live deployment
has explicitly opted in and that mandatory safety limits are present.
"""
from __future__ import annotations

from dataclasses import dataclass
import os


class LiveGateError(RuntimeError):
    pass


@dataclass(frozen=True)
class LiveSafetyConfig:
    enabled: bool = False
    max_order_value: float = 100.0
    max_daily_loss: float = 25.0
    max_open_positions: int = 1
    kill_switch: bool = False

    def validate(self) -> None:
        if self.max_order_value <= 0:
            raise LiveGateError("max_order_value must be positive")
        if self.max_daily_loss <= 0:
            raise LiveGateError("max_daily_loss must be positive")
        if self.max_open_positions < 1:
            raise LiveGateError("max_open_positions must be at least 1")
        if self.kill_switch:
            raise LiveGateError("kill switch is active")


def live_enabled_from_environment() -> bool:
    """Require two independent explicit opt-ins; default is always False."""
    return (
        os.getenv("TRADING_MODE", "PAPER").upper() == "LIVE"
        and os.getenv("ENABLE_LIVE_TRADING", "NO").upper() == "YES"
    )


def authorize_live(config: LiveSafetyConfig) -> None:
    """Authorize the live mode gate; this never submits an order."""
    config.validate()
    if not live_enabled_from_environment():
        raise LiveGateError("Live trading is not explicitly enabled")
