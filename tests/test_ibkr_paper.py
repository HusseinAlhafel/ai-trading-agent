import pytest

from ai_trading_agent.ibkr_paper import IBKRPaperConfig, IBKRPaperOnlyError


def test_ibkr_paper_defaults_are_safe() -> None:
    config = IBKRPaperConfig()
    config.validate()
    assert config.base_url == "https://127.0.0.1:5000/v1/api"
    assert config.verify_ssl is False


def test_ibkr_rejects_non_local_endpoint() -> None:
    with pytest.raises(IBKRPaperOnlyError):
        IBKRPaperConfig(base_url="https://127.0.0.1:7496/v1/api").validate()


def test_ibkr_rejects_invalid_timeout() -> None:
    with pytest.raises(ValueError):
        IBKRPaperConfig(timeout_seconds=0).validate()
