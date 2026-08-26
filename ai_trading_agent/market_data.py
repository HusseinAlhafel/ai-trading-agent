from __future__ import annotations

import json
import time
from dataclasses import dataclass
from urllib.parse import quote
from urllib.request import Request, urlopen

from .models import Candle


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    interval: str
    candles: list[Candle]
    source: str = "Yahoo Finance chart feed"


def fetch_market_data(symbol: str, interval: str = "5m", range_: str = "1d", timeout: int = 15) -> MarketSnapshot:
    """Fetch public market candles for analysis only.

    This function never authenticates with or sends orders to Plus500.
    Quotes may be delayed and can differ from the broker's executable bid/ask.
    """
    encoded = quote(symbol, safe="")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?interval={quote(interval)}&range={quote(range_)}&events=history"
    request = Request(url, headers={"User-Agent": "ai-trading-agent/0.1"})
    with urlopen(request, timeout=timeout) as response:
        payload = json.load(response)

    result = payload.get("chart", {}).get("result")
    if not result:
        error = payload.get("chart", {}).get("error") or {}
        raise RuntimeError(f"market data unavailable for {symbol}: {error.get('description', 'unknown error')}")

    data = result[0]
    timestamps = data.get("timestamp") or []
    quote_data = (data.get("indicators", {}).get("quote") or [{}])[0]
    opens = quote_data.get("open") or []
    highs = quote_data.get("high") or []
    lows = quote_data.get("low") or []
    closes = quote_data.get("close") or []
    volumes = quote_data.get("volume") or []

    candles: list[Candle] = []
    for i, timestamp in enumerate(timestamps):
        values = (opens[i], highs[i], lows[i], closes[i]) if i < len(opens) and i < len(highs) and i < len(lows) and i < len(closes) else None
        if values is None or any(value is None for value in values):
            continue
        volume = volumes[i] if i < len(volumes) and volumes[i] is not None else 0.0
        candles.append(Candle(str(int(timestamp)), float(values[0]), float(values[1]), float(values[2]), float(values[3]), float(volume)))

    if not candles:
        raise RuntimeError(f"market data returned no usable candles for {symbol}")

    return MarketSnapshot(symbol=symbol, interval=interval, candles=candles)


def utc_now_label() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
