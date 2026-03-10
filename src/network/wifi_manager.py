"""WiFi management via NetworkManager (nmcli) — Pi only."""

import logging
import subprocess

logger = logging.getLogger(__name__)


def scan_networks() -> list[dict]:
    """
    Scan for available WiFi networks.

    Returns list of dicts with: ssid, signal (%), security
    """
    try:
        # Force a rescan
        subprocess.run(
            ["nmcli", "dev", "wifi", "rescan"],
            capture_output=True, timeout=10,
        )

        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi", "list"],
            capture_output=True, text=True, timeout=10,
        )

        networks = []
        seen_ssids = set()

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split(":")
            if len(parts) >= 3:
                ssid = parts[0]
                if not ssid or ssid in seen_ssids:
                    continue
                seen_ssids.add(ssid)
                networks.append({
                    "ssid": ssid,
                    "signal": parts[1],
                    "security": parts[2] if parts[2] else "Open",
                })

        # Sort by signal strength descending
        networks.sort(key=lambda n: int(n["signal"] or "0"), reverse=True)
        logger.info("WiFi scan found %d networks", len(networks))
        return networks

    except (subprocess.SubprocessError, OSError) as e:
        logger.error("WiFi scan failed: %s", e)
        return []


def connect(ssid: str, password: str) -> bool:
    """
    Connect to a WiFi network.

    Returns True if connection was successful.
    """
    try:
        result = subprocess.run(
            ["sudo", "nmcli", "dev", "wifi", "connect", ssid, "password", password],
            capture_output=True, text=True, timeout=30,
        )

        if result.returncode == 0:
            logger.info("Connected to WiFi: %s", ssid)
            return True

        logger.error("WiFi connection failed: %s", result.stderr.strip())
        return False

    except (subprocess.SubprocessError, OSError) as e:
        logger.error("WiFi connection error: %s", e)
        return False


def get_status() -> dict:
    """
    Get current WiFi connection status.

    Returns dict with: connected, ssid, ip, internet
    """
    status = {
        "connected": False,
        "ssid": None,
        "ip": None,
        "internet": False,
    }

    try:
        # Check WiFi connection
        result = subprocess.run(
            ["nmcli", "-t", "-f", "GENERAL.STATE,GENERAL.CONNECTION,IP4.ADDRESS",
             "dev", "show", "wlan0"],
            capture_output=True, text=True, timeout=5,
        )

        for line in result.stdout.strip().split("\n"):
            if "GENERAL.STATE:" in line and "connected" in line.lower():
                status["connected"] = True
            elif "GENERAL.CONNECTION:" in line:
                val = line.split(":", 1)[1].strip() if ":" in line else ""
                if val and val != "--":
                    status["ssid"] = val
            elif "IP4.ADDRESS" in line:
                val = line.split(":", 1)[1].strip() if ":" in line else ""
                if val:
                    status["ip"] = val.split("/")[0]  # Remove CIDR notation

        # Check internet connectivity
        if status["connected"]:
            ping = subprocess.run(
                ["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                capture_output=True, timeout=5,
            )
            status["internet"] = ping.returncode == 0

    except (subprocess.SubprocessError, OSError) as e:
        logger.error("WiFi status check failed: %s", e)

    return status


def is_connected() -> bool:
    """Quick check if WiFi is connected."""
    return get_status()["connected"]
