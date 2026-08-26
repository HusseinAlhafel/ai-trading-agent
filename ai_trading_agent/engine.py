from __future__ import annotations

from dataclasses import dataclass

from .broker import PaperBroker
from .models import Candle, Order
from .risk import RiskManager
from .strategy import ExplainableStrategy


@dataclass(frozen=True)
class RunReport:
    starting_cash: float
    ending_equity: float
    position: float
    fills: int
    fees: float
    realized_pnl: float


class TradingEngine:
    def __init__(self, broker: PaperBroker, strategy: ExplainableStrategy, risk: RiskManager) -> None:
        self.broker = broker
        self.strategy = strategy
        self.risk = risk
        self.history: list[Candle] = []

    def run(self, candles: list[Candle]) -> RunReport:
        if not candles:
            raise ValueError("candles cannot be empty")
        starting = self.broker.portfolio.cash
        for candle in candles:
            self.history.append(candle)
            signal = self.strategy.decide(self.history)
            if signal.side is None:
                self.broker.portfolio.mark_to_market(candle.close)
                continue
            qty = self.risk.quantity(signal.side, self.broker.portfolio, candle.close)
            if qty <= 1e-12:
                continue
            self.broker.submit(Order(signal.side, qty, candle.close, candle.timestamp))
        ending = self.broker.portfolio.mark_to_market(candles[-1].close)
        return RunReport(starting, ending, self.broker.portfolio.position, len(self.broker.portfolio.fills), self.broker.portfolio.fees_paid, self.broker.portfolio.realized_pnl)
