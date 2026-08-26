from __future__ import annotations

import argparse

from .indicators import volatility
from .market_data import fetch_market_data, utc_now_label
from .strategy import ExplainableStrategy


def main() -> None:
    parser = argparse.ArgumentParser(description="Market-data signal advisor; manual execution only")
    parser.add_argument("--symbol", default="EURUSD=X", help="Yahoo Finance symbol, e.g. EURUSD=X, BTC-USD, AAPL, GC=F")
    parser.add_argument("--interval", default="5m")
    parser.add_argument("--range", dest="range_", default="1d")
    parser.add_argument("--candles", type=int, default=80)
    args = parser.parse_args()

    snapshot = fetch_market_data(args.symbol, args.interval, args.range_)
    candles = snapshot.candles[-args.candles :]
    signal = ExplainableStrategy().decide(candles)
    last = candles[-1]
    vol = volatility([c.close for c in candles], min(10, len(candles))) or 0.0

    print("AI TRADING SIGNAL — MANUAL EXECUTION ONLY")
    print(f"Checked       : {utc_now_label()}")
    print(f"Symbol        : {snapshot.symbol}")
    print(f"Interval      : {snapshot.interval}")
    print(f"Data source   : {snapshot.source}")
    print(f"Last price    : {last.close:.8f}")
    print(f"Signal        : {signal.side.value if signal.side else 'WAIT'}")
    print(f"Score         : {signal.score:+.2f}")
    print(f"Reason        : {signal.reason}")
    print(f"Volatility    : {vol:.2%}")

    if signal.side is not None:
        distance = max(last.close * max(vol * 1.5, 0.005), last.close * 0.005)
        if signal.side.value == "BUY":
            stop = last.close - distance
            target = last.close + distance * 2
        else:
            stop = last.close + distance
            target = last.close - distance * 2
        print(f"Reference SL  : {stop:.8f}")
        print(f"Reference TP  : {target:.8f}")

    print("NOTE          : This tool only produces an analysis signal. It does not log in to Plus500 and cannot place orders.")


if __name__ == "__main__":
    main()
