from __future__ import annotations

import csv
import io
import statistics
import urllib.request
from dataclasses import dataclass

from ai_trading_agent.backtest import run_backtest
from ai_trading_agent.models import Candle


@dataclass(frozen=True)
class Result:
    symbol: str
    return_pct: float
    pnl: float
    fills: int
    max_drawdown_pct: float


def fetch_stooq(symbol: str) -> list[Candle]:
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        text = response.read().decode("utf-8")
    if not text.startswith("Date,"):
        raise RuntimeError(f"{symbol}: data provider returned no CSV data")
    rows = list(csv.DictReader(io.StringIO(text)))
    candles: list[Candle] = []
    for row in rows:
        try:
            candles.append(Candle(row["Date"], float(row["Open"]), float(row["High"]), float(row["Low"]), float(row["Close"]), float(row.get("Volume") or 0)))
        except (KeyError, ValueError):
            continue
    if len(candles) < 250:
        raise RuntimeError(f"{symbol}: only {len(candles)} usable candles")
    return candles


def main() -> None:
    symbols = ["spy.us", "qqq.us", "gld.us", "eurusd"]
    results: list[Result] = []
    print("REAL MARKET PAPER BACKTEST")
    print("starting_cash=1000.00; timeframe=daily; fees=0.10% per fill")
    for symbol in symbols:
        try:
            candles = fetch_stooq(symbol)
        except Exception as exc:
            print(f"symbol={symbol} status=DATA_ERROR error={exc}")
            continue
        metrics = run_backtest(candles, starting_cash=1000.0)
        results.append(Result(symbol, metrics.return_pct, metrics.net_pnl, metrics.fills, metrics.max_drawdown_pct))
        print(f"symbol={symbol} bars={len(candles)} return_pct={metrics.return_pct:.2f} pnl={metrics.net_pnl:.2f} fills={metrics.fills} max_drawdown_pct={metrics.max_drawdown_pct:.2f}")

    if not results:
        raise RuntimeError("No real-market datasets were available")
    print(f"portfolio_mean_return_pct={statistics.mean(r.return_pct for r in results):.2f}")
    print(f"portfolio_median_return_pct={statistics.median(r.return_pct for r in results):.2f}")
    print(f"profitable_symbols={sum(r.return_pct > 0 for r in results)}/{len(results)}")
    print(f"mean_fills={statistics.mean(r.fills for r in results):.1f}")
    print(f"mean_max_drawdown_pct={statistics.mean(r.max_drawdown_pct for r in results):.2f}")


if __name__ == "__main__":
    main()
