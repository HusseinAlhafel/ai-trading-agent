#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/ibkr-clientportal"
ZIP="${ROOT}/clientportal.gw.zip"
URL="https://download2.interactivebrokers.com/portal/clientportal.gw.zip"
JRE_DIR="${ROOT}/jre11"

mkdir -p "$ROOT"

# IBKR Client Portal Gateway requires Java 11. Prefer an already-installed Java 11,
# otherwise install a private Temurin 11 JRE so the Codespace does not depend on
# the devcontainer feature having been applied successfully.
JAVA_BIN="$(command -v java || true)"
JAVA_OK=0
if [ -n "$JAVA_BIN" ]; then
  JAVA_MAJOR="$("$JAVA_BIN" -version 2>&1 | awk -F'[\".]' '/version/ {print $2; exit}')"
  [ "${JAVA_MAJOR:-0}" = "11" ] && JAVA_OK=1
fi

if [ "$JAVA_OK" -ne 1 ]; then
  echo "Java 11 not available; installing a private Temurin 11 JRE..."
  ARCH="$(uname -m)"
  case "$ARCH" in
    x86_64) ADOPTIUM_ARCH="x64" ;;
    aarch64|arm64) ADOPTIUM_ARCH="aarch64" ;;
    *) echo "Unsupported CPU architecture: $ARCH"; exit 1 ;;
  esac
  TMP="${ROOT}/temurin11.tar.gz"
  rm -rf "$JRE_DIR" "$TMP"
  curl -fsSL "https://api.adoptium.net/v3/binary/latest/11/ga/linux/${ADOPTIUM_ARCH}/jre/hotspot/normal/eclipse" -o "$TMP"
  mkdir -p "$JRE_DIR"
  tar -xzf "$TMP" -C "$JRE_DIR" --strip-components=1
  rm -f "$TMP"
  JAVA_BIN="$JRE_DIR/bin/java"
fi

JAVA_MAJOR="$("$JAVA_BIN" -version 2>&1 | awk -F'[\".]' '/version/ {print $2; exit}')"
if [ "${JAVA_MAJOR:-0}" != "11" ]; then
  echo "IBKR Gateway setup requires Java 11; detected Java ${JAVA_MAJOR:-unknown}."
  exit 1
fi
printf '%s\n' "$(dirname "$(dirname "$JAVA_BIN")")" > "$ROOT/java_home"

find_gateway_home() {
  find "$ROOT" -type f -path '*/bin/run.sh' -print -quit
}

RUN_SH="$(find_gateway_home || true)"
if [ -z "$RUN_SH" ]; then
  echo "Installing the current official IBKR Client Portal Gateway..."
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

GATEWAY_HOME="$(dirname "$(dirname "$RUN_SH")")"
chmod +x "$GATEWAY_HOME/bin/run.sh"
printf '%s\n' "$GATEWAY_HOME" > "$ROOT/gateway_home"

python3 -m pip install -e '.[ibkr]' --break-system-packages
echo "IBKR Paper Gateway prepared at $GATEWAY_HOME."
echo "Java 11 ready at $(dirname "$(dirname "$JAVA_BIN")")."
echo "No credentials or 2FA codes were stored."
