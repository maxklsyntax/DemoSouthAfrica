"""Camera module — RPi Camera Module 3 with label detection and contamination analysis."""
from __future__ import annotations

import logging

import cv2
import numpy as np

from src.config import settings

logger = logging.getLogger(__name__)

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    logger.warning("picamera2 not available — camera will not work on this platform")


class Camera:
    """Interface to the Raspberry Pi Camera Module 3 via picamera2."""

    def __init__(self):
        self.picam2 = None

    def start(self):
        """Initialize and start the camera with autofocus enabled."""
        if not PICAMERA_AVAILABLE:
            logger.warning("Camera not available (no picamera2)")
            return

        from libcamera import controls

        self.picam2 = Picamera2()
        cam_config = self.picam2.create_still_configuration(
            main={"size": (1920, 1080)}
        )
        self.picam2.configure(cam_config)
        self.picam2.start()

        # Enable continuous autofocus (Camera Module 3 / IMX708)
        try:
            self.picam2.set_controls({
                "AfMode": controls.AfModeEnum.Continuous,
                "AfSpeed": controls.AfSpeedEnum.Fast,
            })
            logger.info("Camera started (picamera2) — continuous autofocus enabled")
        except Exception as e:
            logger.warning("Autofocus not available: %s", e)
            logger.info("Camera started (picamera2)")

    @property
    def is_available(self) -> bool:
        return self.picam2 is not None

    def capture(self) -> np.ndarray | None:
        """Capture a single frame, returns BGR numpy array."""
        if not self.picam2:
            logger.error("Camera not initialized")
            return None

        frame = self.picam2.capture_array()
        # picamera2 returns RGB, convert to BGR for OpenCV
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    def stop(self):
        """Stop the camera."""
        if self.picam2:
            self.picam2.stop()
            logger.info("Camera stopped")


def detect_label(frame: np.ndarray) -> dict:
    """
    Detect whether a label is present on the bottle.

    Uses Canny edge detection on the center ROI of the image.
    If the largest contour area exceeds the threshold, a label is detected.

    Returns dict with: label_present (bool), contour_area (float), edge_density (float)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(
        blurred,
        settings.LABEL_EDGE_THRESHOLD,
        settings.LABEL_EDGE_THRESHOLD * 2,
    )

    # Center ROI (50% of image)
    h, w = edges.shape
    roi = edges[h // 4: 3 * h // 4, w // 4: 3 * w // 4]
    edge_density = np.count_nonzero(roi) / roi.size

    contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = max((cv2.contourArea(c) for c in contours), default=0.0)

    label_present = max_area > settings.LABEL_MIN_CONTOUR_AREA

    logger.info(
        "Label detection: present=%s, max_contour=%.0f, edge_density=%.4f",
        label_present, max_area, edge_density,
    )

    return {
        "label_present": bool(label_present),
        "contour_area": float(max_area),
        "edge_density": float(edge_density),
    }


def detect_contamination(frame: np.ndarray) -> dict:
    """
    Detect contamination by analyzing brightness anomalies.

    Counts pixels below low threshold (dark spots) or above high threshold
    (bright spots) in the center ROI. If the anomalous pixel ratio exceeds
    the configured threshold, contamination is detected.

    Returns dict with: contamination_detected (bool), brightness_avg (float),
                       anomalous_ratio (float)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Center ROI (50% of image)
    h, w = gray.shape
    roi = gray[h // 4: 3 * h // 4, w // 4: 3 * w // 4]

    brightness_avg = float(np.mean(roi))
    dark_pixels = np.count_nonzero(roi < settings.CONTAMINATION_BRIGHTNESS_LOW)
    bright_pixels = np.count_nonzero(roi > settings.CONTAMINATION_BRIGHTNESS_HIGH)
    anomalous_ratio = (dark_pixels + bright_pixels) / roi.size

    contamination = anomalous_ratio > settings.CONTAMINATION_PIXEL_RATIO

    logger.info(
        "Contamination check: detected=%s, brightness_avg=%.1f, anomalous_ratio=%.4f",
        contamination, brightness_avg, anomalous_ratio,
    )

    return {
        "contamination_detected": bool(contamination),
        "brightness_avg": float(brightness_avg),
        "anomalous_ratio": float(anomalous_ratio),
    }
