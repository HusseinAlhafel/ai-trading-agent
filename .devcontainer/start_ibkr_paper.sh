#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/ibkr-clientportal"
LOG="${ROOT}/gateway.log"
HOME_FILE="${ROOT}/gateway_home"
JAVA_HOME_FILE="${ROOT}/java_home"
SETUP="$(cd "$(dirname "$0")" && pwd)/setup_ibkr_paper.sh"

if [ ! -s "$HOME_FILE" ]; then
  echo "IBKR Paper Gateway is not prepared yet; running setup automatically..."
  bash "$SETUP"
fi

GATEWAY_HOME="$(cat "$HOME_FILE")"
RUN_SH="$GATEWAY_HOME/bin/run.sh"
CONF="$GATEWAY_HOME/root/conf.yaml"

if [ -s "$JAVA_HOME_FILE" ]; then
  export JAVA_HOME="$(cat "$JAVA_HOME_FILE")"
  export PATH="$JAVA_HOME/bin:$PATH"
fi

if ! command -v java >/dev/null 2>&1; then
  echo "Java 11 is not available. Run setup_ibkr_paper.sh first."
  exit 1
fi
JAVA_MAJOR="$(java -version 2>&1 | awk -F'[\".]' '/version/ {print $2; exit}')"
if [ "${JAVA_MAJOR:-0}" != "11" ]; then
  echo "IBKR Client Portal Gateway requires Java 11; detected Java ${JAVA_MAJOR:-unknown}."
  exit 1
fi

if [ ! -x "$RUN_SH" ] || [ ! -f "$CONF" ]; then
  echo "IBKR Paper Gateway installation is incomplete. Run setup_ibkr_paper.sh again."
  exit 1
fi

if curl -ksSf --max-time 2 https://localhost:5000/ >/dev/null 2>&1; then
  echo "IBKR Client Portal Gateway is already listening on https://localhost:5000"
  exit 0
fi

# IBKR's official run.sh uses relative paths (root/, dist/, build/lib/runtime/).
# It must therefore be launched with the gateway directory as the working directory.
rm -f "$ROOT/gateway.pid"
(
  cd "$GATEWAY_HOME"
  exec bash "$RUN_SH" "root/conf.yaml"
) >"$LOG" 2>&1 &
PID=$!
echo "$PID" > "$ROOT/gateway.pid"

READY=0
for _ in $(seq 1 30); do
  if curl -ksSf --max-time 2 https://localhost:5000/ >/dev/null 2>&1; then
    READY=1
    break
  fi
  if ! kill -0 "$PID" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if [ "$READY" -ne 1 ]; then
  echo "IBKR Client Portal Gateway did not become ready on https://localhost:5000."
  echo "Last gateway log lines:"
  tail -n 60 "$LOG" || true
  exit 1
fi

echo "IBKR Paper Client Portal Gateway is listening on https://localhost:5000"
echo "Authentication must be completed manually; credentials and 2FA are never stored or automated."
