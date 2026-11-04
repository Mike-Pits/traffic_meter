#!/usr/bin/env bash
# One-time setup: creates venv, installs deps, adds "Traffic meter" to the app grid.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install -q -r "$ROOT/requirements.txt"
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/traffic-meter.desktop <<DESK
[Desktop Entry]
Type=Application
Name=Traffic meter
Comment=Draggable network speed widget
Exec=$ROOT/.venv/bin/python $ROOT/traffic_meter.py
Path=$ROOT
Icon=network-transmit-receive
Terminal=false
Categories=Network;Monitor;
DESK
chmod +x ~/.local/share/applications/traffic-meter.desktop
echo "Done. Open Activities and search 'Traffic meter'; right-click to add to favorites."
