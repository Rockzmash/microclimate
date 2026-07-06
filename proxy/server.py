"""
Microclimate Govee Proxy
- Discovers Govee lights via UDP multicast
- Exposes HTTP API for the browser visualizer
- Forwards commands to lights via UDP
"""

import json
import os
import socket
import time
import threading
from dataclasses import dataclass, field
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web")

app = Flask(__name__, static_folder=WEB_DIR)
CORS(app)


@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")

# --- Govee LAN Protocol Constants ---
MCAST_GROUP = "239.255.255.250"
MCAST_PORT = 4001
CONTROL_PORT = 4003
SCAN_MSG = json.dumps({"msg": {"cmd": "scan", "data": {"account_topic": "reserve"}}})

# --- Device Registry ---
@dataclass
class GoveeDevice:
    ip: str
    name: str = "Unknown"
    model: str = "Unknown"
    mac: str = ""
    last_seen: float = field(default_factory=time.time)

devices: dict[str, GoveeDevice] = {}  # ip -> device
lock = threading.Lock()


def discover():
    """Send UDP multicast scan and collect responses."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(3)

    sock.sendto(SCAN_MSG.encode(), (MCAST_GROUP, MCAST_PORT))

    try:
        while True:
            data, addr = sock.recvfrom(4096)
            try:
                msg = json.loads(data)
                device_info = msg.get("msg", {}).get("data", {})
                ip = addr[0]
                with lock:
                    devices[ip] = GoveeDevice(
                        ip=ip,
                        name=device_info.get("deviceName", "Unknown"),
                        model=device_info.get("sku", "Unknown"),
                        mac=device_info.get("device", ""),
                        last_seen=time.time(),
                    )
            except json.JSONDecodeError:
                pass
    except socket.timeout:
        pass
    finally:
        sock.close()


def send_command(device_ip: str, command: dict) -> bool:
    """Send a UDP command to a Govee device on port 4003."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        payload = json.dumps(command)
        sock.sendto(payload.encode(), (device_ip, CONTROL_PORT))
        sock.close()
        return True
    except Exception as e:
        print(f"Error sending to {device_ip}: {e}")
        return False


# --- HTTP API ---

@app.route("/api/lights", methods=["GET"])
def get_lights():
    """Discover and return all Govee lights on the LAN."""
    discover()
    with lock:
        result = [
            {
                "ip": d.ip,
                "name": d.name,
                "model": d.model,
                "mac": d.mac,
                "last_seen": d.last_seen,
            }
            for d in devices.values()
        ]
    return jsonify({"lights": result})


@app.route("/api/lights/<ip>", methods=["POST"])
def control_light(ip: str):
    """
    Control a Govee light.
    Body: {"power": true/false, "r": 255, "g": 0, "b": 0, "brightness": 100}
    All fields optional — only sends what you provide.
    """
    data = request.get_json() or {}

    commands = []

    # Power
    if "power" in data:
        commands.append(
            {"msg": {"cmd": "turn", "data": {"value": 1 if data["power"] else 0}}}
        )

    # Color + brightness
    if any(k in data for k in ("r", "g", "b", "brightness")):
        color_data = {"color": {}, "colorTemInKelvin": 0}
        if "r" in data and "g" in data and "b" in data:
            color_data["color"]["r"] = int(data["r"])
            color_data["color"]["g"] = int(data["g"])
            color_data["color"]["b"] = int(data["b"])
        if "brightness" in data:
            # brightness is a top-level field in colorwc, not nested inside color
            color_data["brightness"] = int(data["brightness"])
        commands.append({"msg": {"cmd": "colorwc", "data": color_data}})

    if not commands:
        return jsonify({"error": "No valid fields provided"}), 400

    results = []
    for cmd in commands:
        ok = send_command(ip, cmd)
        results.append({"command": cmd["msg"]["cmd"], "success": ok})

    return jsonify({"results": results})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("🔮 Microclimate Proxy starting on http://localhost:8770")
    print("   Endpoints:")
    print("   GET  /api/lights       — discover Govee devices")
    print("   POST /api/lights/<ip>  — control a light")
    print("   GET  /health           — health check")
    app.run(host="0.0.0.0", port=8770, debug=False)  # 8770: distinct from Sobo's 8765
