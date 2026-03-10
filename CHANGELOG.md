# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-25

### Added
- Project structure with modular architecture (src/, web/, scripts/)
- Platform detection: auto-detects Raspberry Pi vs local development (Windows/Mac)
- Mock hardware implementations for local testing without Pi hardware
- Hardware modules: KERN PCB 2000-1 scale (USB serial), RPi Camera Module 3, BME280 sensor (I2C)
- Camera analysis: label detection (edge detection) and contamination detection (brightness analysis)
- SAP Digital Manufacturing (DM) integration: posts inspection results to Data Collection API
- SAP Asset Performance Management (APM) integration: posts sensor indicators and contamination alerts
- OAuth2 Client Credentials token management with caching for SAP APIs
- Inspection engine: orchestrates weight check, label detection, contamination check, SAP reporting
- Flask web dashboard with live data (auto-refresh every 3s via REST API polling)
- Dashboard displays: scale status, environment data, last inspection, SAP DM/APM transmission status, network status
- WiFi management via NetworkManager/nmcli (Pi only)
- Access Point mode: auto-starts hotspot when no WiFi is available, captive portal for WiFi configuration
- WiFi configuration web page: scan, select, connect (Pi only)
- GitHub Actions workflow for auto-deployment to Pi on push to main
- Startup script for systemd service
- SAP API connectivity test script
- CLAUDE.md documentation in every folder
- Central configuration with .env support for secrets
