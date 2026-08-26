from __future__ import annotations

from dataclasses import dataclass

from .models import Candle, Side
from .strategy import ExplainableStrategy


@dataclass(frozen=True)
class ManualSignal:
    symbol: str
    side: str
    confidence: float
    reference_price: float
    suggested_position_fraction: float
    stop_loss_fraction: float
    take_profit_fraction: float
    timestamp: str
    reason: str
    execution: str = "MANUAL_ONLY"


class ManualSignalAdvisor:
    """Creates actionable signals for manual execution in Plus500.

    This class deliberately has no broker client, credentials, browser automation,
    or order-submission method. It only converts the local strategy decision into
    a human-readable signal.
    """

    def __init__(
        self,
        strategy: ExplainableStrategy | None = None,
        position_fraction: float = 0.20,
        stop_loss_fraction: float = 0.01,
        take_profit_fraction: float = 0.02,
    ) -> None:
        if not 0 < position_fraction <= 1:
            raise ValueError("position_fraction must be in (0, 1]")
        if not 0 < stop_loss_fraction < 1:
            raise ValueError("stop_loss_fraction must be in (0, 1)")
        if not 0 < take_profit_fraction < 1:
            raise ValueError("take_profit_fraction must be in (0, 1)")
        self.strategy = strategy or ExplainableStrategy()
        self.position_fraction = position_fraction
        self.stop_loss_fraction = stop_loss_fraction
        self.take_profit_fraction = take_profit_fraction

    def advise(self, symbol: str, candles: list[Candle]) -> ManualSignal:
        if not candles:
            raise ValueError("candles cannot be empty")
        latest = candles[-1]
        signal = self.strategy.decide(candles)
        side = signal.side.value if signal.side is not None else "WAIT"
        confidence = min(1.0, abs(signal.score))
        return ManualSignal(
            symbol=symbol,
            side=side,
            confidence=confidence,
            reference_price=latest.close,
            suggested_position_fraction=self.position_fraction if signal.side else 0.0,
            stop_loss_fraction=self.stop_loss_fraction if signal.side else 0.0,
            take_profit_fraction=self.take_profit_fraction if signal.side else 0.0,
            timestamp=latest.timestamp,
            reason=signal.reason,
        )

    @staticmethod
    def exit_price(signal: ManualSignal) -> tuple[float, float] | None:
        if signal.side == "BUY":
            return (
                signal.reference_price * (1 - signal.stop_loss_fraction),
                signal.reference_price * (1 + signal.take_profit_fraction),
            )
        if signal.side == "SELL":
            return (
                signal.reference_price * (1 + signal.stop_loss_fraction),
                signal.reference_price * (1 - signal.take_profit_fraction),
            )
        return None
