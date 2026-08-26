from __future__ import annotations

import argparse

from .broker import BrokerConfig, PaperBroker
from .data import load_csv
from .engine import TradingEngine
from .risk import RiskConfig, RiskManager
from .strategy import ExplainableStrategy


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-style paper trading simulator (offline only)")
    parser.add_argument("--data", default="sample_prices.csv")
    parser.add_argument("--cash", type=float, default=10_000.0)
    parser.add_argument("--fee-rate", type=float, default=0.001)
    parser.add_argument("--position-size", type=float, default=0.20)
    args = parser.parse_args()

    candles = load_csv(args.data)
    broker = PaperBroker(args.cash, BrokerConfig(args.fee_rate))
    engine = TradingEngine(broker, ExplainableStrategy(), RiskManager(RiskConfig(args.position_size, 1.0), fee_rate=args.fee_rate))
    report = engine.run(candles)
    print("PAPER TRADING REPORT")
    print(f"Starting cash : ${report.starting_cash:,.2f}")
    print(f"Ending equity : ${report.ending_equity:,.2f}")
    print(f"Position      : {report.position:.6f}")
    print(f"Fills         : {report.fills}")
    print(f"Fees          : ${report.fees:,.2f}")
    print(f"Realized PnL  : ${report.realized_pnl:,.2f}")


if __name__ == "__main__":
    main()
