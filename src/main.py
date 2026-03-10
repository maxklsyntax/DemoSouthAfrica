"""Bottle Inspection System — main entry point.

Detects platform (Pi vs local), initializes hardware (real or mock),
starts the web dashboard, and runs the inspection loop.
"""

import logging
import sys
import threading
import time

from src.config import settings
from src.platform_detect import IS_RASPBERRY_PI, FEATURES
from src.inspection.engine import run_inspection

# --- Logging ---
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

# --- Shared application state (read by web dashboard) ---
app_state = {
    "scale_connected": False,
    "camera_available": False,
    "current_weight": None,
    "tare_weight": None,
    "last_inspection": {},
    "sap_dm_last": {"timestamp": None, "data": None, "success": None},
    "sap_apm_last": {"timestamp": None, "data": None, "success": None},
    "network": {"connected": False, "ssid": None, "ip": None, "internet": False},
}


def _init_hardware():
    """Initialize hardware — real on Pi, webcam or mock on local dev."""
    if IS_RASPBERRY_PI:
        from src.hardware.scale import Scale
        from src.hardware.camera import Camera
    else:
        from src.hardware.mock import MockScale as Scale
        logger.info("Running in LOCAL DEV MODE")

    # Scale
    scale = Scale()
    try:
        scale.connect()
        app_state["scale_connected"] = scale.is_connected
    except Exception as e:
        logger.error("Scale initialization failed: %s", e)

    # Camera: Pi uses picamera2, local dev tries webcam first, then mock
    if IS_RASPBERRY_PI:
        camera = Camera()
    else:
        from src.hardware.mock import WebcamCamera
        camera = WebcamCamera()
        camera.start()
        if not camera.is_available:
            logger.warning("No webcam found, falling back to mock camera")
            from src.hardware.mock import MockCamera
            camera = MockCamera()

    camera.start()
    app_state["camera_available"] = camera.is_available
    app_state["_camera"] = camera  # Reference for snapshot API

    return scale, camera


def _start_web_server():
    """Start Flask web server in a background daemon thread."""
    from web.app import create_app

    app = create_app(app_state)
    logger.info("Web dashboard starting on http://%s:%d", settings.WEB_HOST, settings.WEB_PORT)

    app.run(
        host=settings.WEB_HOST,
        port=settings.WEB_PORT,
        debug=False,
        use_reloader=False,
    )


def _handle_ap_mode():
    """
    Check WiFi connectivity and start AP mode if needed (Pi only).

    Returns True if WiFi is connected and normal operation can start.
    """
    if not FEATURES["wifi_management"]:
        # Not on Pi — skip WiFi management, assume connected
        app_state["network"] = {
            "connected": True,
            "ssid": "Local Dev",
            "ip": "127.0.0.1",
            "internet": True,
        }
        return True

    from src.network.wifi_manager import is_connected, get_status
    from src.network.ap_mode import start_ap, stop_ap, is_ap_active

    # Update network status
    app_state["network"] = get_status()

    if is_connected():
        logger.info("WiFi connected: %s", app_state["network"].get("ssid"))
        return True

    # No WiFi — start AP mode
    logger.warning("No WiFi connection — starting Access Point mode")
    if start_ap():
        logger.info("AP mode active. Connect to SSID: %s", settings.AP_SSID)
        logger.info("Open http://192.168.4.1:%d/wifi to configure WiFi", settings.WEB_PORT)

        # Wait for WiFi to be configured via the web interface
        while not is_connected():
            app_state["network"] = get_status()
            if not is_ap_active():
                # AP was stopped externally or WiFi connected via web UI
                break
            time.sleep(2)

        # Check if we're now connected
        if is_connected():
            stop_ap()
            app_state["network"] = get_status()
            logger.info("WiFi configured successfully: %s", app_state["network"].get("ssid"))
            return True

        # Still not connected — stay in AP mode, but continue anyway
        # so the web interface remains accessible for retry
        logger.warning("WiFi not configured yet. AP mode remains active.")
        return False

    logger.error("Failed to start AP mode")
    return False



def _update_network_status():
    """Update network status in app_state (Pi only)."""
    if not FEATURES["wifi_management"]:
        return

    from src.network.wifi_manager import get_status
    app_state["network"] = get_status()


def main():
    """Main entry point."""
    logger.info("=== Bottle Inspection System v0.1.0 ===")
    logger.info("Platform: %s", "Raspberry Pi" if IS_RASPBERRY_PI else "Local Dev")

    # Step 1: Check WiFi / AP mode
    _handle_ap_mode()

    # Step 2: Initialize hardware
    scale, camera = _init_hardware()

    # Step 3: Start web server in background
    web_thread = threading.Thread(target=_start_web_server, daemon=True)
    web_thread.start()

    logger.info("System ready. Starting inspection loop.")
    logger.info("Dashboard: http://%s:%d", settings.WEB_HOST, settings.WEB_PORT)

    # Step 4: Main inspection loop
    last_network_check = 0
    previous_weight = 0.0

    try:
        while True:
            now = time.time()

            # Periodic network status update (every 30s)
            if now - last_network_check >= 30:
                _update_network_status()
                last_network_check = now

            # Manual inspection trigger (from dashboard button)
            if app_state.get("trigger_inspection"):
                app_state["trigger_inspection"] = False
                logger.info("Manual inspection triggered")
                run_inspection(scale, camera, app_state)

            # Scale polling — detect bottle placement
            weight = scale.read_weight()
            if weight is not None:
                app_state["current_weight"] = round(weight, 1)

            if weight is not None and weight > settings.WEIGHT_TRIGGER:
                if previous_weight <= settings.WEIGHT_TRIGGER:
                    # Bottle just placed on scale
                    logger.info("Bottle detected (%.1f g), stabilizing...", weight)
                    time.sleep(settings.STABILIZATION_DELAY)

                    # Run full inspection
                    run_inspection(scale, camera, app_state)

                    # Wait for bottle removal
                    logger.info("Waiting for bottle removal...")
                    while True:
                        w = scale.read_weight()
                        if w is not None:
                            app_state["current_weight"] = round(w, 1)
                        if w is not None and w < settings.WEIGHT_TRIGGER:
                            logger.info("Bottle removed")
                            break
                        time.sleep(0.3)

            previous_weight = weight if weight is not None else 0.0
            time.sleep(settings.INSPECTION_LOOP_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Shutdown requested (Ctrl+C)")
    finally:
        scale.close()
        camera.stop()
        logger.info("=== Bottle Inspection System stopped ===")


if __name__ == "__main__":
    main()
