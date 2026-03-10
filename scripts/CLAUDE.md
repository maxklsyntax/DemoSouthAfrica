# scripts/

Utility and startup scripts.

- `start.sh` — Pi startup script: activates venv if present, runs `python -m src.main`. Used by the systemd service.
- `test_sap_connection.py` — Standalone SAP API connectivity test. Posts test data to DM + APM, prints success/failure. No hardware required.
