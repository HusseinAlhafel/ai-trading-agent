from __future__ import annotations

from dataclasses import dataclass

from .models import Fill, Order, Portfolio, Side


@dataclass(frozen=True)
class BrokerConfig:
    fee_rate: float = 0.001


class PaperBroker:
    """In-memory broker. It deliberately has no network or live-order interface."""

    def __init__(self, starting_cash: float, config: BrokerConfig | None = None) -> None:
        if starting_cash <= 0:
            raise ValueError("starting_cash must be positive")
        self.config = config or BrokerConfig()
        if not 0 <= self.config.fee_rate < 1:
            raise ValueError("fee_rate must be in [0, 1)")
        self.portfolio = Portfolio(cash=starting_cash, equity=starting_cash)

    def submit(self, order: Order) -> Fill:
        if order.quantity <= 0 or order.price <= 0:
            raise ValueError("quantity and price must be positive")
        gross = order.quantity * order.price
        fee = gross * self.config.fee_rate

        if order.side is Side.BUY:
            total = gross + fee
            if total > self.portfolio.cash + 1e-12:
                raise ValueError("insufficient paper cash")
            self.portfolio.cash -= total
            old_position = self.portfolio.position
            new_position = old_position + order.quantity
            if new_position > 0:
                self.portfolio.average_entry_price = (
                    old_position * self.portfolio.average_entry_price + total
                ) / new_position
            self.portfolio.position = new_position
        else:
            if order.quantity > self.portfolio.position + 1e-12:
                raise ValueError("insufficient paper position")
            self.portfolio.cash += gross - fee
            entry = self.portfolio.average_entry_price
            self.portfolio.position -= order.quantity
            self.portfolio.realized_pnl += (order.price - entry) * order.quantity - fee
            if self.portfolio.position <= 1e-12:
                self.portfolio.position = 0.0
                self.portfolio.average_entry_price = 0.0

        self.portfolio.fees_paid += fee
        fill = Fill(order.side, order.quantity, order.price, fee, order.timestamp)
        self.portfolio.fills.append(fill)
        self.portfolio.mark_to_market(order.price)
        return fill
