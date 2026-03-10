"""OAuth2 Client Credentials token management for SAP APIs."""

import logging
import time

import requests

logger = logging.getLogger(__name__)

# Token cache: keyed by (client_id, token_url)
_token_cache: dict[tuple[str, str], dict] = {}


def get_bearer_token(client_id: str, client_secret: str, token_url: str) -> str:
    """
    Acquire or return a cached OAuth2 Bearer token.

    Uses Client Credentials grant. Refreshes token 60 seconds before expiry.
    Raises requests.RequestException on failure.
    """
    cache_key = (client_id, token_url)
    cached = _token_cache.get(cache_key)

    if cached and cached["expires_at"] > time.time() + 60:
        return cached["access_token"]

    logger.info("Requesting new OAuth2 token from %s", token_url)

    response = requests.post(
        token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    response.raise_for_status()
    token_data = response.json()

    expires_in = token_data.get("expires_in", 3600)
    _token_cache[cache_key] = {
        "access_token": token_data["access_token"],
        "expires_at": time.time() + expires_in,
    }

    logger.info("Token acquired, expires in %d seconds", expires_in)
    return token_data["access_token"]
