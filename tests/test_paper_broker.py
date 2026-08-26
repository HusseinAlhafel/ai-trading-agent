from ai_trading_agent.broker import PaperBroker
from ai_trading_agent.models import Order, Side


def test_buy_and_mark_to_market_are_paper_only():
    broker = PaperBroker(1000.0)
    fill = broker.submit(Order(Side.BUY, 1.0, 100.0, "t1"))
    assert fill.side is Side.BUY
    assert broker.portfolio.position == 1.0
    assert broker.portfolio.cash < 900.0
    assert broker.portfolio.equity == broker.portfolio.cash + 100.0
    assert broker.portfolio.average_entry_price == 100.1


def test_cannot_sell_more_than_position():
    broker = PaperBroker(1000.0)
    try:
        broker.submit(Order(Side.SELL, 1.0, 100.0, "t1"))
    except ValueError as exc:
        assert "position" in str(exc)
    else:
        raise AssertionError("short selling must not be enabled")


def test_realized_pnl_uses_entry_price_and_fee():
    broker = PaperBroker(1000.0)
    broker.submit(Order(Side.BUY, 1.0, 100.0, "t1"))
    broker.submit(Order(Side.SELL, 1.0, 110.0, "t2"))
    assert broker.portfolio.position == 0.0
    assert abs(broker.portfolio.realized_pnl - 9.79) < 1e-9
