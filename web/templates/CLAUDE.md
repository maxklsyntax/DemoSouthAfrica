# web/templates/

Jinja2 HTML templates using template inheritance from `base.html`.

- `base.html` — Base layout: nav bar, main content block, footer with version and connection status
- `dashboard.html` — 6-card responsive grid with auto-refreshing data (via `dashboard.js`)
- `wifi.html` — WiFi configuration: scan, select network, enter password, connect (Pi only)

The `is_pi` template variable controls whether the WiFi nav link and page are shown.
