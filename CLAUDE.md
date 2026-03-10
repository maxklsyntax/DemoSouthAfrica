# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Raspberry Pi 4 demo system for automated bottle quality inspection. Checks label presence (camera), weight (KERN scale), contamination (brightness analysis), and environment data (BME280). Sends results to SAP Digital Manufacturing (DM) and SAP Asset Performance Management (APM) via REST APIs. Includes a web dashboard and WiFi AP mode for field setup.

## Commands

```bash
# Install dependencies (local dev — Pi-only packages are commented out)
pip install -r requirements.txt

# Run the application
python -m src.main

# Test SAP API connectivity (no hardware needed)
python scripts/test_sap_connection.py

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
├── hardware/            # Hardware abstraction (scale, camera, sensor + mocks)
├── inspection/engine.py # Orchestrates full inspection cycle
├── sap/                 # SAP DM + APM API clients with shared OAuth2 auth
└── network/             # WiFi management + AP mode (Pi only, via nmcli)

web/
├── app.py               # Flask app factory
├── api/routes.py        # JSON REST API for dashboard
├── templates/           # Jinja2 templates (dashboard + wifi config)
└── static/              # CSS + JS (dashboard auto-refresh every 3s)
```

## Key Design Decisions

- **Platform detection**: `src/platform_detect.py` auto-detects Pi vs local. On non-Pi, mock hardware classes provide fake data so the full system runs locally.
- **Config**: Thresholds in `src/config/settings.py`, secrets in `.env` (never committed).
- **SAP clients**: Separate modules for DM and APM with shared `sap/auth.py` (OAuth2 token caching).
- **Web dashboard**: Flask on port 8080, JS polls `/api/*` every 3s for live data.
- **AP mode**: On Pi boot without WiFi, starts NetworkManager hotspot. User configures WiFi via web UI, then AP stops.

## Data Flow

- **Scale** -> `inspection/engine.py` -> `sap/dm_client.py` -> **SAP DM** (Data Collection)
- **Camera** (contamination) -> `inspection/engine.py` -> `sap/apm_client.py` -> **SAP APM** (Alert)
- **BME280** -> `main.py` (timer) -> `sap/apm_client.py` -> **SAP APM** (Indicators)
- All results -> `app_state` dict -> `web/api/routes.py` -> **Dashboard**

## Conventions

- All code, comments, and documentation in English
- Versioning: semver (current: 0.1.0), tracked in CHANGELOG.md
- Git branches: `dev` (development), `main` (stable, auto-deploys to Pi)
- Tolerances and thresholds in `config/settings.py`, never hardcoded in modules
- Ring light must be active before camera analysis starts
- Tare scale before each measurement cycle (KCP 't' command)
- SAP API endpoint paths must be verified against tenant-specific API docs
