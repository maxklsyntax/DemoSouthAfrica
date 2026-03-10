"""Standalone script to test SAP API connectivity without hardware."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.sap import auth, dm_client, apm_client


def test_dm():
    """Test SAP DM connectivity."""
    print("\n--- SAP Digital Manufacturing ---")

    if not settings.SAP_DM_BASE_URL:
        print("SKIP: SAP_DM_BASE_URL not configured")
        return

    try:
        token = auth.get_bearer_token(
            settings.SAP_DM_CLIENT_ID,
            settings.SAP_DM_CLIENT_SECRET,
            settings.SAP_DM_TOKEN_URL,
        )
        print(f"OK: Token acquired ({token[:20]}...)")
    except Exception as e:
        print(f"FAIL: Token request failed: {e}")
        return

    result = dm_client.post_inspection_result(
        weight=155.3,
        label_ok=True,
        contamination=False,
        overall="GOOD",
    )
    print(f"Post inspection: {'OK' if result['success'] else 'FAIL'}")


def test_apm():
    """Test SAP APM connectivity."""
    print("\n--- SAP Asset Performance Management ---")

    if not settings.SAP_APM_BASE_URL:
        print("SKIP: SAP_APM_BASE_URL not configured")
        return

    result = apm_client.post_contamination_alert(
        brightness_avg=35.0,
        contamination_ratio=0.08,
    )
    print(f"Post contamination alert: {'OK' if result['success'] else 'FAIL'}")


if __name__ == "__main__":
    print("=== SAP Connection Test ===")
    test_dm()
    test_apm()
    print("\nDone.")
