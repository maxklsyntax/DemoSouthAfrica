# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-10

### Added
- Live camera preview in web dashboard (1fps refresh)
- Manual "Run Inspection" button in dashboard
- Webcam support for local development (OpenCV VideoCapture)
- Camera selector dropdown (switch between multiple cameras)
- Camera list API endpoint (`/api/camera/list`)
- Camera select API endpoint (`POST /api/camera/select`)
- Camera snapshot API endpoint (`/api/camera/snapshot`)
- Standalone mode: system works with camera only, scale only, or both
- Pi self-update: systemd timer checks GitHub every minute, auto-restarts on changes
- Setup script (`scripts/pi_setup.sh`) for one-command Pi provisioning
- Detailed setup guide (`docs/setup-guide.md` + PDF)

### Changed
- Inspection engine accepts optional hardware (scale=None or camera=None)
- Dashboard layout: full-width camera card with live preview
- Deploy strategy: replaced GitHub Actions SSH workflow with Pi-side git pull timer

### Removed
- BME280 environment sensor (hardware, mock, config, API endpoints, dashboard card)
- `post_sensor_data()` from APM client (only contamination alerts remain)
- GitHub Actions SSH deploy workflow (replaced by Pi self-update)

## [0.1.0] - 2026-02-25

### Added
- Project structure with modular architecture (src/, web/, scripts/)
- Platform detection: auto-detects Raspberry Pi vs local development
- Mock hardware implementations for local testing without Pi hardware
- Hardware modules: KERN PCB 2000-1 scale (USB serial), RPi Camera Module 3
- Camera analysis: label detection (edge detection) and contamination detection (brightness analysis)
- SAP Digital Manufacturing (DM) integration: posts inspection results to Data Collection API
- SAP Asset Performance Management (APM) integration: posts contamination alerts
- OAuth2 Client Credentials token management with caching for SAP APIs
- Inspection engine: orchestrates weight check, label detection, contamination check, SAP reporting
- Flask web dashboard with live data (auto-refresh every 3s via REST API polling)
- WiFi management via NetworkManager/nmcli (Pi only)
- Access Point mode: auto-starts hotspot when no WiFi, captive portal for configuration
- Startup script for systemd service
- SAP API connectivity test script
- Central configuration with .env support for secrets
