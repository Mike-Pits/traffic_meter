# Traffic meter

A small, draggable, semi-transparent desktop widget that shows real-time network speed, split into **VPN** and **Direct** (non-VPN) traffic.

Built with Python, PySide6 (Qt) and psutil. Targets Windows 11 and Ubuntu (Wayland or X11).

## Features

- Frameless, translucent, always-on-top window; drag it anywhere (Wayland-safe system move)
- Live download/upload speed for VPN and Direct, auto-scaled (B/s, KB/s, MB/s, GB/s), refreshed every second
- VPN detected automatically by network interface name (tun, tap, wg, nordlynx, proton, mullvad, tailscale, wintun, etc.)
- Virtual adapters (loopback, Docker, VMware, VirtualBox, Hyper-V) are ignored
- Right-click menu: opacity (35-100%) and Quit
- Remembers position and opacity in `~/.traffic_meter.json`

## Install and run

```bash
pip install -r requirements.txt
python traffic_meter.py
```

On a minimal Ubuntu install you may need: `sudo apt install libegl1 libgl1 libxkbcommon0`.

## One-click launcher (start on click)

Run the installer once; afterwards launch "Traffic meter" like any app.

- **Windows 11:** double-click `launchers\windows_install.bat`, then search "Traffic meter" in Start (right-click to pin to taskbar).
- **Ubuntu:** `bash launchers/ubuntu_install.sh`, then search "Traffic meter" in Activities (right-click to add to favorites).

Nothing starts automatically at login.

## How "Direct" is calculated

While a VPN is connected, its encrypted packets also pass through the physical adapter. The widget subtracts the VPN rate from the physical rate, so Direct is an approximation of traffic outside the tunnel.

## Limitations

- Home network (192.168.*.*) traffic is not shown yet. Splitting it out needs packet capture (Npcap on Windows, libpcap/CAP_NET_RAW on Linux) and admin rights.
- On Wayland, the compositor may ignore always-on-top.
- Not yet tested on real Windows 11 / Ubuntu hardware.
- If your VPN adapter isn't recognised, add its name pattern to `VPN_RE` in `traffic_meter.py`.
