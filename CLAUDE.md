# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Raspberry Pi 4 demo system for automated bottle quality inspection. Checks label presence (camera), weight (KERN scale), and contamination (brightness analysis). Sends label status and weight to SAP Digital Manufacturing (DM) and contamination alerts to SAP Asset Performance Management (APM) via REST APIs. Includes a live web dashboard with camera preview and WiFi AP mode for field setup. Also runs on a laptop with webcam as Plan B.

## Commands

```bash
# Install dependencies (local dev — Pi-only packages are commented out)
pip install -r requirements.txt

# Run the application
python -m src.main

# Test SAP API connectivity (no hardware needed)
python scripts/test_sap_connection.py

# On Pi: one-time setup (venv, systemd service, auto-update timer)
sudo ./scripts/pi_setup.sh

# On Pi: manage systemd service
sudo systemctl start|stop|restart|status bottle-inspection
sudo journalctl -u bottle-inspection -f
```

## Architecture

```
src/
├── main.py              # Entry point: platform detection, hardware init, inspection loop
├── platform_detect.py   # Detects Pi vs local dev, sets feature flags
├── config/settings.py   # All config values, loads secrets from .env
├── hardware/            # Hardware abstraction (scale, camera + mocks + webcam)
├── inspection/engine.py # Orchestrates full inspection cycle
├── sap/                 # SAP DM + APM API clients with shared OAuth2 auth
└── network/             # WiFi management + AP mode (Pi only, via nmcli)

web/
├── app.py               # Flask app factory
├── api/routes.py        # JSON REST API for dashboard + camera
├── templates/           # Jinja2 templates (dashboard + wifi config)
└── static/              # CSS + JS (camera preview 1fps, data refresh 3s)

scripts/
├── pi_setup.sh          # Pi provisioning: venv, systemd, auto-update timer
├── start.sh             # Manual start script
└── test_sap_connection.py

docs/
└── setup-guide.md/pdf   # Detailed step-by-step setup guide
```

## Key Design Decisions

- **Platform detection**: `src/platform_detect.py` auto-detects Pi vs local. On non-Pi, WebcamCamera (OpenCV) is tried first, then MockCamera as fallback.
- **Optional hardware**: Inspection engine accepts `scale=None` or `camera=None`. Each check is skipped if its hardware is unavailable. System works standalone with just camera or just scale.
- **Config**: Thresholds in `src/config/settings.py`, secrets in `.env` (never committed).
- **SAP clients**: DM client sends label (bool) + weight. APM client sends contamination alerts only. Shared `sap/auth.py` for OAuth2 token caching.
- **Web dashboard**: Flask on port 8080. Live camera preview (1fps), data polling (3s). Manual "Run Inspection" button. Camera selector dropdown for multiple cameras.
- **AP mode**: On Pi boot without WiFi, starts NetworkManager hotspot. User configures WiFi via web UI at `http://10.42.0.1:8080/wifi`, then AP stops.
- **Auto-update**: Pi checks GitHub every minute via systemd timer. On new commits: git pull → pip install → service restart.

## Data Flow

- **Camera** (label bool) -> `inspection/engine.py` -> `sap/dm_client.py` -> **SAP DM** (Data Collection)
- **Scale** (weight) -> `inspection/engine.py` -> `sap/dm_client.py` -> **SAP DM** (Data Collection)
- **Camera** (contamination) -> `inspection/engine.py` -> `sap/apm_client.py` -> **SAP APM** (Alert)
- All results -> `app_state` dict -> `web/api/routes.py` -> **Dashboard**

## Conventions

- All code, comments, and documentation in English
- Versioning: semver (current: 0.2.0), tracked in CHANGELOG.md
- Git branch: `main` (stable, Pi auto-pulls every minute)
- Tolerances and thresholds in `config/settings.py`, never hardcoded in modules
- Ring light must be active before camera analysis starts
- Tare scale before each measurement cycle (KCP 't' command)
- SAP API endpoint paths must be verified against tenant-specific API docs
