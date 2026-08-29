from __future__ import annotations

import json
import statistics
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass

from ai_trading_agent.backtest import run_backtest
from ai_trading_agent.models import Candle


@dataclass(frozen=True)
class Result:
    symbol: str
    bars: int
    return_pct: float
    pnl: float
    fills: int
    max_drawdown_pct: float


def fetch_yahoo(symbol: str) -> list[Candle]:
    params = urllib.parse.urlencode({"period1": 0, "period2": int(time.time()), "interval": "1d", "events": "history", "includeAdjustedClose": "true"})
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol, safe='')}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    quote = result["indicators"]["quote"][0]
    volumes = quote.get("volume") or [0] * len(timestamps)
    candles: list[Candle] = []
    import datetime as dt
    for i, ts in enumerate(timestamps):
        try:
            candles.append(Candle(
                dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat(),
                float(quote["open"][i]), float(quote["high"][i]),
                float(quote["low"][i]), float(quote["close"][i]), float(volumes[i] or 0),
            ))
        except (IndexError, TypeError, ValueError):
            continue
    if len(candles) < 250:
        raise RuntimeError(f"{symbol}: only {len(candles)} usable daily candles")
    return candles


def main() -> None:
    symbols = ["SPY", "QQQ", "GLD", "EURUSD=X"]
    results: list[Result] = []
    print("REAL MARKET PAPER BACKTEST")
    print("starting_cash=1000.00; timeframe=daily; fees=0.10% per fill")
    for symbol in symbols:
        try:
            candles = fetch_yahoo(symbol)
            metrics = run_backtest(candles, starting_cash=1000.0)
        except Exception as exc:
            print(f"symbol={symbol} status=DATA_ERROR error={exc}")
            continue
        results.append(Result(symbol, len(candles), metrics.return_pct, metrics.net_pnl, metrics.fills, metrics.max_drawdown_pct))
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
