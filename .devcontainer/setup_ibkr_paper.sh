#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/ibkr-clientportal"
ZIP="${ROOT}/clientportal.gw.zip"
URL="https://download2.interactivebrokers.com/portal/clientportal.gw.zip"
CLASS='ibgroup/web/core/clientportal/gw/GatewayStart.class'

mkdir -p "$ROOT"

if ! command -v java >/dev/null 2>&1; then
  echo "Java is required for the IBKR Client Portal Gateway."
  exit 1
fi

JAVA_MAJOR="$(java -version 2>&1 | awk -F'[\".]' '/version/ {print $2; exit}')"
if [ "${JAVA_MAJOR:-0}" -gt 11 ]; then
  echo "IBKR Client Portal Gateway setup requires Java 11 in this Codespace."
  echo "Rebuild the container so the Java 11 feature is applied."
  exit 1
fi

find_gateway_home() {
  find "$ROOT" -type f -path '*/bin/run.sh' -print -quit
}

find_gateway_class() {
  local jar
  while IFS= read -r -d '' jar; do
    if jar tf "$jar" 2>/dev/null | grep -Fxq "$CLASS"; then
      return 0
    fi
  done < <(find "$ROOT" -type f -name '*.jar' -print0)
  return 1
}

RUN_SH="$(find_gateway_home || true)"
if [ -z "$RUN_SH" ] || ! find_gateway_class; then
  echo "Installing a fresh official IBKR Client Portal Gateway..."
  rm -rf "$ROOT/dist" "$ROOT/build" "$ROOT/bin" "$ROOT/root" "$ROOT/clientportal.gw"
  rm -f "$ZIP" "$ROOT/gateway_home"
  curl -fsSL "$URL" -o "$ZIP"
  unzip -q "$ZIP" -d "$ROOT"
  rm -f "$ZIP"
  RUN_SH="$(find_gateway_home || true)"
fi

if [ -z "$RUN_SH" ]; then
  echo "Could not locate IBKR Client Portal Gateway bin/run.sh after extraction."
  exit 1
fi

if ! find_gateway_class; then
  echo "IBKR Gateway archive is missing GatewayStart.class; installation was not accepted."
  exit 1
fi

GATEWAY_HOME="$(dirname "$(dirname "$RUN_SH")")"
chmod +x "$GATEWAY_HOME/bin/run.sh"
printf '%s\n' "$GATEWAY_HOME" > "$ROOT/gateway_home"

python -m pip install -e '.[ibkr]'
echo "IBKR Paper Gateway prepared at $GATEWAY_HOME."
echo "No credentials or 2FA codes were stored."
