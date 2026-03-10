# web/api/

Flask Blueprint with JSON REST API endpoints.

All routes read from `current_app.config["APP_STATE"]` which is the shared state dict updated by the main inspection loop. Network endpoints (scan, connect) are restricted to Raspberry Pi only.
