from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Candle:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass(frozen=True)
class Order:
    side: Side
    quantity: float
    price: float
    timestamp: str


@dataclass(frozen=True)
class Fill:
    side: Side
    quantity: float
    price: float
    fee: float
    timestamp: str


@dataclass
class Portfolio:
    cash: float
    position: float = 0.0
    equity: float = 0.0
    fees_paid: float = 0.0
    realized_pnl: float = 0.0
    average_entry_price: float = 0.0
    fills: list[Fill] = field(default_factory=list)

    def mark_to_market(self, price: float) -> float:
        self.equity = self.cash + self.position * price
        return self.equity
