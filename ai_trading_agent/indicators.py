from __future__ import annotations


def sma(values: list[float], period: int) -> float | None:
    if period <= 0:
        raise ValueError("period must be positive")
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def momentum(values: list[float], period: int) -> float | None:
    if period <= 0:
        raise ValueError("period must be positive")
    if len(values) <= period:
        return None
    base = values[-period - 1]
    if base == 0:
        return None
    return values[-1] / base - 1.0


def volatility(values: list[float], period: int) -> float | None:
    if period <= 1 or len(values) < period:
        return None
    window = values[-period:]
    mean = sum(window) / period
    variance = sum((x - mean) ** 2 for x in window) / period
    return variance**0.5 / mean if mean else None
