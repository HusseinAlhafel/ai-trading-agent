from ai_trading_agent.broker import PaperBroker
from ai_trading_agent.engine import TradingEngine
from ai_trading_agent.models import Candle, Side
from ai_trading_agent.risk import RiskManager
from ai_trading_agent.strategy import ExplainableStrategy


def test_engine_never_exceeds_max_position():
    candles = [Candle(str(i), 100 + i, 101 + i, 99 + i, 100 + i, 100) for i in range(30)]
    broker = PaperBroker(1000)
    report = TradingEngine(broker, ExplainableStrategy(), RiskManager()).run(candles)
    assert report.position * candles[-1].close <= report.ending_equity + 1e-6


def test_engine_cooldown_is_configurable():
    candles = [Candle(str(i), 100 + i, 101 + i, 99 + i, 100 + i, 100) for i in range(30)]
    broker = PaperBroker(1000)
    engine = TradingEngine(broker, ExplainableStrategy(), RiskManager(), trade_cooldown_bars=3)
    report = engine.run(candles)
    fill_indices = [next(i for i, c in enumerate(candles) if c.timestamp == fill.timestamp) for fill in broker.portfolio.fills]
    assert all(b - a > 3 for a, b in zip(fill_indices, fill_indices[1:]))
    assert report.fills == len(broker.portfolio.fills)
