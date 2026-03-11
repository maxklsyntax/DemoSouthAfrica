# web/templates/

Jinja2 HTML templates using template inheritance from `base.html`.

- `base.html` — Base layout: nav bar, main content block, footer with version and connection status
- `dashboard.html` — Card grid with live camera preview, Check Label / Check Weight buttons, camera selector, and auto-refreshing data
- `wifi.html` — WiFi configuration: scan, select network, enter password, connect (Pi only)

The `is_pi` template variable controls whether the WiFi nav link and page are shown.
