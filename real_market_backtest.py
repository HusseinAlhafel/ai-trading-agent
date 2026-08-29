from __future__ import annotations

import datetime as dt
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


def _from_yfinance(symbol: str) -> list[Candle]:
    """Fetch daily OHLCV using yfinance (Yahoo Finance backend)."""
    import yfinance as yf

    frame = yf.download(
        symbol,
        period="20y",
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if frame is None or frame.empty:
        raise RuntimeError("empty yfinance response")
    if getattr(frame.columns, "nlevels", 1) > 1:
        frame.columns = frame.columns.get_level_values(0)
    candles: list[Candle] = []
    for index, row in frame.iterrows():
        try:
            timestamp = index.date().isoformat() if hasattr(index, "date") else str(index)[:10]
            candles.append(Candle(
                timestamp,
                float(row["Open"]), float(row["High"]),
                float(row["Low"]), float(row["Close"]), float(row.get("Volume", 0) or 0),
            ))
        except (KeyError, TypeError, ValueError):
            continue
    if len(candles) < 250:
        raise RuntimeError(f"only {len(candles)} usable daily candles")
    return candles


def _from_chart_api(symbol: str) -> list[Candle]:
    """Fallback to Yahoo's chart endpoint with retries."""
    end = int(time.time())
    start = end - 20 * 365 * 24 * 60 * 60
    params = urllib.parse.urlencode({"period1": start, "period2": end, "interval": "1d", "events": "history", "includeAdjustedClose": "true"})
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol, safe='')}?{params}"
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as response:
                import json
                payload = json.loads(response.read().decode("utf-8"))
            result = payload["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            quote = result["indicators"]["quote"][0]
            volumes = quote.get("volume") or [0] * len(timestamps)
            candles: list[Candle] = []
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
                raise RuntimeError(f"only {len(candles)} usable daily candles")
            return candles
        except Exception as exc:
            last_error = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Yahoo chart API failed: {last_error}")


def fetch_market(symbol: str) -> list[Candle]:
    errors: list[str] = []
    try:
        return _from_yfinance(symbol)
    except Exception as exc:
        errors.append(f"yfinance={exc}")
    try:
        return _from_chart_api(symbol)
    except Exception as exc:
        errors.append(f"chart_api={exc}")
    raise RuntimeError("; ".join(errors))


def main() -> None:
    symbols = ["SPY", "QQQ", "GLD", "EURUSD=X"]
    results: list[Result] = []
    print("REAL MARKET PAPER BACKTEST")
    print("source=Yahoo Finance via yfinance/chart API; lookback=20y; starting_cash=1000.00; fee_rate=0.10%")
    for symbol in symbols:
        try:
            candles = fetch_market(symbol)
            metrics = run_backtest(candles, starting_cash=1000.0)
        except Exception as exc:
            print(f"symbol={symbol} status=DATA_ERROR error={exc}")
            continue
        result = Result(symbol, len(candles), metrics.return_pct, metrics.net_pnl, metrics.fills, metrics.max_drawdown_pct)
        results.append(result)
        print(f"symbol={symbol} bars={result.bars} return_pct={result.return_pct:.2f} pnl={result.pnl:.2f} fills={result.fills} max_drawdown_pct={result.max_drawdown_pct:.2f}")

    if not results:
        raise RuntimeError("No real-market datasets were available")
    print(f"portfolio_mean_return_pct={statistics.mean(r.return_pct for r in results):.2f}")
    print(f"portfolio_median_return_pct={statistics.median(r.return_pct for r in results):.2f}")
    print(f"profitable_symbols={sum(r.return_pct > 0 for r in results)}/{len(results)}")
    print(f"mean_fills={statistics.mean(r.fills for r in results):.1f}")
    print(f"mean_max_drawdown_pct={statistics.mean(r.max_drawdown_pct for r in results):.2f}")


if __name__ == "__main__":
    main()
