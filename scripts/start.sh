#!/bin/bash
# Bottle Inspection System — Pi startup script
# Called by systemd service or manually

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== Bottle Inspection System ==="
echo "Working directory: $PROJECT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated"
fi

# Start the application
exec python3 -m src.main
