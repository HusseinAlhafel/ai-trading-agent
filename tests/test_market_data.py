from ai_trading_agent.market_data import MarketSnapshot
from ai_trading_agent.models import Candle


def test_market_snapshot_is_analysis_only() -> None:
    snapshot = MarketSnapshot(
        symbol="TEST",
        interval="5m",
        candles=[Candle("1", 1, 1.1, 0.9, 1.05)],
    )
    assert snapshot.symbol == "TEST"
    assert snapshot.candles[-1].close == 1.05
    assert "Yahoo" in snapshot.source
