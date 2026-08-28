import pytest

from ai_trading_agent.ibkr_paper import IBKRPaperConfig, IBKRPaperOnlyError


def test_ibkr_paper_defaults_are_safe() -> None:
    config = IBKRPaperConfig()
    config.validate()
    assert config.port == 7497


def test_ibkr_rejects_live_port() -> None:
    with pytest.raises(IBKRPaperOnlyError):
        IBKRPaperConfig(port=7496).validate()


def test_ibkr_rejects_invalid_timeout() -> None:
    with pytest.raises(ValueError):
        IBKRPaperConfig(timeout_seconds=0).validate()
