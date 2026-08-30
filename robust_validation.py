from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass

from ai_trading_agent.broker import BrokerConfig, PaperBroker
from ai_trading_agent.models import Candle, Order, Side
from ai_trading_agent.risk import RiskManager
from ai_trading_agent.strategy import ExplainableStrategy
from real_market_backtest import fetch_market


@dataclass(frozen=True)
class Metrics:
    return_pct: float
    max_drawdown_pct: float
    fills: int
    fees: float


def realistic_backtest(
    candles: list[Candle],
    starting_cash: float = 1000.0,
    fee_rate: float = 0.001,
    slippage_bps: float = 0.0,
    start_index: int = 0,
) -> Metrics:
    """No-lookahead paper backtest: signal uses prior bars, fill uses next bar open."""
    if len(candles) < 20:
        raise ValueError("not enough candles")
    if fee_rate < 0 or slippage_bps < 0:
        raise ValueError("costs must be non-negative")

    broker = PaperBroker(starting_cash, BrokerConfig(fee_rate=fee_rate))
    strategy = ExplainableStrategy()
    risk = RiskManager(fee_rate=fee_rate)
    history = list(candles[:start_index])
    peak = starting_cash
    max_dd = 0.0

    for i in range(max(start_index, 1), len(candles)):
        candle = candles[i]
        signal = strategy.decide(history)
        execution_price = candle.open * (
            1.0 + slippage_bps / 10_000 if signal.side is Side.BUY else
            1.0 - slippage_bps / 10_000
        )
        if signal.side is not None and execution_price > 0:
            qty = risk.quantity(signal.side, broker.portfolio, execution_price)
            if qty > 1e-12:
                try:
                    broker.submit(Order(signal.side, qty, execution_price, candle.timestamp))
                except ValueError:
                    pass
        equity = broker.portfolio.mark_to_market(candle.close)
        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - equity) / peak * 100)
        history.append(candle)

    ending = broker.portfolio.mark_to_market(candles[-1].close)
    return Metrics((ending / starting_cash - 1) * 100, max_dd, len(broker.portfolio.fills), broker.portfolio.fees_paid)


def monte_carlo_paths(candles: list[Candle], paths: int = 300, bars: int = 1200, block: int = 10, seed: int = 2026) -> list[float]:
    """Block-bootstrap close-to-close returns to preserve short-term dependence."""
    if len(candles) < block + 2:
        raise ValueError("not enough candles for Monte Carlo")
    returns = [math.log(candles[i].close / candles[i - 1].close) for i in range(1, len(candles))]
    rng = random.Random(seed)
    out: list[float] = []
    start = candles[-1].close
    for path_id in range(paths):
        selected: list[float] = []
        while len(selected) < bars:
            j = rng.randrange(0, len(returns) - block + 1)
            selected.extend(returns[j:j + block])
        selected = selected[:bars]
        generated: list[Candle] = []
        price = start
        for i, ret in enumerate(selected):
            open_ = price
            close = max(0.01, open_ * math.exp(ret))
            high = max(open_, close)
            low = min(open_, close)
            generated.append(Candle(f"MC-{path_id:04d}-{i:05d}", open_, high, low, close, 0.0))
            price = close
        out.append(realistic_backtest(generated).return_pct)
    return out


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return float("nan")
    k = (len(ordered) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def main() -> None:
    symbols = ["SPY", "QQQ", "GLD", "EURUSD=X"]
    datasets: dict[str, list[Candle]] = {}
    print("ROBUST VALIDATION — NO LOOKAHEAD")
    for symbol in symbols:
        candles = fetch_market(symbol)
        datasets[symbol] = candles
        split = int(len(candles) * 0.70)
        oos = realistic_backtest(candles, start_index=split)
        full = realistic_backtest(candles)
        print(
            f"OOS symbol={symbol} bars={len(candles)-split} "
            f"return_pct={oos.return_pct:.2f} max_drawdown_pct={oos.max_drawdown_pct:.2f} fills={oos.fills}"
        )
        print(
            f"FULL symbol={symbol} return_pct={full.return_pct:.2f} "
            f"max_drawdown_pct={full.max_drawdown_pct:.2f} fills={full.fills}"
        )

    print("\nCOST SENSITIVITY — OOS ONLY")
    for fee in (0.001, 0.002, 0.005):
        for slip in (0.0, 5.0, 10.0, 25.0):
            results = []
            for candles in datasets.values():
                split = int(len(candles) * 0.70)
                results.append(realistic_backtest(candles, fee_rate=fee, slippage_bps=slip, start_index=split).return_pct)
            print(
                f"fee_pct={fee*100:.2f} slippage_bps={slip:.1f} "
                f"mean_return_pct={statistics.mean(results):.2f} profitable={sum(x>0 for x in results)}/{len(results)} "
                f"worst_pct={min(results):.2f}"
            )

    print("\nMONTE CARLO — BLOCK BOOTSTRAP")
    all_mc: list[float] = []
    for symbol, candles in datasets.items():
        values = monte_carlo_paths(candles, paths=300, bars=1200, block=10, seed=2026 + len(symbol))
        all_mc.extend(values)
        print(
            f"MC symbol={symbol} paths=300 median_pct={statistics.median(values):.2f} "
            f"p05_pct={percentile(values, .05):.2f} p95_pct={percentile(values, .95):.2f} "
            f"loss_rate={sum(x<0 for x in values)/len(values)*100:.1f}%"
        )
    print(
        f"MC aggregate_paths={len(all_mc)} median_pct={statistics.median(all_mc):.2f} "
        f"p05_pct={percentile(all_mc,.05):.2f} p95_pct={percentile(all_mc,.95):.2f} "
        f"loss_rate={sum(x<0 for x in all_mc)/len(all_mc)*100:.1f}%"
    )


if __name__ == "__main__":
    main()
