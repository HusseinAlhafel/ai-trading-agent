from __future__ import annotations

from dataclasses import dataclass

from .broker import PaperBroker
from .models import Candle, Order, Side
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
    """Paper-trading execution loop with drawdown and overtrading protection."""

    def __init__(
        self,
        broker: PaperBroker,
        strategy: ExplainableStrategy,
        risk: RiskManager,
        drawdown_halt: float = 0.15,
        drawdown_recovery: float = 0.05,
        trade_cooldown_bars: int = 3,
    ) -> None:
        if not 0 < drawdown_recovery < drawdown_halt < 1:
            raise ValueError("drawdown_recovery must be below drawdown_halt and both must be in (0, 1)")
        if trade_cooldown_bars < 0:
            raise ValueError("trade_cooldown_bars must be non-negative")
        self.broker = broker
        self.strategy = strategy
        self.risk = risk
        self.history: list[Candle] = []
        self.drawdown_halt = drawdown_halt
        self.drawdown_recovery = drawdown_recovery
        self.trade_cooldown_bars = trade_cooldown_bars
        self._peak_equity: float | None = None
        self._drawdown_halted = False
        self._last_trade_index: int | None = None

    def run(self, candles: list[Candle]) -> RunReport:
        if not candles:
            raise ValueError("candles cannot be empty")
        starting = self.broker.portfolio.cash
        for candle in candles:
            self.history.append(candle)
            index = len(self.history) - 1
            equity = self.broker.portfolio.mark_to_market(candle.close)
            self._peak_equity = equity if self._peak_equity is None else max(self._peak_equity, equity)
            drawdown = 0.0 if self._peak_equity <= 0 else (self._peak_equity - equity) / self._peak_equity

            if drawdown >= self.drawdown_halt:
                self._drawdown_halted = True
                if self.broker.portfolio.position > 1e-12:
                    qty = self.broker.portfolio.position
                    self.broker.submit(Order(Side.SELL, qty, candle.close, candle.timestamp))
                    self._last_trade_index = index
                continue
            if self._drawdown_halted:
                if drawdown > self.drawdown_recovery:
                    continue
                self._drawdown_halted = False

            if self._last_trade_index is not None and index - self._last_trade_index <= self.trade_cooldown_bars:
                continue

            signal = self.strategy.decide(self.history)
            if signal.side is None:
                continue
            closes = [c.close for c in self.history]
            qty = self.risk.quantity(signal.side, self.broker.portfolio, candle.close, closes=closes)
            if qty <= 1e-12:
                continue
            self.broker.submit(Order(signal.side, qty, candle.close, candle.timestamp))
            self._last_trade_index = index
        ending = self.broker.portfolio.mark_to_market(candles[-1].close)
        return RunReport(
            starting,
            ending,
            self.broker.portfolio.position,
            len(self.broker.portfolio.fills),
            self.broker.portfolio.fees_paid,
            self.broker.portfolio.realized_pnl,
        )
