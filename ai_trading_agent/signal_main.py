from __future__ import annotations

import argparse

from .data import load_csv
from .signal_advisor import ManualSignalAdvisor


def main() -> None:
    parser = argparse.ArgumentParser(description="Manual Plus500 signal generator (no order execution)")
    parser.add_argument("--data", default="sample_prices.csv")
    parser.add_argument("--symbol", default="DEMO")
    parser.add_argument("--position-size", type=float, default=0.20)
    parser.add_argument("--stop-loss", type=float, default=0.01)
    parser.add_argument("--take-profit", type=float, default=0.02)
    args = parser.parse_args()

    candles = load_csv(args.data)
    advisor = ManualSignalAdvisor(
        position_fraction=args.position_size,
        stop_loss_fraction=args.stop_loss,
        take_profit_fraction=args.take_profit,
    )
    signal = advisor.advise(args.symbol, candles)

    print("MANUAL PLUS500 SIGNAL")
    print("======================")
    print(f"Symbol              : {signal.symbol}")
    print(f"Signal              : {signal.side}")
    print(f"Confidence          : {signal.confidence:.0%}")
    print(f"Reference price     : {signal.reference_price:.6f}")
    print(f"Position fraction   : {signal.suggested_position_fraction:.0%}")
    print(f"Timestamp           : {signal.timestamp}")
    print(f"Reason              : {signal.reason}")

    exits = advisor.exit_price(signal)
    if exits is not None:
        stop_loss, take_profit = exits
        print(f"Stop-loss reference : {stop_loss:.6f}")
        print(f"Take-profit ref.    : {take_profit:.6f}")

    print("Execution           : MANUAL ONLY")
    print("No Plus500 order was submitted.")


if __name__ == "__main__":
    main()
