"""REST API endpoints and page routes for the web dashboard."""

import logging

import cv2
from flask import Blueprint, Flask, Response, current_app, jsonify, render_template, request

from src.platform_detect import IS_RASPBERRY_PI

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _state() -> dict:
    return current_app.config["APP_STATE"]


# --- JSON API Endpoints ---


@api_bp.route("/status")
def status():
    """Overall system status."""
    state = _state()
    return jsonify({
        "is_raspberry_pi": IS_RASPBERRY_PI,
        "scale_connected": state.get("scale_connected", False),
        "camera_available": state.get("camera_available", False),
        "internet_connected": state.get("network", {}).get("internet", False),
    })


@api_bp.route("/scale")
def scale():
    """Current scale data."""
    state = _state()
    return jsonify({
        "connected": state.get("scale_connected", False),
        "current_weight": state.get("current_weight"),
        "tare_weight": state.get("tare_weight"),
    })


@api_bp.route("/inspection/latest")
def inspection_latest():
    """Last inspection result."""
    state = _state()
    return jsonify(state.get("last_inspection", {}))


@api_bp.route("/inspection/trigger", methods=["POST"])
def inspection_trigger():
    """Trigger a manual inspection."""
    state = _state()
    state["trigger_inspection"] = True
    return jsonify({"triggered": True})


@api_bp.route("/camera/snapshot")
def camera_snapshot():
    """Capture a JPEG snapshot from the camera."""
    state = _state()
    camera = state.get("_camera")
    if camera is None or not camera.is_available:
        return Response(status=503)

    frame = camera.capture()
    if frame is None:
        return Response(status=503)

    _, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return Response(jpeg.tobytes(), mimetype="image/jpeg")


@api_bp.route("/camera/list")
def camera_list():
    """List available camera devices."""
    from src.hardware.mock import WebcamCamera

    state = _state()
    camera = state.get("_camera")

    active_index = None
    if hasattr(camera, "device_index"):
        active_index = camera.device_index

    cameras = WebcamCamera.enumerate_cameras(skip_index=active_index)
    return jsonify({"cameras": cameras, "active": active_index})


@api_bp.route("/camera/select", methods=["POST"])
def camera_select():
    """Switch to a different camera device."""
    state = _state()
    camera = state.get("_camera")

    data = request.get_json()
    device_index = data.get("index")
    if device_index is None:
        return jsonify({"error": "index is required"}), 400

    if not hasattr(camera, "switch_device"):
        return jsonify({"error": "Camera switching not supported"}), 400

    camera.switch_device(int(device_index))
    state["camera_available"] = camera.is_available

    return jsonify({
        "success": camera.is_available,
        "active": camera.device_index if camera.is_available else None,
    })


@api_bp.route("/sap/dm/status")
def sap_dm_status():
    """Last SAP DM transmission status."""
    state = _state()
    return jsonify(state.get("sap_dm_last", {}))


@api_bp.route("/sap/apm/status")
def sap_apm_status():
    """Last SAP APM transmission status."""
    state = _state()
    return jsonify(state.get("sap_apm_last", {}))


@api_bp.route("/network")
def network():
    """Network / WiFi status."""
    state = _state()
    return jsonify(state.get("network", {}))


@api_bp.route("/network/scan")
def network_scan():
    """Scan for available WiFi networks (Pi only)."""
    if not IS_RASPBERRY_PI:
        return jsonify({"error": "WiFi scanning only available on Raspberry Pi"}), 400

    from src.network.wifi_manager import scan_networks
    networks = scan_networks()
    return jsonify({"networks": networks})


@api_bp.route("/network/connect", methods=["POST"])
def network_connect():
    """Connect to a WiFi network (Pi only)."""
    if not IS_RASPBERRY_PI:
        return jsonify({"error": "WiFi connection only available on Raspberry Pi"}), 400

    data = request.get_json()
    ssid = data.get("ssid", "")
    password = data.get("password", "")

    if not ssid:
        return jsonify({"error": "SSID is required"}), 400

    from src.network.wifi_manager import connect
    success = connect(ssid, password)

    return jsonify({"success": success, "ssid": ssid})


# --- Page Routes ---


def register_page_routes(app: Flask):
    """Register HTML page routes on the Flask app."""

    @app.route("/")
    def dashboard():
        return render_template(
            "dashboard.html",
            is_pi=IS_RASPBERRY_PI,
        )

    @app.route("/wifi")
    def wifi_config():
        if not IS_RASPBERRY_PI:
            return "WiFi configuration is only available on Raspberry Pi", 404
        return render_template("wifi.html")
