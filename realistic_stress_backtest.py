from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass

from ai_trading_agent.broker import BrokerConfig, PaperBroker
from ai_trading_agent.engine import TradingEngine
from ai_trading_agent.models import Candle, Order, Side
from ai_trading_agent.risk import RiskManager
from ai_trading_agent.strategy import ExplainableStrategy


@dataclass(frozen=True)
class Case:
    name: str
    fee_bps: float
    slippage_bps: float
    crash_probability: float
    shock_sigma: float


CASES = [
    Case("baseline", 10, 0, 0.00, 0.00),
    Case("realistic_costs", 10, 5, 0.00, 0.00),
    Case("stressed_costs", 20, 15, 0.00, 0.00),
    Case("crash_shocks", 10, 5, 0.006, 0.08),
    Case("high_volatility", 10, 10, 0.002, 0.12),
]


def make_market(seed: int, bars: int = 3000) -> list[Candle]:
    rng = random.Random(seed)
    price = 100.0
    candles: list[Candle] = []
    regime_len = max(1, bars // 6)
    regimes = [
        (0.0005, 0.004),
        (-0.0005, 0.004),
        (0.0, 0.0035),
        (0.0007, 0.008),
        (-0.0007, 0.008),
        (0.0001, 0.005),
    ]
    for i in range(bars):
        drift, sigma = regimes[min(i // regime_len, len(regimes) - 1)]
        ret = drift + rng.gauss(0.0, sigma)
        if rng.random() < (0.006 if sigma >= 0.008 else 0.001):
            ret += rng.choice((-1, 1)) * abs(rng.gauss(0.0, 0.04))
        open_ = price
        close = max(1.0, open_ * math.exp(ret))
        high = max(open_, close) * (1.0 + abs(rng.gauss(0, sigma / 2)))
        low = min(open_, close) * (1.0 - abs(rng.gauss(0, sigma / 2)))
        candles.append(Candle(f"2020-01-01T{i:04d}", open_, high, low, close, 1000.0))
        price = close
    return candles


def inject_shocks(candles: list[Candle], seed: int, probability: float, sigma: float) -> list[Candle]:
    if probability <= 0:
        return candles
    rng = random.Random(seed + 100000)
    out: list[Candle] = []
    price = candles[0].open
    for c in candles:
        shock = 0.0
        if rng.random() < probability:
            shock = -abs(rng.gauss(0.0, sigma))
        open_ = price
        close = max(1.0, c.close * math.exp(shock))
        scale = max(0.001, abs(close / max(c.close, 1e-12) - 1.0))
        high = max(open_, close) * (1.0 + max(0.001, abs(c.high / max(c.close, 1e-12) - 1.0)))
        low = min(open_, close) * (1.0 - max(0.001, abs(c.low / max(c.close, 1e-12) - 1.0) + scale / 2))
        out.append(Candle(c.timestamp, open_, high, low, close, c.volume))
        price = close
    return out


class SlippagePaperBroker(PaperBroker):
    """In-memory broker that applies deterministic adverse slippage to fills."""

    def __init__(self, starting_cash: float, fee_rate: float, slippage_rate: float) -> None:
        super().__init__(starting_cash, BrokerConfig(fee_rate=fee_rate))
        if not 0 <= slippage_rate < 1:
            raise ValueError("slippage_rate must be in [0, 1)")
        self.slippage_rate = slippage_rate

    def submit(self, order: Order):
        slipped = order.price * (
            1 + self.slippage_rate if order.side is Side.BUY else 1 - self.slippage_rate
        )
        return super().submit(Order(order.side, order.quantity, slipped, order.timestamp))


def run_case(candles: list[Candle], case: Case) -> tuple[float, float, int, float, float]:
    fee_rate = case.fee_bps / 10000.0
    slippage = case.slippage_bps / 10000.0
    broker = SlippagePaperBroker(1000.0, fee_rate, slippage)
    risk = RiskManager(fee_rate=fee_rate)
    engine = TradingEngine(broker, ExplainableStrategy(), risk)
    report = engine.run(candles)

    equity_returns: list[float] = []
    previous_equity = 1000.0
    peak = 1000.0
    max_dd = 0.0
    for candle in candles:
        equity = broker.portfolio.mark_to_market(candle.close)
        if previous_equity > 0:
            equity_returns.append(equity / previous_equity - 1.0)
        previous_equity = equity
        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - equity) / peak * 100.0)

    mean = statistics.mean(equity_returns) if equity_returns else 0.0
    stdev = statistics.stdev(equity_returns) if len(equity_returns) > 1 else 0.0
    sharpe = mean / stdev * math.sqrt(252) if stdev > 0 else 0.0
    return (report.ending_equity / 1000.0 - 1.0) * 100.0, max_dd, report.fills, report.fees, sharpe


def main() -> None:
    runs_per_case = 20
    print("REALISTIC PAPER-TRADING STRESS TEST")
    print("No live orders; synthetic OHLCV only; engine risk protections are enabled; Sharpe is not a market forecast.")
    print(f"cases={len(CASES)} runs_per_case={runs_per_case} total_runs={len(CASES) * runs_per_case} bars_per_run=3000 starting_cash=1000")
    for case in CASES:
        results = []
        for seed in range(runs_per_case):
            candles = make_market(seed)
            candles = inject_shocks(candles, seed, case.crash_probability, case.shock_sigma)
            results.append(run_case(candles, case))
        returns = [x[0] for x in results]
        dds = [x[1] for x in results]
        fills = [x[2] for x in results]
        fees = [x[3] for x in results]
        sharpes = [x[4] for x in results]
        profitable = sum(r > 0 for r in returns)
        print(f"\n[{case.name}] fee_bps={case.fee_bps} slippage_bps={case.slippage_bps}")
        print(f"profitable_runs={profitable}/{runs_per_case}")
        print(f"mean_return_pct={statistics.mean(returns):.2f}")
        print(f"median_return_pct={statistics.median(returns):.2f}")
        print(f"worst_return_pct={min(returns):.2f}")
        print(f"best_return_pct={max(returns):.2f}")
        print(f"mean_max_drawdown_pct={statistics.mean(dds):.2f}")
        print(f"worst_max_drawdown_pct={max(dds):.2f}")
        print(f"mean_fills={statistics.mean(fills):.1f}")
        print(f"mean_fees={statistics.mean(fees):.2f}")
        print(f"mean_annualized_sharpe={statistics.mean(sharpes):.2f}")
        print("returns_pct=" + ",".join(f"{r:.2f}" for r in returns))


if __name__ == "__main__":
    main()
