from __future__ import annotations

from dataclasses import dataclass

from ai_trading_agent.live_paper_loop import LivePaperConfig, LivePaperSession
from ai_trading_agent.market_data import fetch_market_data


@dataclass(frozen=True)
class ReplayResult:
    symbol: str
    bars: int
    start_equity: float
    end_equity: float
    return_pct: float
    max_drawdown_pct: float
    fills: int
    realized_pnl: float


def replay(symbol: str, interval: str = "5m", range_: str = "1d", cash: float = 1000.0) -> ReplayResult:
    snapshot = fetch_market_data(symbol, interval, range_)
    candles = snapshot.candles
    if len(candles) < 20:
        raise RuntimeError(f"not enough intraday candles for {symbol}: {len(candles)}")

    session = LivePaperSession(LivePaperConfig(symbol=symbol, interval=interval, range_=range_, starting_cash=cash))
    peak = cash
    max_dd = 0.0
    for i in range(len(candles)):
        status = session.process_snapshot(candles[: i + 1])
        if status is not None:
            equity = float(status["equity"])
            peak = max(peak, equity)
            if peak > 0:
                max_dd = max(max_dd, (peak - equity) / peak * 100.0)

    final = session.broker.portfolio.mark_to_market(candles[-1].close)
    return ReplayResult(
        symbol, len(candles), cash, final, (final / cash - 1.0) * 100.0,
        max_dd, len(session.broker.portfolio.fills), session.broker.portfolio.realized_pnl,
    )


def main() -> None:
    symbols = ["GC=F", "EURUSD=X", "SPY", "BTC-USD"]
    print("LIVE-MARKET INTRADAY PAPER REPLAY")
    print("source=public Yahoo Finance; interval=5m; range=1d; starting_cash=1000; REAL ORDERS DISABLED")
    results: list[ReplayResult] = []
    for symbol in symbols:
        try:
            result = replay(symbol)
        except Exception as exc:
            print(f"symbol={symbol} status=DATA_ERROR error={exc}")
            continue
        results.append(result)
        print(
            f"symbol={result.symbol} bars={result.bars} return_pct={result.return_pct:.2f} "
            f"ending_equity={result.end_equity:.2f} max_drawdown_pct={result.max_drawdown_pct:.2f} "
            f"fills={result.fills} realized_pnl={result.realized_pnl:.2f}"
        )
    if not results:
        raise RuntimeError("No intraday market datasets were available")
    print(f"datasets_ok={len(results)}/{len(symbols)}")


if __name__ == "__main__":
    main()
