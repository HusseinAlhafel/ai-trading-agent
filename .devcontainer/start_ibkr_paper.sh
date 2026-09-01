#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/ibkr-clientportal"
LOG="${ROOT}/gateway.log"

if [ ! -x "$ROOT/bin/run.sh" ]; then
  echo "IBKR Paper Gateway is not installed yet. Rebuild the Codespace container once."
  exit 0
fi

if pgrep -f 'clientportal.*run.sh|clientportal.gw' >/dev/null 2>&1; then
  echo "IBKR Client Portal Gateway is already running."
  exit 0
fi

nohup bash "$ROOT/bin/run.sh" "$ROOT/root/conf.yaml" >"$LOG" 2>&1 &
echo "IBKR Paper Client Portal Gateway started on https://localhost:5000"
echo "Authenticate manually in the forwarded Codespace port; credentials and 2FA are never stored."
