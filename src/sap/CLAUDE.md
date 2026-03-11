# src/sap/

SAP API integration modules.

## auth.py — OAuth2 Token Management

- `get_bearer_token(client_id, client_secret, token_url) -> str`
- Caches tokens in a module-level dict, auto-refreshes 60s before expiry
- Used by the DM client

## dm_client.py — SAP Digital Manufacturing

- `post_label_result(label_ok: bool) -> dict` — Sends label presence (True/False) to SAP DM
- `post_weight_result(weight: float) -> dict` — Sends weight measurement to SAP DM
- Both use the Production Process API: `POST /pe/api/v1/process/processDefinitions/start`
- Same process key, differentiated by `dcGroup` and `parameterName`
- OAuth2 Bearer auth
- Returns `{success, timestamp, data}` for dashboard display

## apm_client.py — SAP Asset Performance Management

- `post_contamination_alert(brightness_avg, contamination_ratio) -> dict` — Alert only
- Currently not used from the dashboard (reserved for future use)

## API Endpoint Note

The exact API paths are based on SAP API Hub documentation and must be verified against the specific SAP tenant.
