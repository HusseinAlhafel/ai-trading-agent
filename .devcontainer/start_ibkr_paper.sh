#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/ibkr-clientportal"
LOG="${ROOT}/gateway.log"
HOME_FILE="${ROOT}/gateway_home"

if [ ! -s "$HOME_FILE" ]; then
  echo "IBKR Paper Gateway is not installed yet. Rebuild the Codespace container once."
  exit 0
fi

GATEWAY_HOME="$(cat "$HOME_FILE")"
RUN_SH="$GATEWAY_HOME/bin/run.sh"
CONF="$GATEWAY_HOME/root/conf.yaml"

if [ ! -x "$RUN_SH" ] || [ ! -f "$CONF" ]; then
  echo "IBKR Paper Gateway installation is incomplete. Run setup_ibkr_paper.sh again."
  exit 1
fi

if pgrep -f "$RUN_SH" >/dev/null 2>&1; then
  echo "IBKR Client Portal Gateway is already running."
  exit 0
fi

nohup bash "$RUN_SH" "$CONF" >"$LOG" 2>&1 &
PID=$!
echo "$PID" > "$ROOT/gateway.pid"
sleep 2

if ! kill -0 "$PID" >/dev/null 2>&1; then
  echo "IBKR Client Portal Gateway exited during startup. Check: $LOG"
  tail -n 40 "$LOG" || true
  exit 1
fi

echo "IBKR Paper Client Portal Gateway started on https://localhost:5000"
echo "Open the forwarded port 5000 and log in manually."
echo "Credentials and 2FA are never stored or automated."
