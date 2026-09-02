from __future__ import annotations

from dataclasses import dataclass

from .models import Portfolio, Side


@dataclass(frozen=True)
class RiskConfig:
    # Keep each directional allocation modest while the strategy is validated.
    position_fraction: float = 0.10
    max_position_fraction: float = 0.50


class RiskManager:
    def __init__(self, config: RiskConfig | None = None, fee_rate: float = 0.001) -> None:
        self.config = config or RiskConfig()
        if not 0 <= fee_rate < 1:
            raise ValueError("fee_rate must be in [0, 1)")
        self.fee_rate = fee_rate
        if not 0 < self.config.position_fraction <= self.config.max_position_fraction <= 1:
            raise ValueError("invalid risk fractions")

    def quantity(self, side: Side, portfolio: Portfolio, price: float) -> float:
        if price <= 0:
            return 0.0
        equity = portfolio.mark_to_market(price)
        max_units = equity * self.config.max_position_fraction / price
        target_units = equity * self.config.position_fraction / price
        if side is Side.BUY:
            affordable = portfolio.cash / (price * (1 + self.fee_rate))
            return max(0.0, min(target_units, affordable, max_units - portfolio.position))
        return max(0.0, min(portfolio.position, target_units))
