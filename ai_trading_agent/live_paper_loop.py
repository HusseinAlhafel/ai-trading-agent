"""Public-market-data paper-trading loop.

Safety boundary:
- Public Yahoo Finance candles are used for analysis only.
- Orders are sent only to the in-memory PaperBroker.
- No IBKR/Plus500 login, credentials, browser automation, or live order API is used.

The loop polls for fresh candles and only processes a candle timestamp once, so a
poll does not replay the same candle and create duplicate simulated fills.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass

from .broker import BrokerConfig, PaperBroker
from .market_data import fetch_market_data, utc_now_label
from .models import Candle, Order
from .risk import RiskConfig, RiskManager
from .strategy import ExplainableStrategy


@dataclass(frozen=True)
class LivePaperConfig:
    symbol: str = "GC=F"
    interval: str = "5m"
    range_: str = "1d"
    starting_cash: float = 1_000.0
    fee_rate: float = 0.001
    position_size: float = 0.20
    max_position: float = 1.00
    poll_seconds: float = 60.0

    def validate(self) -> None:
        if not self.symbol:
            raise ValueError("symbol must not be empty")
        if self.starting_cash <= 0:
            raise ValueError("starting_cash must be positive")
        if self.fee_rate < 0:
            raise ValueError("fee_rate must be non-negative")
        if self.poll_seconds <= 0:
            raise ValueError("poll_seconds must be positive")


class LivePaperSession:
    def __init__(self, config: LivePaperConfig) -> None:
        config.validate()
        self.config = config
        self.broker = PaperBroker(config.starting_cash, BrokerConfig(config.fee_rate))
        self.strategy = ExplainableStrategy()
        self.risk = RiskManager(
            RiskConfig(config.position_size, config.max_position),
            fee_rate=config.fee_rate,
        )
        self.history: list[Candle] = []
        self.last_timestamp: str | None = None

    def process_snapshot(self, candles: list[Candle]) -> dict[str, object] | None:
        """Process newest unseen candle without using that candle for its own signal."""
        if not candles:
            raise ValueError("candles cannot be empty")
        candle = candles[-1]
        if candle.timestamp == self.last_timestamp:
            return None

        # Build prior-bar history first. The newest candle is appended only after
        # the signal is calculated, preventing current-candle look-ahead.
        existing = {item.timestamp for item in self.history}
        new_items = [item for item in candles if item.timestamp not in existing]
        prior_history = (self.history + new_items[:-1])[-200:]
        signal = self.strategy.decide(prior_history)

        quantity = 0.0
        if signal.side is not None:
            quantity = self.risk.quantity(signal.side, self.broker.portfolio, candle.close)
            if quantity > 1e-12:
                self.broker.submit(Order(signal.side, quantity, candle.close, candle.timestamp))

        self.history = (prior_history + [candle])[-200:]
        self.last_timestamp = candle.timestamp

        equity = self.broker.portfolio.mark_to_market(candle.close)
        return {
            "timestamp": candle.timestamp,
            "price": candle.close,
            "signal": signal.side.value if signal.side is not None else "WAIT",
            "score": signal.score,
            "reason": signal.reason,
            "quantity": quantity,
            "equity": equity,
            "position": self.broker.portfolio.position,
            "fills": len(self.broker.portfolio.fills),
            "realized_pnl": self.broker.portfolio.realized_pnl,
        }


def run_forever(config: LivePaperConfig) -> None:
    session = LivePaperSession(config)
    print(
        f"LIVE PAPER START symbol={config.symbol} interval={config.interval} "
        f"cash={config.starting_cash:.2f} -- REAL ORDERS DISABLED",
        flush=True,
    )
    while True:
        try:
            snapshot = fetch_market_data(config.symbol, config.interval, config.range_)
            status = session.process_snapshot(snapshot.candles)
            if status is not None:
                print(
                    f"{utc_now_label()} PAPER {config.symbol} "
                    f"price={status['price']:.5f} signal={status['signal']} "
                    f"score={status['score']:.2f} equity={status['equity']:.2f} "
                    f"fills={status['fills']} reason={status['reason']}",
                    flush=True,
                )
        except Exception as exc:  # keep the monitoring loop alive on transient feed errors
            print(f"{utc_now_label()} DATA_ERROR {type(exc).__name__}: {exc}", flush=True)
        time.sleep(config.poll_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="24/7 public-data paper-trading loop")
    parser.add_argument("--symbol", default="GC=F")
    parser.add_argument("--interval", default="5m")
    parser.add_argument("--range", dest="range_", default="1d")
    parser.add_argument("--cash", type=float, default=1_000.0)
    parser.add_argument("--fee-rate", type=float, default=0.001)
    parser.add_argument("--position-size", type=float, default=0.20)
    parser.add_argument("--max-position", type=float, default=1.00)
    parser.add_argument("--poll-seconds", type=float, default=60.0)
    args = parser.parse_args()

    run_forever(
        LivePaperConfig(
            symbol=args.symbol,
            interval=args.interval,
            range_=args.range_,
            starting_cash=args.cash,
            fee_rate=args.fee_rate,
            position_size=args.position_size,
            max_position=args.max_position,
            poll_seconds=args.poll_seconds,
        )
    )


if __name__ == "__main__":
    main()
