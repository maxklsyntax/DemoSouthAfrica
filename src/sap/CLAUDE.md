# src/sap/

SAP API integration modules.

## auth.py — OAuth2 Token Management

- `get_bearer_token(client_id, client_secret, token_url) -> str`
- Caches tokens in a module-level dict, auto-refreshes 60s before expiry
- Used by both DM and APM clients

## dm_client.py — SAP Digital Manufacturing

- `post_inspection_result(weight, label_ok, contamination, overall) -> dict`
- OAuth2 Bearer auth
- POST to `/datacollection/v1/log` with parameter values
- Returns `{success, timestamp, data}` for dashboard display

## apm_client.py — SAP Asset Performance Management

- `post_sensor_data(temperature, humidity, pressure) -> dict` — Indicator values
- `post_contamination_alert(brightness_avg, contamination_ratio) -> dict` — Alert
- Supports X-API-Key or OAuth2 (configured via `SAP_APM_AUTH_MODE` in .env)
- POST to `/services/api/v1/indicator-values` and `/services/api/v1/alerts`

## API Endpoint Note

The exact API paths are based on SAP API Hub documentation and must be verified against the specific SAP tenant. Payload formats may need adjustment after first real API test.
