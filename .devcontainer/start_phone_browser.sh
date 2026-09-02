#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/ibkr-clientportal"
mkdir -p "$ROOT"

export DISPLAY=:99
export XDG_RUNTIME_DIR="${ROOT}/xdg-runtime"
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"

# Start a private virtual desktop inside the Codespace.
if ! pgrep -f 'Xvfb :99' >/dev/null 2>&1; then
  nohup Xvfb :99 -screen 0 1440x900x24 -ac >"$ROOT/xvfb.log" 2>&1 &
fi

sleep 1

# Expose that desktop through noVNC so it can be controlled from the phone.
if ! pgrep -f 'x11vnc.*5900' >/dev/null 2>&1; then
  nohup x11vnc -display :99 -forever -shared -localhost -rfbport 5900 -nopw >"$ROOT/x11vnc.log" 2>&1 &
fi

if ! pgrep -f 'novnc_proxy.*6080' >/dev/null 2>&1; then
  nohup /usr/share/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 >"$ROOT/novnc.log" 2>&1 &
fi

# Open IBKR Gateway in the browser running inside the same Codespace.
if ! pgrep -f '[c]hromium.*localhost:5000' >/dev/null 2>&1; then
  nohup chromium \
    --no-sandbox \
    --disable-dev-shm-usage \
    --disable-gpu \
    --no-first-run \
    --no-default-browser-check \
    --start-maximized \
    --ignore-certificate-errors \
    https://localhost:5000/ >"$ROOT/chromium.log" 2>&1 &
fi

echo "Phone browser desktop is available on http://localhost:6080 inside the Codespace."
echo "Forward Codespace port 6080 and open it from the phone."
