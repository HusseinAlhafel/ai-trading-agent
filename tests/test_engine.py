from ai_trading_agent.broker import PaperBroker
from ai_trading_agent.engine import TradingEngine
from ai_trading_agent.models import Candle
from ai_trading_agent.risk import RiskManager
from ai_trading_agent.strategy import ExplainableStrategy


def test_engine_never_exceeds_max_position():
    candles = [Candle(str(i), 100 + i, 101 + i, 99 + i, 100 + i, 100) for i in range(30)]
    broker = PaperBroker(1000)
    report = TradingEngine(broker, ExplainableStrategy(), RiskManager()).run(candles)
    assert report.position * candles[-1].close <= report.ending_equity + 1e-6
