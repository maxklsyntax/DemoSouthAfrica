# src/

Application source code. Run via `python -m src.main` from project root.

## Module Map

| Module | Responsibility |
|---|---|
| `main.py` | Entry point: init hardware, start web server, run inspection loop |
| `platform_detect.py` | Detect Pi vs local dev, expose `IS_RASPBERRY_PI` and `FEATURES` dict |
| `config/` | Central settings, .env loading |
| `hardware/` | Scale, camera, sensor abstraction + mock implementations |
| `inspection/` | Inspection business logic |
| `sap/` | SAP DM and APM REST API clients |
| `network/` | WiFi scanning, connecting, AP mode (Pi only) |

## Import Convention

All imports use the `src.` prefix: `from src.config import settings`

## Shared State

`main.py` owns the `app_state` dict which is passed to the Flask app and updated by the inspection loop and SAP clients. The web API reads from it.
