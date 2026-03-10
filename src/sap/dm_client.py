"""SAP Digital Manufacturing (DM) client — posts inspection data to Data Collection API."""

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


def post_inspection_result(
    weight: float,
    label_ok: bool,
    contamination: bool,
    overall: str,
) -> dict:
    """
    Send complete inspection result to SAP DM Data Collection.

    Returns dict with: success (bool), timestamp (str), data (dict)
    for display in the dashboard.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    data = {
        "plant": settings.SAP_DM_PLANT,
        "timestamp": timestamp,
        "parameterValues": [
            {"name": "WEIGHT", "value": str(weight), "unit": "g"},
            {"name": "LABEL_PRESENT", "value": str(label_ok)},
            {"name": "CONTAMINATION_DETECTED", "value": str(contamination)},
            {"name": "OVERALL_RESULT", "value": overall},
        ],
    }

    result = {"success": False, "timestamp": timestamp, "data": data}

    if not settings.SAP_DM_BASE_URL:
        logger.warning("SAP DM not configured, skipping")
        return result

    url = f"{settings.SAP_DM_BASE_URL}/datacollection/v1/log"

    try:
        headers = _get_headers()
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        result["success"] = True
        logger.info("Inspection result sent to SAP DM: %s", overall)
    except requests.RequestException as e:
        logger.error("Failed to send inspection result to SAP DM: %s", e)

    return result
