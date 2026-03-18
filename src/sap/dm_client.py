"""SAP Digital Manufacturing (DM) client — posts inspection data via Production Process API."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import requests

from src.config import settings
from src.sap.auth import get_bearer_token

logger = logging.getLogger(__name__)


def _get_headers() -> dict:
    """Build authorization headers for SAP DM API calls."""
    token = get_bearer_token(
        settings.SAP_DM_CLIENT_ID,
        settings.SAP_DM_CLIENT_SECRET,
        settings.SAP_DM_TOKEN_URL,
    )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _start_production_process(process_key: str, data: list[dict], resource: str = None) -> dict:
    """
    Start a Production Process in SAP DM with the given data entries.

    POST /pe/api/v1/process/processDefinitions/start?key=<key>&async=true
    """
    if resource is None:
        resource = settings.SAP_DM_RESOURCE
    timestamp = datetime.now(timezone.utc).isoformat()
    result = {"success": False, "timestamp": timestamp, "data": data}

    if not settings.SAP_DM_BASE_URL:
        logger.warning("SAP DM not configured, skipping")
        return result

    url = (
        f"{settings.SAP_DM_BASE_URL}"
        f"/pe/api/v1/process/processDefinitions/start"
        f"?key={process_key}&async=true"
    )

    body = {
        "plant": settings.SAP_DM_PLANT,
        "resource": resource,
        "origin": "Machine",
        "data": data,
    }

    try:
        headers = _get_headers()
        response = requests.post(url, json=body, headers=headers, timeout=10)
        response.raise_for_status()
        result["success"] = True
        logger.info("Production Process started: %s", process_key)
    except requests.RequestException as e:
        logger.error("Failed to start Production Process %s: %s", process_key, e)

    return result


def post_label_result(label_ok: bool) -> dict:
    """Send label inspection result to SAP DM — posts to both QM and FILL workcenters."""
    data = [
        {
            "comment": "",
            "parameterName": "LABEL_PRESENT",
            "dcGroup": "VI_LABEL_INSPECTION",
            "parameterValue": str(label_ok),
        }
    ]
    result_qm = _start_production_process(settings.SAP_DM_LABEL_PROCESS_KEY, data, resource="QM")
    result_fill = _start_production_process(settings.SAP_DM_LABEL_PROCESS_KEY, data, resource="FILL")
    # Return combined result — success only if both succeed
    return {
        "success": result_qm["success"] and result_fill["success"],
        "timestamp": result_qm["timestamp"],
        "data": data,
        "details": {"QM": result_qm["success"], "FILL": result_fill["success"]},
    }


def post_weight_result(weight: float) -> dict:
    """Send weight measurement to SAP DM via VI_WEIGHT_MEASUREMENT (same PP as label)."""
    data = [
        {
            "comment": "",
            "parameterName": "WEIGHT",
            "dcGroup": "VI_WEIGHT_MEASUREMENT",
            "parameterValue": str(weight),
        }
    ]
    return _start_production_process(settings.SAP_DM_LABEL_PROCESS_KEY, data)
