from __future__ import annotations

from dataclasses import dataclass

from .indicators import momentum, sma, volatility
from .models import Candle, Side


@dataclass(frozen=True)
class Signal:
    side: Side | None
    score: float
    reason: str


class ExplainableStrategy:
    """A deterministic AI-style scorer using trend, momentum and volatility."""

    def __init__(self, fast_period: int = 5, slow_period: int = 12, momentum_period: int = 4) -> None:
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.momentum_period = momentum_period

    def decide(self, candles: list[Candle]) -> Signal:
        closes = [c.close for c in candles]
        fast = sma(closes, self.fast_period)
        slow = sma(closes, self.slow_period)
        mom = momentum(closes, self.momentum_period)
        vol = volatility(closes, min(10, len(closes))) if len(closes) >= 2 else None
        if fast is None or slow is None or mom is None:
            return Signal(None, 0.0, "warming up")

        score = 0.0
        reasons: list[str] = []
        if fast > slow:
            score += 0.5
            reasons.append("fast SMA above slow SMA")
        elif fast < slow:
            score -= 0.5
            reasons.append("fast SMA below slow SMA")
        if mom > 0.01:
            score += 0.4
            reasons.append("positive momentum")
        elif mom < -0.01:
            score -= 0.4
            reasons.append("negative momentum")
        if vol is not None and vol > 0.08:
            score *= 0.5
            reasons.append("high volatility reduced confidence")

        if score >= 0.6:
            return Signal(Side.BUY, score, "; ".join(reasons))
        if score <= -0.6:
            return Signal(Side.SELL, score, "; ".join(reasons))
        return Signal(None, score, "; ".join(reasons) or "no edge")
