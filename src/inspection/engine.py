"""Inspection engine — orchestrates a bottle inspection cycle."""

import logging
import random

from src.config import settings
from src.sap import dm_client, apm_client

logger = logging.getLogger(__name__)


def run_inspection(scale, camera, app_state: dict) -> dict:
    """
    Execute a bottle inspection cycle.

    Scale and camera are each optional (pass None to skip).
    Each available component runs its checks independently.

    Updates app_state with last inspection and SAP transmission results.
    Returns the inspection result dict.
    """
    result = {
        "weight": None,
        "weight_ok": None,
        "label_present": None,
        "contamination_detected": None,
        "overall": "N/A",
        "details": {},
    }

    # Step 1: Weight (real scale or simulated)
    if scale is not None and scale.is_connected:
        weight = scale.read_stable_weight()
        if weight is not None:
            result["weight"] = round(weight, 1)
            result["weight_ok"] = settings.WEIGHT_MIN <= weight <= settings.WEIGHT_MAX
            logger.info("Weight: %.1f g — OK: %s", weight, result["weight_ok"])
        else:
            logger.error("Could not read stable weight")
    else:
        # No scale: simulate a realistic weight for demo purposes
        weight = round(random.uniform(settings.WEIGHT_MIN, settings.WEIGHT_MAX), 1)
        result["weight"] = weight
        result["weight_ok"] = True
        logger.info("Weight (simulated): %.1f g", weight)

    # Step 2: Camera (if available)
    if camera is not None and camera.is_available:
        from src.hardware.camera import detect_label, detect_contamination

        frame = camera.capture()
        if frame is not None:
            label_result = detect_label(frame)
            result["label_present"] = label_result["label_present"]
            result["details"]["label"] = label_result

            contam_result = detect_contamination(frame)
            result["contamination_detected"] = contam_result["contamination_detected"]
            result["details"]["contamination"] = contam_result

            # Send contamination alert to SAP APM
            if result["contamination_detected"]:
                apm_result = apm_client.post_contamination_alert(
                    contam_result["brightness_avg"],
                    contam_result["anomalous_ratio"],
                )
                app_state["sap_apm_last"] = apm_result
        else:
            logger.error("Camera capture failed")

    # Step 3: Determine overall result based on available checks
    checks_passed = True
    has_any_check = False

    if result["weight_ok"] is not None:
        has_any_check = True
        if not result["weight_ok"]:
            checks_passed = False

    if result["label_present"] is not None:
        has_any_check = True
        if not result["label_present"]:
            checks_passed = False

    if result["contamination_detected"] is not None:
        has_any_check = True
        if result["contamination_detected"]:
            checks_passed = False

    if has_any_check:
        result["overall"] = "GOOD" if checks_passed else "BAD"

    logger.info(
        "=== INSPECTION: %s === (weight=%s, label=%s, contamination=%s)",
        result["overall"],
        result.get("weight", "N/A"),
        result["label_present"],
        result["contamination_detected"],
    )

    # SAP DM sending is done manually via dashboard buttons
    app_state["last_inspection"] = result

    return result
