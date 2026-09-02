#!/usr/bin/env python3
"""Fail-closed readiness check for the IBKR Paper Client Portal session.

The check never submits an order and never accepts credentials. It reports READY
only when the local Client Portal Gateway is authenticated, established, and
explicitly reports LOGIN_TYPE=2 (Paper).
"""
from __future__ import annotations

import json
import ssl
import sys
import urllib.error
import urllib.request

BASE = "https://localhost:5000/v1/api"
SSL = ssl._create_unverified_context()


def request(path: str, method: str) -> dict:
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Accept", "*/*")
    with urllib.request.urlopen(req, context=SSL, timeout=10) as response:
        return json.loads(response.read().decode())


def main() -> int:
    try:
        auth = request("/iserver/auth/status", "POST")
        validation = request("/sso/validate", "GET")
    except (OSError, ValueError, urllib.error.URLError) as exc:
        print(f"IBKR_PAPER_READY=NO")
        print(f"BLOCKER=Gateway unavailable or unauthenticated: {exc}")
        return 2

    value = auth.get("success", {}).get("value", auth.get("success", auth))
    connected = bool(value.get("connected"))
    authenticated = bool(value.get("authenticated"))
    established = bool(value.get("established"))
    login_type = validation.get("LOGIN_TYPE", validation.get("loginType"))
    paper = login_type == 2

    result = {
        "gateway": "https://localhost:5000",
        "connected": connected,
        "authenticated": authenticated,
        "established": established,
        "login_type": login_type,
        "paper_verified": paper,
        "real_orders_enabled": False,
    }
    print(json.dumps(result, indent=2))

    if connected and authenticated and established and paper:
        print("IBKR_PAPER_READY=YES")
        return 0

    print("IBKR_PAPER_READY=NO")
    if not paper:
        print("BLOCKER=Paper session was not verified (LOGIN_TYPE must be 2).")
    elif not authenticated:
        print("BLOCKER=IBKR session is not authenticated; manual login/2FA is required.")
    elif not established:
        print("BLOCKER=IBKR session is not established yet.")
    else:
        print("BLOCKER=IBKR Gateway connection is not confirmed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
