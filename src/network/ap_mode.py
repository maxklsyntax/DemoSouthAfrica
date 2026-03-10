"""Access Point mode management via NetworkManager — Pi only.

When the Pi cannot connect to WiFi on boot, it starts an AP so users
can configure WiFi via the web interface from a phone or laptop.
"""

import logging
import subprocess

from src.config import settings

logger = logging.getLogger(__name__)

_AP_CONNECTION_NAME = "BottleInspection-AP"


def start_ap() -> bool:
    """
    Start WiFi Access Point mode using NetworkManager's built-in hotspot.

    Uses nmcli to create a hotspot — no hostapd/dnsmasq needed on Bookworm.
    The hotspot provides DHCP (ipv4.method=shared) so clients get an IP automatically.

    Returns True if AP started successfully.
    """
    try:
        # Remove any existing AP connection first
        subprocess.run(
            ["sudo", "nmcli", "con", "delete", _AP_CONNECTION_NAME],
            capture_output=True, timeout=10,
        )

        result = subprocess.run(
            [
                "sudo", "nmcli", "dev", "wifi", "hotspot",
                "ifname", "wlan0",
                "con-name", _AP_CONNECTION_NAME,
                "ssid", settings.AP_SSID,
                "password", settings.AP_PASSWORD,
            ],
            capture_output=True, text=True, timeout=15,
        )

        if result.returncode == 0:
            logger.info("AP mode started: SSID=%s", settings.AP_SSID)
            return True

        logger.error("Failed to start AP mode: %s", result.stderr.strip())
        return False

    except (subprocess.SubprocessError, OSError) as e:
        logger.error("AP mode start error: %s", e)
        return False


def stop_ap() -> bool:
    """
    Stop the Access Point and return to normal WiFi client mode.

    Returns True if AP was stopped successfully.
    """
    try:
        result = subprocess.run(
            ["sudo", "nmcli", "con", "down", _AP_CONNECTION_NAME],
            capture_output=True, text=True, timeout=10,
        )

        if result.returncode == 0:
            logger.info("AP mode stopped")
            return True

        logger.warning("AP stop returned: %s", result.stderr.strip())
        return False

    except (subprocess.SubprocessError, OSError) as e:
        logger.error("AP mode stop error: %s", e)
        return False


def is_ap_active() -> bool:
    """Check if the AP hotspot connection is currently active."""
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "con", "show", "--active"],
            capture_output=True, text=True, timeout=5,
        )

        for line in result.stdout.strip().split("\n"):
            if _AP_CONNECTION_NAME in line:
                return True

        return False

    except (subprocess.SubprocessError, OSError):
        return False
