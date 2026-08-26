"""Offline paper-trading loop.

This module is intentionally network-free. It replays the repository's CSV candles
through the existing PaperBroker and can loop forever for soak testing. It does not
connect to IBKR, submit broker orders, or read credentials.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass

from .broker import BrokerConfig, PaperBroker
from .data import load_csv
from .engine import TradingEngine
from .risk import RiskConfig, RiskManager
from .strategy import ExplainableStrategy


@dataclass(frozen=True)
class ReplayConfig:
    starting_cash: float = 10_000.0
    fee_rate: float = 0.001
    position_size: float = 0.20
    max_position: float = 1.00
    interval_seconds: float = 0.0
    loop_forever: bool = False

    def validate(self) -> None:
        if self.starting_cash <= 0:
            raise ValueError("starting_cash must be positive")
        if self.interval_seconds < 0:
            raise ValueError("interval_seconds must be non-negative")


def run_replay(data_path: str, config: ReplayConfig) -> list[float]:
    """Replay candles once and return ending equity for each cycle."""
    config.validate()
    candles = load_csv(data_path)
    if not candles:
        raise ValueError("data file contains no candles")

    equities: list[float] = []
    while True:
        broker = PaperBroker(config.starting_cash, BrokerConfig(config.fee_rate))
        engine = TradingEngine(
            broker,
            ExplainableStrategy(),
            RiskManager(
                RiskConfig(config.position_size, config.max_position),
                fee_rate=config.fee_rate,
            ),
        )
        report = engine.run(candles)
        equities.append(report.ending_equity)
        print(
            f"PAPER CYCLE ending_equity={report.ending_equity:.2f} "
            f"fills={report.fills} realized_pnl={report.realized_pnl:.2f}",
            flush=True,
        )

        if not config.loop_forever:
            break
        if config.interval_seconds:
            time.sleep(config.interval_seconds)

    return equities


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline 24/7 paper-trading replay")
    parser.add_argument("--data", default="sample_prices.csv")
    parser.add_argument("--cash", type=float, default=10_000.0)
    parser.add_argument("--fee-rate", type=float, default=0.001)
    parser.add_argument("--position-size", type=float, default=0.20)
    parser.add_argument("--max-position", type=float, default=1.00)
    parser.add_argument("--interval", type=float, default=0.0)
    parser.add_argument("--loop", action="store_true", help="repeat the offline dataset forever")
    args = parser.parse_args()

    run_replay(
        args.data,
        ReplayConfig(
            starting_cash=args.cash,
            fee_rate=args.fee_rate,
            position_size=args.position_size,
            max_position=args.max_position,
            interval_seconds=args.interval,
            loop_forever=args.loop,
        ),
    )


if __name__ == "__main__":
    main()
