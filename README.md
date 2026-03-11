# Bottle Inspection Demo — Raspberry Pi

## Overview

Demo system for automated quality inspection of small 0.1L glass bottles.
The system checks label presence (camera), measures weight (scale), and detects contamination (brightness analysis). Label and weight results are sent to SAP Digital Manufacturing (DM) via the Production Process API. Includes a live web dashboard with camera preview and WiFi AP mode for field setup.

Runs on Raspberry Pi 4 **and** as Plan B on a laptop with webcam.

---

## Hardware

| Component | Model | Connection |
|---|---|---|
| Computer | Raspberry Pi 4 Model B (min. 2GB) | — |
| Scale | KERN PCB 2000-1 (2kg / 0.1g) | USB-B → USB-A |
| Camera | Raspberry Pi Camera Module 3 | CSI port |
| Lighting | Ring light (optional) | USB |
| OS | Raspberry Pi OS (64-bit, Bookworm) | — |

**Laptop mode:** Scale is simulated (random weight 150–260g), webcam (built-in or USB) is auto-detected.

---

## Quick Start

### On the Raspberry Pi

```bash
git clone https://github.com/maxklsyntax/DemoSouthAfrica.git
cd DemoSouthAfrica
chmod +x scripts/pi_setup.sh
sudo ./scripts/pi_setup.sh
```

The setup script installs everything automatically (venv, dependencies, systemd service, auto-update from GitHub every minute).

### On a Laptop (Plan B)

```bash
git clone https://github.com/maxklsyntax/DemoSouthAfrica.git
cd DemoSouthAfrica
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

Open dashboard: http://localhost:8080

---

## SAP Credentials

```bash
cp .env.example .env
nano .env   # Fill in credentials
```

See `.env.example` for all required variables.

---

## Project Structure

```
src/
├── main.py              # Entry point: platform detection, hardware init, inspection loop
├── platform_detect.py   # Detects Pi vs laptop, sets feature flags
├── config/settings.py   # All thresholds and configuration, loads .env
├── hardware/            # Hardware abstraction (scale, camera + mocks + webcam)
├── inspection/engine.py # Orchestrates the inspection cycle
├── sap/                 # SAP DM API client with OAuth2 auth
└── network/             # WiFi management + AP mode (Pi only)

web/
├── app.py               # Flask app factory
├── api/routes.py        # REST API for dashboard
├── templates/           # Jinja2 templates (dashboard + WiFi config)
└── static/              # CSS + JS (live preview, auto-refresh)

scripts/
├── pi_setup.sh          # Pi provisioning (venv, systemd, auto-update)
├── start.sh             # Manual start script
└── test_sap_connection.py  # SAP API connectivity test

docs/
└── setup-guide.md/pdf   # Detailed step-by-step setup guide
```

---

## Data Flow

```
Camera (label bool)  → Check Label button  → SAP DM (Production Process)
Scale  (weight)      → Check Weight button → SAP DM (Production Process)
All results          → app_state           → Web Dashboard
```

---

## Dashboard Controls

| Button | Action |
|---|---|
| **Check Label** | Captures image, detects label, sends result to SAP DM |
| **Check Weight** | Reads weight (or simulates), sends result to SAP DM |

Camera selector dropdown allows switching between available cameras.

---

## WiFi Configuration (Field Deployment)

When the Pi finds no known WiFi network, it automatically starts a hotspot:

1. Connect to WiFi `BottleInspection-Setup` (password: `inspect123`)
2. Browser: `http://10.42.0.1:8080/wifi`
3. Select WiFi + enter password → Pi connects automatically

---

## Auto-Update

The Pi checks **every minute** for new commits on GitHub.
On changes: `git pull` → install dependencies → restart service.

Workflow: Edit code on laptop → `git push` → Pi updates automatically.

---

## Useful Commands

```bash
# Manage service
sudo systemctl start|stop|restart|status bottle-inspection

# View live logs
sudo journalctl -u bottle-inspection -f

# Check auto-update timer
sudo systemctl status bottle-inspection-update.timer

# Manual update
cd ~/DemoSouthAfrica && git pull origin main

# Test SAP connection
source .venv/bin/activate && python scripts/test_sap_connection.py

# Check scale port
ls /dev/ttyUSB*

# Test camera (Pi)
rpicam-still -o test.jpg
```

---

## Documentation

- **[Setup Guide (PDF)](docs/setup-guide.pdf)** — Detailed step-by-step guide
- **CLAUDE.md** — Technical reference for development
