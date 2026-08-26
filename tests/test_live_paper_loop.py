from ai_trading_agent.live_paper_loop import LivePaperConfig, LivePaperSession
from ai_trading_agent.models import Candle


def candles(count: int = 14) -> list[Candle]:
    return [
        Candle(str(i), 100.0 + i, 101.0 + i, 99.0 + i, 100.0 + i, 1_000.0)
        for i in range(count)
    ]


def test_live_paper_session_ignores_duplicate_candle() -> None:
    session = LivePaperSession(LivePaperConfig(starting_cash=1_000.0))
    data = candles()

    first = session.process_snapshot(data)
    assert first is not None
    fills_after_first = len(session.broker.portfolio.fills)

    duplicate = session.process_snapshot(data)
    assert duplicate is None
    assert len(session.broker.portfolio.fills) == fills_after_first


def test_live_paper_session_processes_only_newest_candle() -> None:
    session = LivePaperSession(LivePaperConfig(starting_cash=1_000.0))
    data = candles()

    first = session.process_snapshot(data)
    assert first is not None
    assert session.last_timestamp == "13"

    extended = data + [Candle("14", 114.0, 115.0, 113.0, 114.0, 1_000.0)]
    second = session.process_snapshot(extended)
    assert second is not None
    assert second["timestamp"] == "14"
    assert session.last_timestamp == "14"
    assert len(session.history) == 15


def test_live_paper_config_rejects_non_positive_poll() -> None:
    config = LivePaperConfig(poll_seconds=0)
    try:
        config.validate()
    except ValueError as exc:
        assert "poll_seconds" in str(exc)
    else:
        raise AssertionError("expected ValueError")
