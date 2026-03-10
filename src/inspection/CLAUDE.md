# src/inspection/

Inspection business logic.

## engine.py — `run_inspection(scale, camera, app_state)`

Orchestrates one full bottle inspection cycle:

1. Read stable weight → check against tolerance (150–260g)
2. Capture camera frame → `detect_label()` + `detect_contamination()`
3. If contamination detected → POST alert to SAP APM
4. Determine overall result: GOOD only if weight OK + label present + no contamination
5. POST full result to SAP DM Data Collection
6. Update `app_state` with results

Returns a dict with: weight, weight_ok, label_present, contamination_detected, overall, details.
