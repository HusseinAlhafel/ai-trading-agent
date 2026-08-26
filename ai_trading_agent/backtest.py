from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .broker import BrokerConfig, PaperBroker
from .engine import TradingEngine
from .models import Candle, Order
from .risk import RiskManager
from .strategy import ExplainableStrategy


@dataclass(frozen=True)
class BacktestMetrics:
    starting_cash: float
    ending_equity: float
    net_pnl: float
    return_pct: float
    fills: int
    fees: float
    realized_pnl: float
    max_drawdown_pct: float


def load_candles(path: str | Path) -> list[Candle]:
    candles: list[Candle] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            candles.append(
                Candle(
                    timestamp=row["timestamp"],
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row.get("volume", 0) or 0),
                )
            )
    if not candles:
        raise ValueError("no candles found")
    return candles


def run_backtest(candles: list[Candle], starting_cash: float = 1000.0) -> BacktestMetrics:
    broker = PaperBroker(starting_cash, BrokerConfig(fee_rate=0.001))
    engine = TradingEngine(broker, ExplainableStrategy(), RiskManager())

    peak = starting_cash
    max_drawdown = 0.0
    for candle in candles:
        engine.history.append(candle)
        signal = engine.strategy.decide(engine.history)
        if signal.side is not None:
            qty = engine.risk.quantity(signal.side, broker.portfolio, candle.close)
            if qty > 1e-12:
                broker.submit(Order(signal.side, qty, candle.close, candle.timestamp))
        equity = broker.portfolio.mark_to_market(candle.close)
        peak = max(peak, equity)
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - equity) / peak * 100)

    ending = broker.portfolio.mark_to_market(candles[-1].close)
    net_pnl = ending - starting_cash
    return BacktestMetrics(
        starting_cash=starting_cash,
        ending_equity=ending,
        net_pnl=net_pnl,
        return_pct=net_pnl / starting_cash * 100,
        fills=len(broker.portfolio.fills),
        fees=broker.portfolio.fees_paid,
        realized_pnl=broker.portfolio.realized_pnl,
        max_drawdown_pct=max_drawdown,
    )


def format_metrics(metrics: BacktestMetrics) -> str:
    return (
        f"starting_cash={metrics.starting_cash:.2f}\n"
        f"ending_equity={metrics.ending_equity:.2f}\n"
        f"net_pnl={metrics.net_pnl:.2f}\n"
        f"return_pct={metrics.return_pct:.2f}\n"
        f"fills={metrics.fills}\n"
        f"fees={metrics.fees:.2f}\n"
        f"realized_pnl={metrics.realized_pnl:.2f}\n"
        f"max_drawdown_pct={metrics.max_drawdown_pct:.2f}"
    )
