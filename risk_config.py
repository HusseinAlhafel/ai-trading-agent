from dataclasses import dataclass


@dataclass(frozen=True)
class RiskConfig:
    max_position_value: float = 1000.0
    max_daily_loss: float = 100.0
    max_open_positions: int = 3

    def validate_order_value(self, value: float) -> None:
        if value <= 0:
            raise ValueError("order value must be positive")
        if value > self.max_position_value:
            raise ValueError("order exceeds maximum position value")
