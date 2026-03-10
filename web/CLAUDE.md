# web/

Flask web application — monitoring dashboard and WiFi configuration portal.

## app.py

Flask app factory: `create_app(app_state)`. Receives the shared `app_state` dict from `main.py`. Registers API blueprint and page routes.

## api/routes.py

JSON REST API (all `GET` except network connect):

| Endpoint | Description |
|---|---|
| `/api/status` | Overall system status |
| `/api/scale` | Current weight, tare, connected |
| `/api/sensor` | Temperature, humidity, pressure |
| `/api/inspection/latest` | Last inspection result |
| `/api/sap/dm/status` | Last SAP DM transmission |
| `/api/sap/apm/status` | Last SAP APM transmission |
| `/api/network` | WiFi/internet status |
| `/api/network/scan` | Scan WiFi (Pi only) |
| `POST /api/network/connect` | Connect to WiFi (Pi only) |

## Templates

- `base.html` — Layout with nav (dashboard + wifi link if Pi)
- `dashboard.html` — 6-card grid: scale, environment, inspection, network, SAP DM, SAP APM
- `wifi.html` — Scan, select, connect (Pi only)

## Static Assets

- `css/style.css` — Card-based responsive layout
- `js/dashboard.js` — Polls all `/api/*` endpoints every 3 seconds, updates DOM
