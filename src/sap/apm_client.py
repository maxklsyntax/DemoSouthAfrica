"""SAP Asset Performance Management (APM) client — contamination alerts."""

import logging
from datetime import datetime, timezone

import requests

from src.config import settings
from src.sap.auth import get_bearer_token

logger = logging.getLogger(__name__)


def _get_headers() -> dict:
    """Build authorization headers — supports X-API-Key or OAuth2."""
    headers = {"Content-Type": "application/json"}

    if settings.SAP_APM_AUTH_MODE == "apikey":
        headers["X-API-Key"] = settings.SAP_APM_API_KEY
    else:
        token = get_bearer_token(
            settings.SAP_APM_CLIENT_ID,
            settings.SAP_APM_CLIENT_SECRET,
            settings.SAP_APM_TOKEN_URL,
        )
        headers["Authorization"] = f"Bearer {token}"

    return headers


def post_contamination_alert(brightness_avg: float, contamination_ratio: float) -> dict:
    """
    Post a contamination alert to SAP APM.

    Returns dict with: success (bool), timestamp (str), data (dict)
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    data = {
        "equipmentId": settings.SAP_APM_EQUIPMENT_ID,
        "alertType": "CONTAMINATION",
        "severity": "HIGH",
        "timestamp": timestamp,
        "description": (
            f"Contamination detected on bottle. "
            f"Average brightness: {brightness_avg:.1f}, "
            f"Anomalous pixel ratio: {contamination_ratio:.2%}"
        ),
        "parameters": {
            "brightnessAverage": round(brightness_avg, 1),
            "contaminationRatio": round(contamination_ratio, 4),
        },
    }

    result = {"success": False, "timestamp": timestamp, "data": data}

    if not settings.SAP_APM_BASE_URL:
        logger.warning("SAP APM not configured, skipping contamination alert")
        return result

    url = f"{settings.SAP_APM_BASE_URL}/services/api/v1/alerts"

    try:
        headers = _get_headers()
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        result["success"] = True
        logger.warning("Contamination alert sent to SAP APM!")
    except requests.RequestException as e:
        logger.error("Failed to send contamination alert to SAP APM: %s", e)

    return result
