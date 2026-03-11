# web/

Flask web application — monitoring dashboard with live camera preview and WiFi configuration portal.

## app.py

Flask app factory: `create_app(app_state)`. Receives the shared `app_state` dict from `main.py`. Registers API blueprint and page routes.

## api/routes.py

JSON REST API:

| Endpoint | Description |
|---|---|
| `/api/status` | Overall system status |
| `/api/scale` | Current weight, tare, connected |
| `/api/inspection/latest` | Last inspection result |
| `/api/inspection/trigger` (POST) | Trigger manual inspection |
| `/api/camera/snapshot` | JPEG snapshot from active camera |
| `/api/camera/list` | List available cameras |
| `/api/camera/select` (POST) | Switch active camera |
| `/api/check/label` (POST) | Capture + detect label + send to SAP DM |
| `/api/check/weight` (POST) | Read/simulate weight + send to SAP DM |
| `/api/sap/dm/status` | Last SAP DM transmission |
| `/api/network` | WiFi/internet status |
| `/api/network/scan` | Scan WiFi (Pi only) |
| `/api/network/connect` (POST) | Connect to WiFi (Pi only) |

## Templates

- `base.html` — Layout with nav (dashboard + wifi link if Pi)
- `dashboard.html` — Card grid: camera (full-width with preview + selector), scale, inspection, network, SAP DM
- `wifi.html` — Scan, select, connect (Pi only)

## Static Assets

- `css/style.css` — Card-based responsive layout with camera preview styles
- `js/dashboard.js` — Camera preview (1fps), data polling (3s), check label/weight buttons, camera selector
