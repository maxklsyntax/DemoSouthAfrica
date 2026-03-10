"""KERN PCB 2000-1 scale module — reads weight via USB serial (KCP protocol)."""
from __future__ import annotations

import logging
import re

import serial

from src.config import settings

logger = logging.getLogger(__name__)


class Scale:
    """Interface to the KERN PCB 2000-1 precision scale via USB serial."""

    def __init__(self):
        self.ser = None

    def connect(self):
        """Open serial connection to the KERN scale."""
        try:
            self.ser = serial.Serial(
                port=settings.SCALE_PORT,
                baudrate=settings.SCALE_BAUDRATE,
                timeout=settings.SCALE_TIMEOUT,
            )
            logger.info("Scale connected on %s", settings.SCALE_PORT)
        except serial.SerialException as e:
            logger.error("Failed to connect to scale: %s", e)
            raise

    @property
    def is_connected(self) -> bool:
        return self.ser is not None and self.ser.is_open

    def read_weight(self) -> float | None:
        """
        Read current weight from the KERN scale.

        Sends KCP 'w' command, parses response like "     150.3 g".
        Returns weight in grams, or None if reading failed.
        """
        if not self.is_connected:
            logger.error("Scale not connected")
            return None

        try:
            self.ser.write(b"w\r\n")
            raw = self.ser.readline().decode("utf-8").strip()
            logger.debug("Scale raw: '%s'", raw)

            match = re.search(r"([-+]?\d+\.?\d*)", raw)
            if match:
                return float(match.group(1))

            logger.warning("Could not parse weight from: '%s'", raw)
            return None
        except (serial.SerialException, UnicodeDecodeError) as e:
            logger.error("Error reading scale: %s", e)
            return None

    def read_stable_weight(self) -> float | None:
        """
        Read weight multiple times and return value only if stable.

        Requires consecutive readings within WEIGHT_STABLE_TOLERANCE grams.
        """
        readings = []
        for _ in range(settings.WEIGHT_STABLE_READINGS + 2):
            w = self.read_weight()
            if w is not None:
                readings.append(w)

        if len(readings) < settings.WEIGHT_STABLE_READINGS:
            return None

        last_n = readings[-settings.WEIGHT_STABLE_READINGS:]
        if max(last_n) - min(last_n) < settings.WEIGHT_STABLE_TOLERANCE:
            return sum(last_n) / len(last_n)

        logger.warning("Weight not stable: %s", last_n)
        return None

    def tare(self):
        """Send tare command to the KERN scale (KCP 't' command)."""
        if not self.is_connected:
            logger.error("Scale not connected")
            return
        try:
            self.ser.write(b"t\r\n")
            logger.info("Tare command sent")
        except serial.SerialException as e:
            logger.error("Error sending tare command: %s", e)

    def close(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            logger.info("Scale disconnected")
