from ai_trading_agent.data import load_csv
from ai_trading_agent.signal_advisor import ManualSignalAdvisor


def test_manual_signal_is_non_executing():
    candles = load_csv("sample_prices.csv")
    signal = ManualSignalAdvisor().advise("DEMO", candles)

    assert signal.execution == "MANUAL_ONLY"
    assert signal.side in {"BUY", "SELL", "WAIT"}
    assert 0.0 <= signal.confidence <= 1.0
    assert signal.reference_price == candles[-1].close


def test_no_exit_levels_for_wait():
    advisor = ManualSignalAdvisor()
    signal = advisor.advise("DEMO", load_csv("sample_prices.csv"))
    if signal.side == "WAIT":
        assert advisor.exit_price(signal) is None
