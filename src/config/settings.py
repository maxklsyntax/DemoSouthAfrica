"""Central configuration — loads secrets from .env, defines all thresholds and settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env")

# --- Hardware ---
SCALE_PORT = "/dev/ttyUSB0"
SCALE_BAUDRATE = 9600
SCALE_TIMEOUT = 2  # seconds

# --- Inspection Tolerances ---
WEIGHT_MIN = 150.0       # grams, filled bottle minimum
WEIGHT_MAX = 260.0       # grams, filled bottle maximum
WEIGHT_TRIGGER = 50.0    # grams, minimum to detect bottle placed
WEIGHT_STABLE_READINGS = 3
WEIGHT_STABLE_TOLERANCE = 0.5  # grams, max deviation for stable reading

# --- Camera / Label Detection ---
LABEL_EDGE_THRESHOLD = 50
LABEL_MIN_CONTOUR_AREA = 5000
LABEL_BRIGHTNESS_DIFF = 30

# --- Contamination Detection ---
CONTAMINATION_BRIGHTNESS_LOW = 40
CONTAMINATION_BRIGHTNESS_HIGH = 240
CONTAMINATION_PIXEL_RATIO = 0.05  # 5% of ROI pixels

# --- Timing ---
INSPECTION_LOOP_INTERVAL = 0.5   # seconds between scale polling
STABILIZATION_DELAY = 1.5        # seconds to wait for scale to stabilize

# --- SAP Digital Manufacturing (DM) ---
SAP_DM_CLIENT_ID = os.getenv("SAP_DM_CLIENT_ID", "")
SAP_DM_CLIENT_SECRET = os.getenv("SAP_DM_CLIENT_SECRET", "")
SAP_DM_TOKEN_URL = os.getenv("SAP_DM_TOKEN_URL", "")
SAP_DM_BASE_URL = os.getenv("SAP_DM_BASE_URL", "")
SAP_DM_PLANT = os.getenv("SAP_DM_PLANT", "")

# --- SAP Asset Performance Management (APM) ---
SAP_APM_AUTH_MODE = os.getenv("SAP_APM_AUTH_MODE", "apikey")  # "apikey" or "oauth2"
SAP_APM_API_KEY = os.getenv("SAP_APM_API_KEY", "")
SAP_APM_BASE_URL = os.getenv("SAP_APM_BASE_URL", "")
SAP_APM_CLIENT_ID = os.getenv("SAP_APM_CLIENT_ID", "")
SAP_APM_CLIENT_SECRET = os.getenv("SAP_APM_CLIENT_SECRET", "")
SAP_APM_TOKEN_URL = os.getenv("SAP_APM_TOKEN_URL", "")
SAP_APM_EQUIPMENT_ID = os.getenv("SAP_APM_EQUIPMENT_ID", "")

# --- Web ---
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "8080"))

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Network / AP Mode ---
AP_SSID = "BottleInspection-Setup"
AP_PASSWORD = "inspect123"
