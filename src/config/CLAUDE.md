# src/config/

Central configuration module.

## settings.py

- Loads `.env` from project root via `python-dotenv`
- All hardware settings: serial port, baudrate, I2C address
- Inspection tolerances: weight range (150–260g), label thresholds, contamination thresholds
- SAP credentials via `os.getenv()`: DM (OAuth2) and APM (API key or OAuth2)
- Timing: poll interval, sensor report interval, stabilization delay
- Web server: host, port
- AP mode: SSID, password

## Adding New Config

Add new values to `settings.py` with sensible defaults. Use `os.getenv()` for anything secret or environment-specific.
