# Microclimate

Audio-reactive particle system that mirrors your room's ambience — and drives Govee smart lights in sync.

## How it works

```
🎤 Mic → Web Audio API (FFT analysis) ─┬→ p5.js particle system (visual)
                                        └→ Govee LAN proxy (lights)
```

- **Volume** → particle spawn rate + light brightness
- **Spectral centroid** (warm↔bright sounds) → hue shift, palette drift  
- **Spectral flux** (how fast sound changes) → turbulence, particle velocity
- **Bass energy** → "thump" particle bursts + light brightness spike

## Run

Double-click `run.bat` or:

```bash
cd proxy
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

Then open **http://localhost:8765** in Firefox.

## Controls

| Button | What |
|--------|------|
| 🎤 Mic | Toggle microphone on/off |
| 💡 Lights | Toggle Govee light sync |
| 🔍 Scan | Discover Govee lights on LAN |
| 🎨 Hue | Cycle color palette (cool/warm/green/purple/fire) |

## Govee lights

The proxy auto-discovers Govee devices on your LAN via UDP multicast (port 4001).
Lights must be on the same network. Control uses port 4003 — no cloud account needed.

If no Govee lights are found, the visualizer still works fine standalone.
