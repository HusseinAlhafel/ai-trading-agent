#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/ibkr-clientportal"
ZIP="${ROOT}/clientportal.gw.zip"
URL="https://download2.interactivebrokers.com/portal/clientportal.gw.zip"

mkdir -p "$ROOT"

if [ ! -f "$ROOT/bin/run.sh" ]; then
  echo "Downloading official IBKR Client Portal Gateway..."
  curl -fsSL "$URL" -o "$ZIP"
  rm -rf "$ROOT/dist" "$ROOT/build" "$ROOT/bin" "$ROOT/root"
  unzip -q "$ZIP" -d "$ROOT"
  rm -f "$ZIP"
fi

chmod +x "$ROOT/bin/run.sh"
python -m pip install -e '.[ibkr]'
echo "IBKR Paper Gateway prepared. No credentials were stored."
