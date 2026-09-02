"""Fail-closed readiness helper for IBKR Live manual-approval mode.

This script does not submit, modify, or cancel live orders.
"""
from __future__ import annotations

import os


def main() -> int:
    host = os.getenv("IBKR_HOST", "127.0.0.1")
    mode = os.getenv("TRADING_MODE", "live_manual_approval")
    print(f"IBKR HOST: {host}")
    print(f"TRADING MODE: {mode}")
    print("LIVE ORDER SUBMISSION: DISABLED")
    print("MANUAL APPROVAL: REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
