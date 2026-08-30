from __future__ import annotations

import statistics
from dataclasses import dataclass

from ai_trading_agent.models import Candle
from robust_validation import realistic_backtest
from real_market_backtest import fetch_market


@dataclass(frozen=True)
class PortfolioResult:
    symbol: str
    ending_equity: float
    return_pct: float
    max_drawdown_pct: float
    fills: int


def run_portfolio(starting_cash: float = 1000.0, fee_rate: float = 0.001, slippage_bps: float = 10.0) -> None:
    symbols = ["SPY", "QQQ", "GLD", "EURUSD=X"]
    allocation = starting_cash / len(symbols)
    results: list[PortfolioResult] = []

    print("PORTFOLIO OOS VALIDATION")
    print(f"starting_cash={starting_cash:.2f} allocation_per_symbol={allocation:.2f} fee_pct={fee_rate*100:.2f} slippage_bps={slippage_bps:.1f}")

    for symbol in symbols:
        candles = fetch_market(symbol)
        split = int(len(candles) * 0.70)
        metrics = realistic_backtest(
            candles,
            starting_cash=allocation,
            fee_rate=fee_rate,
            slippage_bps=slippage_bps,
            start_index=split,
        )
        ending = allocation * (1.0 + metrics.return_pct / 100.0)
        results.append(PortfolioResult(symbol, ending, metrics.return_pct, metrics.max_drawdown_pct, metrics.fills))
        print(
            f"symbol={symbol} oos_return_pct={metrics.return_pct:.2f} "
            f"ending_equity={ending:.2f} max_drawdown_pct={metrics.max_drawdown_pct:.2f} fills={metrics.fills}"
        )

    ending_total = sum(r.ending_equity for r in results)
    return_pct = (ending_total / starting_cash - 1.0) * 100.0
    print("PORTFOLIO SUMMARY")
    print(f"ending_equity={ending_total:.2f}")
    print(f"net_pnl={ending_total-starting_cash:.2f}")
    print(f"return_pct={return_pct:.2f}")
    print(f"mean_asset_return_pct={statistics.mean(r.return_pct for r in results):.2f}")
    print(f"median_asset_return_pct={statistics.median(r.return_pct for r in results):.2f}")
    print(f"profitable_assets={sum(r.return_pct > 0 for r in results)}/{len(results)}")
    print(f"mean_asset_drawdown_pct={statistics.mean(r.max_drawdown_pct for r in results):.2f}")
    print(f"total_fills={sum(r.fills for r in results)}")


if __name__ == "__main__":
    run_portfolio()
