"""Traffic meter: draggable, semi-transparent network speed widget (Windows 11 / Ubuntu)."""
import json, re, sys, time
from pathlib import Path
import psutil
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QAction
from PySide6.QtWidgets import QApplication, QWidget, QMenu

CFG = Path.home() / ".traffic_meter.json"
VPN_RE = re.compile(r"^(tun|tap|wg|utun|ppp|nordlynx|proton|mullvad|tailscale|wintun|zt)|vpn|wireguard|openvpn|tap-windows|wintun|nord|proton|mullvad", re.I)
SKIP_RE = re.compile(r"^(lo$|loopback|docker|veth|br-|virbr|vmnet|vboxnet|vethernet|isatap|teredo|pseudo)|loopback|vethernet|virtualbox|vmware", re.I)
COLORS = {"VPN": "#4ade80", "Direct": "#f87171"}
OPACITIES = [0.35, 0.5, 0.65, 0.8, 1.0]


def fmt(bps):
    for unit in ("B/s", "KB/s", "MB/s", "GB/s"):
        if bps < 1024 or unit == "GB/s":
            return f"{bps:6.1f} {unit}" if unit != "B/s" else f"{bps:6.0f} {unit}"
        bps /= 1024


def sample():
    """Return cumulative (down, up) bytes for VPN and direct interfaces."""
    stats = psutil.net_if_stats()
    io = psutil.net_io_counters(pernic=True)
    t = {"VPN": [0, 0], "Direct": [0, 0]}
    for name, c in io.items():
        st = stats.get(name)
        if not st or not st.isup or SKIP_RE.search(name):
            continue
        k = "VPN" if VPN_RE.search(name) else "Direct"
        t[k][0] += c.bytes_recv
        t[k][1] += c.bytes_sent
    return t


class Meter(QWidget):
    def __init__(self):
        super().__init__()
        self.cfg = {"opacity": 0.8, "pos": None}
        try:
            self.cfg.update(json.loads(CFG.read_text()))
        except Exception:
            pass
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(self.cfg["opacity"])
        self.resize(230, 110)
        if self.cfg["pos"]:
            self.move(*self.cfg["pos"])
        self.prev, self.prev_t = sample(), time.monotonic()
        self.rates = {"VPN": (0, 0), "Direct": (0, 0)}
        self.timer = QTimer(self, timeout=self.tick, interval=1000)
        self.timer.start()

    def tick(self):
        cur, now = sample(), time.monotonic()
        dt = max(now - self.prev_t, 1e-3)
        r = {k: [max(0, (cur[k][i] - self.prev[k][i]) / dt) for i in (0, 1)] for k in cur}
        # While a tunnel is up, its encrypted packets also cross the physical NIC;
        # subtract tunnel rate so "Direct" approximates traffic outside the VPN.
        for i in (0, 1):
            r["Direct"][i] = max(0, r["Direct"][i] - r["VPN"][i])
        self.rates, self.prev, self.prev_t = r, cur, now
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(20, 22, 28, 200)); p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 12, 12)
        p.setFont(QFont("monospace", 9))
        y = 24
        for k in ("VPN", "Direct"):
            p.setPen(QColor(COLORS[k]))
            p.drawText(14, y, k)
            p.setPen(QColor("#e5e7eb"))
            p.drawText(70, y, f"↓{fmt(self.rates[k][0])}")
            p.drawText(70, y + 18, f"↑{fmt(self.rates[k][1])}")
            y += 46

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            h = self.windowHandle()
            if h and h.startSystemMove():  # Wayland-safe drag
                return
            self._off = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and hasattr(self, "_off"):
            self.move(e.globalPosition().toPoint() - self._off)

    def mouseReleaseEvent(self, e):
        self.save()

    def save(self):
        self.cfg["pos"] = [self.x(), self.y()]
        try:
            CFG.write_text(json.dumps(self.cfg))
        except Exception:
            pass

    def contextMenuEvent(self, e):
        m = QMenu(self)
        om = m.addMenu("Opacity")
        for o in OPACITIES:
            a = QAction(f"{int(o*100)}%", om, checkable=True, checked=abs(o - self.cfg["opacity"]) < .01)
            a.triggered.connect(lambda _=False, o=o: self.set_opacity(o))
            om.addAction(a)
        m.addAction("Quit", QApplication.quit)
        m.exec(e.globalPos())

    def set_opacity(self, o):
        self.cfg["opacity"] = o
        self.setWindowOpacity(o)
        self.save()

    def closeEvent(self, e):
        self.save()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Meter(); w.show()
    sys.exit(app.exec())
