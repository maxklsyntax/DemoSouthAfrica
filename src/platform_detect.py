"""Platform detection for Raspberry Pi vs local development."""

import platform
from pathlib import Path


def _detect_raspberry_pi() -> bool:
    """Check if running on a Raspberry Pi."""
    # Primary check: device tree model file (Linux/Pi specific)
    model_path = Path("/proc/device-tree/model")
    if model_path.exists():
        try:
            model = model_path.read_text()
            if "Raspberry Pi" in model:
                return True
        except OSError:
            pass

    # Fallback: check architecture
    machine = platform.machine().lower()
    if machine in ("aarch64", "armv7l", "armv6l"):
        system = platform.system()
        if system == "Linux":
            return True

    return False


IS_RASPBERRY_PI = _detect_raspberry_pi()

FEATURES = {
    "hardware_scale": IS_RASPBERRY_PI,
    "hardware_camera": IS_RASPBERRY_PI,
    "wifi_management": IS_RASPBERRY_PI,
    "ap_mode": IS_RASPBERRY_PI,
    "sap_integration": True,
    "web_dashboard": True,
}
