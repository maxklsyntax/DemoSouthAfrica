#!/bin/bash
# =============================================================================
# Bottle Inspection System — Raspberry Pi Setup
#
# Run once on the Pi after cloning the repo:
#   chmod +x scripts/pi_setup.sh && sudo ./scripts/pi_setup.sh
#
# Sets up: venv, dependencies, systemd service, auto-update (git pull)
# =============================================================================

set -e

# --- Config ---
APP_USER="${SUDO_USER:-pi}"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="bottle-inspection"
UPDATE_TIMER_NAME="bottle-inspection-update"

echo "============================================"
echo " Bottle Inspection System — Pi Setup"
echo "============================================"
echo "App directory : $APP_DIR"
echo "Run as user   : $APP_USER"
echo ""

# Must run as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run with sudo"
    exit 1
fi

# --- 1. System dependencies ---
echo "[1/5] Installing system packages..."
apt-get update -qq
apt-get install -y -qq python3-venv python3-pip git libcap-dev > /dev/null

# --- 2. Python venv + dependencies ---
echo "[2/5] Setting up Python virtual environment..."
cd "$APP_DIR"

if [ ! -d ".venv" ]; then
    sudo -u "$APP_USER" python3 -m venv .venv
fi

sudo -u "$APP_USER" .venv/bin/pip install --quiet --upgrade pip
sudo -u "$APP_USER" .venv/bin/pip install --quiet -r requirements.txt

echo "  -> venv ready at $APP_DIR/.venv"

# --- 3. systemd service (main app) ---
echo "[3/5] Creating systemd service..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Bottle Inspection System
After=network-online.target NetworkManager.service
Wants=network-online.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/python -m src.main
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# --- 4. Auto-update: systemd timer (git pull every 5 min) ---
echo "[4/5] Creating auto-update service + timer..."

cat > /etc/systemd/system/${UPDATE_TIMER_NAME}.service << EOF
[Unit]
Description=Bottle Inspection — Git Pull & Restart if changed

[Service]
Type=oneshot
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=/bin/bash -c '\
  cd $APP_DIR && \
  OLD_HEAD=\$(git rev-parse HEAD) && \
  git pull --ff-only origin main 2>/dev/null && \
  NEW_HEAD=\$(git rev-parse HEAD) && \
  if [ "\$OLD_HEAD" != "\$NEW_HEAD" ]; then \
    echo "Code updated (\$OLD_HEAD -> \$NEW_HEAD), installing deps + restarting..." && \
    $APP_DIR/.venv/bin/pip install --quiet -r requirements.txt && \
    sudo systemctl restart ${SERVICE_NAME}; \
  else \
    echo "Already up to date."; \
  fi'
EOF

cat > /etc/systemd/system/${UPDATE_TIMER_NAME}.timer << EOF
[Unit]
Description=Check for updates every minute

[Timer]
OnBootSec=10
OnUnitActiveSec=60
AccuracySec=10

[Install]
WantedBy=timers.target
EOF

# Allow app user to restart the service without password
echo "$APP_USER ALL=(ALL) NOPASSWD: /bin/systemctl restart ${SERVICE_NAME}" > /etc/sudoers.d/${SERVICE_NAME}
chmod 440 /etc/sudoers.d/${SERVICE_NAME}

# --- 5. Enable and start everything ---
echo "[5/5] Enabling and starting services..."
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}.service
systemctl enable ${UPDATE_TIMER_NAME}.timer
systemctl start ${SERVICE_NAME}.service
systemctl start ${UPDATE_TIMER_NAME}.timer

echo ""
echo "============================================"
echo " Setup complete!"
echo "============================================"
echo ""
echo " App service  : sudo systemctl status $SERVICE_NAME"
echo " App logs     : sudo journalctl -u $SERVICE_NAME -f"
echo " Update timer : sudo systemctl status $UPDATE_TIMER_NAME.timer"
echo " Dashboard    : http://$(hostname -I | awk '{print $1}'):8080"
echo ""
echo " The Pi will check GitHub for updates every minute."
echo " If new code is found, it auto-installs deps and restarts."
echo ""
