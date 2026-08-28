import pytest

from ai_trading_agent.live_gate import LiveGateError, LiveSafetyConfig, authorize_live


def test_live_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("TRADING_MODE", raising=False)
    monkeypatch.delenv("ENABLE_LIVE_TRADING", raising=False)
    with pytest.raises(LiveGateError):
        authorize_live(LiveSafetyConfig())


def test_live_requires_two_explicit_opt_ins(monkeypatch):
    monkeypatch.setenv("TRADING_MODE", "LIVE")
    monkeypatch.setenv("ENABLE_LIVE_TRADING", "NO")
    with pytest.raises(LiveGateError):
        authorize_live(LiveSafetyConfig())


def test_live_gate_accepts_only_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("TRADING_MODE", "LIVE")
    monkeypatch.setenv("ENABLE_LIVE_TRADING", "YES")
    authorize_live(LiveSafetyConfig())


def test_kill_switch_fails_closed(monkeypatch):
    monkeypatch.setenv("TRADING_MODE", "LIVE")
    monkeypatch.setenv("ENABLE_LIVE_TRADING", "YES")
    with pytest.raises(LiveGateError):
        authorize_live(LiveSafetyConfig(kill_switch=True))
