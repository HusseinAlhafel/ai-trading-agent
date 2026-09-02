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
    """Paper-trading execution loop with a conservative drawdown circuit breaker."""

    def __init__(
        self,
        broker: PaperBroker,
        strategy: ExplainableStrategy,
        risk: RiskManager,
        drawdown_halt: float = 0.15,
        drawdown_recovery: float = 0.05,
    ) -> None:
        if not 0 < drawdown_recovery < drawdown_halt < 1:
            raise ValueError("drawdown_recovery must be below drawdown_halt and both must be in (0, 1)")
        self.broker = broker
        self.strategy = strategy
        self.risk = risk
        self.history: list[Candle] = []
        self.drawdown_halt = drawdown_halt
        self.drawdown_recovery = drawdown_recovery
        self._peak_equity: float | None = None
        self._drawdown_halted = False

    def run(self, candles: list[Candle]) -> RunReport:
        if not candles:
            raise ValueError("candles cannot be empty")
        starting = self.broker.portfolio.cash
        for candle in candles:
            self.history.append(candle)
            equity = self.broker.portfolio.mark_to_market(candle.close)
            self._peak_equity = equity if self._peak_equity is None else max(self._peak_equity, equity)
            drawdown = 0.0 if self._peak_equity <= 0 else (self._peak_equity - equity) / self._peak_equity

            # Hard protection: flatten the paper position during a deep drawdown
            # and block new BUY orders until the portfolio has materially recovered.
            if drawdown >= self.drawdown_halt:
                self._drawdown_halted = True
                if self.broker.portfolio.position > 1e-12:
                    qty = self.broker.portfolio.position
                    self.broker.submit(Order(Side.SELL, qty, candle.close, candle.timestamp))
                continue
            if self._drawdown_halted:
                if drawdown > self.drawdown_recovery:
                    continue
                self._drawdown_halted = False

            signal = self.strategy.decide(self.history)
            if signal.side is None:
                continue
            # While halted we never reach this point; normal signals use the
            # conservative 10% target sizing from RiskManager.
            qty = self.risk.quantity(signal.side, self.broker.portfolio, candle.close)
            if qty <= 1e-12:
                continue
            self.broker.submit(Order(signal.side, qty, candle.close, candle.timestamp))
        ending = self.broker.portfolio.mark_to_market(candles[-1].close)
        return RunReport(
            starting,
            ending,
            self.broker.portfolio.position,
            len(self.broker.portfolio.fills),
            self.broker.portfolio.fees_paid,
            self.broker.portfolio.realized_pnl,
        )
