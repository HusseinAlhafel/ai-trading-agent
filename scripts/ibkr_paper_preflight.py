"""Fail-closed preflight for IBKR Paper Trading.

This script intentionally accepts only the IBKR Paper socket port (7497).
It does not place orders.
"""
from __future__ import annotations

import os
import sys

PAPER_PORT = 7497


def main() -> int:
    host = os.getenv("IBKR_HOST", "127.0.0.1")
    raw_port = os.getenv("IBKR_PORT", str(PAPER_PORT))
    try:
        port = int(raw_port)
    except ValueError:
        print(f"ERROR: IBKR_PORT must be an integer, got {raw_port!r}")
        return 2

    if port != PAPER_PORT:
        print(f"REFUSED: only IBKR Paper port {PAPER_PORT} is supported; got {port}.")
        return 3

    print(f"READY FOR PAPER PREFLIGHT: {host}:{port}")
    print("ORDER PLACEMENT: NOT PERFORMED")
    print("LIVE TRADING: DISABLED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
