# scripts/

Utility and startup scripts.

- `pi_setup.sh` — One-command Pi provisioning: creates venv, installs deps, sets up systemd service + auto-update timer (git pull every minute). Run with `sudo ./scripts/pi_setup.sh`.
- `start.sh` — Manual startup script: activates venv if present, runs `python -m src.main`.
- `test_sap_connection.py` — Standalone SAP API connectivity test. Posts test data to DM + APM, prints success/failure. No hardware required.
