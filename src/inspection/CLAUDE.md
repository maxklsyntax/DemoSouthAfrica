# src/inspection/

Inspection business logic.

## engine.py — `run_inspection(scale, camera, app_state)`

Orchestrates one full bottle inspection cycle:

1. Read stable weight → check against tolerance (150–260g). If no scale: simulate random weight in range.
2. Capture camera frame → `detect_label()` + `detect_contamination()`
3. Determine overall result: GOOD only if weight OK + label present + no contamination
4. Update `app_state` with results

Note: SAP DM sending is not done here — it is triggered manually from the dashboard via "Check Label" and "Check Weight" buttons (see `web/api/routes.py`).

Returns a dict with: weight, weight_ok, label_present, contamination_detected, overall, details.
