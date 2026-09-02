#!/usr/bin/env python3
"""Verify the local IBKR Client Portal Gateway session is authenticated as Paper.

This script never accepts credentials and never targets a live endpoint.
"""
import json
import sys
import urllib.request
import urllib.error

BASE = "https://localhost:5000/v1/api"


def post(path):
    req = urllib.request.Request(BASE + path, method="POST")
    req.add_header("Accept", "*/*")
    with urllib.request.urlopen(req, context=__import__("ssl")._create_unverified_context(), timeout=10) as r:
        return json.loads(r.read().decode())


def get(path):
    req = urllib.request.Request(BASE + path, method="GET")
    req.add_header("Accept", "*/*")
    with urllib.request.urlopen(req, context=__import__("ssl")._create_unverified_context(), timeout=10) as r:
        return json.loads(r.read().decode())


def main():
    try:
        status = post("/iserver/auth/status")
        validation = get("/sso/validate")
    except Exception as exc:
        print(f"IBKR_PAPER_STATUS=ERROR: {exc}")
        return 2

    # CPGW returns either the documented success envelope or direct fields depending on version.
    value = status.get("success", {}).get("value", status.get("success", status))
    connected = bool(value.get("connected"))
    authenticated = bool(value.get("authenticated"))
    established = bool(value.get("established"))
    login_type = validation.get("LOGIN_TYPE", validation.get("loginType"))
    paper_verified = login_type == 2

    result = {
        "connected": connected,
        "authenticated": authenticated,
        "established": established,
        "paper_verified": paper_verified,
        "login_type": login_type,
        "real_orders_enabled": False,
    }
    print(json.dumps(result, indent=2))

    if not (connected and authenticated and established and paper_verified):
        print("IBKR_PAPER_STATUS=NOT_READY")
        return 1

    print("IBKR_PAPER_STATUS=READY")
    return 0


if __name__ == "__main__":
    sys.exit(main())
