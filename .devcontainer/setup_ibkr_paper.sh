#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/ibkr-clientportal"
ZIP="${ROOT}/clientportal.gw.zip"
URL="https://download2.interactivebrokers.com/portal/clientportal.gw.zip"

mkdir -p "$ROOT"

if ! command -v java >/dev/null 2>&1; then
  echo "Java 17+ is required for the IBKR Client Portal Gateway."
  exit 1
fi

# The official archive is downloaded directly from Interactive Brokers.
# Authentication is intentionally never automated or stored.
if ! find "$ROOT" -type f -path '*/bin/run.sh' -print -quit | grep -q .; then
  echo "Downloading official IBKR Client Portal Gateway..."
  curl -fsSL "$URL" -o "$ZIP"
  rm -rf "$ROOT/dist" "$ROOT/build" "$ROOT/bin" "$ROOT/root" "$ROOT/clientportal.gw"
  unzip -q "$ZIP" -d "$ROOT"
  rm -f "$ZIP"
fi

RUN_SH="$(find "$ROOT" -type f -path '*/bin/run.sh' -print -quit)"
if [ -z "$RUN_SH" ]; then
  echo "Could not locate IBKR Client Portal Gateway bin/run.sh after extraction."
  exit 1
fi

GATEWAY_HOME="$(dirname "$(dirname "$RUN_SH")")"
chmod +x "$GATEWAY_HOME/bin/run.sh"
printf '%s\n' "$GATEWAY_HOME" > "$ROOT/gateway_home"

python -m pip install -e '.[ibkr]'
echo "IBKR Paper Gateway prepared at $GATEWAY_HOME."
echo "No credentials or 2FA codes were stored."
