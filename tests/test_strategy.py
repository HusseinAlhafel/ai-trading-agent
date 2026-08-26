from ai_trading_agent.models import Candle, Side
from ai_trading_agent.strategy import ExplainableStrategy


def candles(values):
    return [Candle(str(i), v, v + 1, v - 1, v, 100) for i, v in enumerate(values)]


def test_strategy_warms_up():
    signal = ExplainableStrategy().decide(candles([100, 101, 102]))
    assert signal.side is None


def test_uptrend_can_generate_buy():
    signal = ExplainableStrategy().decide(candles(list(range(100, 120))))
    assert signal.side is Side.BUY
    assert signal.score > 0
