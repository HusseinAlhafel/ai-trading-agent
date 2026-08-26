from datetime import datetime, timezone

import pytest

from ai_trading_agent.models import Order, Side
from ai_trading_agent.plus500_t4_adapter import Plus500T4Adapter, Plus500T4Config, Plus500T4NotConfigured


def test_t4_is_disabled_by_default() -> None:
    adapter = Plus500T4Adapter()
    assert adapter.status()["enabled"] is False
    assert adapter.status()["live_trading"] is False
    assert adapter.status()["order_submission"] is False


def test_t4_rejects_order_submission() -> None:
    adapter = Plus500T4Adapter(Plus500T4Config(enabled=True, live_trading=True))
    order = Order(Side.BUY, 1.0, 100.0, datetime.now(timezone.utc))
    with pytest.raises(Plus500T4NotConfigured):
        adapter.submit(order)
