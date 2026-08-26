from __future__ import annotations

import csv
from pathlib import Path

from .models import Candle


def load_csv(path: str | Path) -> list[Candle]:
    rows: list[Candle] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"timestamp", "open", "high", "low", "close", "volume"}
        if not required.issubset(reader.fieldnames or set()):
            raise ValueError(f"CSV must contain: {', '.join(sorted(required))}")
        for row in reader:
            candle = Candle(
                timestamp=row["timestamp"],
                open=float(row["open"]), high=float(row["high"]),
                low=float(row["low"]), close=float(row["close"]),
                volume=float(row["volume"]),
            )
            if candle.low <= 0 or candle.high < candle.low or not (candle.low <= candle.open <= candle.high) or not (candle.low <= candle.close <= candle.high):
                raise ValueError(f"invalid OHLC values at {candle.timestamp}")
            rows.append(candle)
    if not rows:
        raise ValueError("CSV contains no candles")
    return rows
