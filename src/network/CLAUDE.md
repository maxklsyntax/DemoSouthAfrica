# src/network/

WiFi and Access Point management — **Pi only** (skipped on local dev).

## wifi_manager.py

Uses `nmcli` subprocess calls (Raspberry Pi OS Bookworm uses NetworkManager natively).

- `scan_networks() -> list[dict]` — SSID, signal %, security
- `connect(ssid, password) -> bool`
- `get_status() -> dict` — connected, ssid, ip, internet (pings 8.8.8.8)
- `is_connected() -> bool`

## ap_mode.py

Creates a WiFi hotspot via `nmcli device wifi hotspot` — no hostapd or dnsmasq needed.

- `start_ap() -> bool` — Creates hotspot with SSID from settings
- `stop_ap() -> bool`
- `is_ap_active() -> bool`

## AP Mode Flow

Boot → no WiFi → `start_ap()` → user connects to hotspot → opens web UI `/wifi` → scans + selects network → Pi connects → `stop_ap()` → normal operation. If connection fails → AP restarts.
