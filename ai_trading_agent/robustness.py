from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass

from .backtest import run_backtest
from .models import Candle


@dataclass(frozen=True)
class ScenarioResult:
    scenario: str
    seed: int
    return_pct: float
    net_pnl: float
    fills: int
    max_drawdown_pct: float


def generate_candles(scenario: str, seed: int, n: int = 3000) -> list[Candle]:
    rng = random.Random(seed)
    price = 100.0
    candles: list[Candle] = []
    for i in range(n):
        if scenario == "bull":
            drift, vol = 0.00035, 0.009
        elif scenario == "bear":
            drift, vol = -0.00035, 0.009
        elif scenario == "sideways":
            drift, vol = 0.0, 0.007
        elif scenario == "high_volatility":
            drift, vol = 0.00005, 0.022
        else:
            raise ValueError(f"unknown scenario: {scenario}")

        shock = rng.gauss(0.0, vol)
        open_price = price
        close = max(1.0, price * math.exp(drift + shock))
        intrabar = abs(rng.gauss(0.0, vol * 0.65))
        high = max(open_price, close) * (1.0 + intrabar)
        low = min(open_price, close) / (1.0 + intrabar)
        volume = 1000.0 * (1.0 + rng.random())
        candles.append(
            Candle(
                timestamp=f"2020-01-01T00:{i // 60:02d}:{i % 60:02d}",
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
            )
        )
        price = close
    return candles


def run_robustness(trials_per_scenario: int = 5, candles_per_trial: int = 3000) -> list[ScenarioResult]:
    results: list[ScenarioResult] = []
    scenarios = ["bull", "bear", "sideways", "high_volatility"]
    for scenario_index, scenario in enumerate(scenarios):
        for trial in range(trials_per_scenario):
            seed = 20260829 + scenario_index * 100 + trial
            metrics = run_backtest(
                generate_candles(scenario, seed, candles_per_trial),
                starting_cash=1000.0,
            )
            results.append(
                ScenarioResult(
                    scenario=scenario,
                    seed=seed,
                    return_pct=metrics.return_pct,
                    net_pnl=metrics.net_pnl,
                    fills=metrics.fills,
                    max_drawdown_pct=metrics.max_drawdown_pct,
                )
            )
    return results


def main() -> None:
    results = run_robustness()
    returns = [r.return_pct for r in results]
    pnls = [r.net_pnl for r in results]
    print("ROBUSTNESS PAPER BACKTEST")
    print("starting_cash=1000.00")
    print(f"trials={len(results)} candles_per_trial=3000")
    print(f"profitable_trials={sum(r.return_pct > 0 for r in results)}")
    print(f"average_return_pct={statistics.mean(returns):.2f}")
    print(f"median_return_pct={statistics.median(returns):.2f}")
    print(f"best_return_pct={max(returns):.2f}")
    print(f"worst_return_pct={min(returns):.2f}")
    print(f"average_net_pnl={statistics.mean(pnls):.2f}")
    print(f"average_fills={statistics.mean(r.fills for r in results):.1f}")
    print(f"max_drawdown_pct={max(r.max_drawdown_pct for r in results):.2f}")
    for scenario in sorted({r.scenario for r in results}):
        subset = [r for r in results if r.scenario == scenario]
        print(
            f"scenario={scenario} avg_return_pct={statistics.mean(r.return_pct for r in subset):.2f} "
            f"profitable={sum(r.return_pct > 0 for r in subset)}/{len(subset)} "
            f"avg_fills={statistics.mean(r.fills for r in subset):.1f} "
            f"max_drawdown_pct={max(r.max_drawdown_pct for r in subset):.2f}"
        )


if __name__ == "__main__":
    main()
