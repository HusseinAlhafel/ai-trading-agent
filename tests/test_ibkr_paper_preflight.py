from __future__ import annotations

import os

from scripts.ibkr_paper_preflight import main


def test_preflight_defaults_to_paper(monkeypatch, capsys):
    monkeypatch.delenv("IBKR_PORT", raising=False)
    monkeypatch.setenv("IBKR_HOST", "127.0.0.1")
    assert main() == 0
    out = capsys.readouterr().out
    assert "7497" in out
    assert "LIVE TRADING: DISABLED" in out


def test_preflight_rejects_non_paper_port(monkeypatch, capsys):
    monkeypatch.setenv("IBKR_PORT", "7496")
    assert main() == 3
    assert "REFUSED" in capsys.readouterr().out
