"""Mock hardware implementations for local development (Windows/Mac)."""
from __future__ import annotations

import logging
import random
import time

import numpy as np

logger = logging.getLogger(__name__)


class MockScale:
    """Simulates the KERN scale with random weight values."""

    def __init__(self):
        self._connected = False
        self._tare_offset = 0.0
        self._current_weight = 0.0
        self._last_change = time.time()

    def connect(self):
        self._connected = True
        logger.info("[MOCK] Scale connected")

    @property
    def is_connected(self) -> bool:
        return self._connected

    def read_weight(self) -> float | None:
        if not self._connected:
            return None

        # Simulate: every 10 seconds, randomly place or remove a bottle
        if time.time() - self._last_change > 10:
            if self._current_weight < 10:
                # Place a bottle (random filled weight)
                self._current_weight = random.uniform(140, 260)
            else:
                # Remove the bottle
                self._current_weight = random.uniform(0, 5)
            self._last_change = time.time()

        # Add small noise
        noise = random.uniform(-0.3, 0.3)
        return round(self._current_weight - self._tare_offset + noise, 1)

    def read_stable_weight(self) -> float | None:
        return self.read_weight()

    def tare(self):
        if self._connected:
            self._tare_offset = self._current_weight
            logger.info("[MOCK] Tare set to %.1f g", self._tare_offset)

    def close(self):
        self._connected = False
        logger.info("[MOCK] Scale disconnected")


class MockCamera:
    """Simulates the camera with generated test frames."""

    def __init__(self):
        self._started = False

    def start(self):
        self._started = True
        logger.info("[MOCK] Camera started")

    @property
    def is_available(self) -> bool:
        return self._started

    def capture(self) -> np.ndarray | None:
        if not self._started:
            return None

        # Generate a 1920x1080 test frame with some features
        frame = np.full((1080, 1920, 3), 180, dtype=np.uint8)

        # Draw a simulated label rectangle in the center
        if random.random() > 0.2:  # 80% chance label is present
            cv2 = _get_cv2()
            if cv2:
                cv2.rectangle(frame, (700, 300), (1220, 780), (255, 255, 255), -1)
                cv2.rectangle(frame, (700, 300), (1220, 780), (0, 0, 0), 3)

        return frame

    def stop(self):
        self._started = False
        logger.info("[MOCK] Camera stopped")


class WebcamCamera:
    """Uses the laptop webcam via OpenCV for real image capture."""

    def __init__(self, device_index: int = 0):
        self._device_index = device_index
        self._cap = None

    @property
    def device_index(self) -> int:
        return self._device_index

    def start(self):
        cv2 = _get_cv2()
        if not cv2:
            logger.error("OpenCV not installed — webcam not available")
            return

        self._cap = cv2.VideoCapture(self._device_index)
        if self._cap.isOpened():
            logger.info("Webcam started (device %d)", self._device_index)
        else:
            logger.error("Could not open webcam (device %d)", self._device_index)
            self._cap.release()
            self._cap = None

    @property
    def is_available(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    def capture(self) -> np.ndarray | None:
        if not self.is_available:
            return None

        ret, frame = self._cap.read()
        if ret:
            return frame

        logger.error("Webcam capture failed")
        return None

    def switch_device(self, device_index: int):
        """Stop current capture and switch to a different camera device."""
        self.stop()
        self._device_index = device_index
        self.start()

    def stop(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            logger.info("Webcam stopped")

    @staticmethod
    def enumerate_cameras(max_index: int = 8, skip_index: int | None = None) -> list[dict]:
        """Probe camera indices and return list of available devices.

        skip_index: don't probe this index (it's already open/active).
        """
        cv2 = _get_cv2()
        if not cv2:
            return []

        cameras = []
        for idx in range(max_index):
            if idx == skip_index:
                # Already active — report it without opening
                cameras.append({
                    "index": idx,
                    "name": f"Camera {idx} (active)",
                    "resolution": "—",
                })
                continue
            try:
                cap = cv2.VideoCapture(idx)
                if cap.isOpened():
                    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    name = cap.getBackendName()
                    cameras.append({
                        "index": idx,
                        "name": f"Camera {idx} ({name})",
                        "resolution": f"{w}x{h}",
                    })
                    cap.release()
            except Exception:
                continue
        return cameras


def _get_cv2():
    """Lazy import cv2 for mock camera."""
    try:
        import cv2
        return cv2
    except ImportError:
        return None
