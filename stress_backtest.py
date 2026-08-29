from __future__ import annotations

import math
import random
from collections import Counter

from ai_trading_agent.backtest import run_backtest
from ai_trading_agent.models import Candle


def make_market(seed: int = 42, bars: int = 3000) -> list[Candle]:
    """Deterministic multi-regime synthetic market for robustness testing.

    Regimes rotate through bull, bear, range and high-volatility conditions.
    This is a stress test, not historical market data and must not be read as
    a forecast of future returns.
    """
    rng = random.Random(seed)
    price = 100.0
    candles: list[Candle] = []
    regime_len = bars // 6
    regimes = [
        (0.0008, 0.004),
        (-0.0008, 0.004),
        (0.0, 0.003),
        (0.0010, 0.010),
        (-0.0010, 0.010),
        (0.0002, 0.005),
    ]
    for i in range(bars):
        drift, sigma = regimes[min(i // regime_len, len(regimes) - 1)]
        ret = drift + rng.gauss(0.0, sigma)
        open_ = price
        close = max(1.0, open_ * math.exp(ret))
        high = max(open_, close) * (1.0 + abs(rng.gauss(0, sigma / 2)))
        low = min(open_, close) * (1.0 - abs(rng.gauss(0, sigma / 2)))
        candles.append(Candle(f"2020-01-01T{i:04d}", open_, high, low, close, 1000.0))
        price = close
    return candles


def main() -> None:
    results = []
    for seed in range(20):
        metrics = run_backtest(make_market(seed=seed), starting_cash=1000.0)
        results.append(metrics)

    returns = [m.return_pct for m in results]
    drawdowns = [m.max_drawdown_pct for m in results]
    fills = [m.fills for m in results]
    profitable = sum(r > 0 for r in returns)

    print("ROBUSTNESS PAPER BACKTEST")
    print("runs=20 bars_per_run=3000 starting_cash=1000")
    print(f"profitable_runs={profitable}/20")
    print(f"mean_return_pct={sum(returns)/len(returns):.2f}")
    print(f"median_return_pct={sorted(returns)[len(returns)//2]:.2f}")
    print(f"worst_return_pct={min(returns):.2f}")
    print(f"best_return_pct={max(returns):.2f}")
    print(f"mean_max_drawdown_pct={sum(drawdowns)/len(drawdowns):.2f}")
    print(f"worst_max_drawdown_pct={max(drawdowns):.2f}")
    print(f"mean_fills={sum(fills)/len(fills):.1f}")
    print(f"mean_fills_per_1000_bars={sum(fills)/len(fills)/3:.2f}")
    print("returns_pct=" + ",".join(f"{r:.2f}" for r in returns))


if __name__ == "__main__":
    main()
