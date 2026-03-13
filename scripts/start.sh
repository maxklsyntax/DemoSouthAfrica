#!/bin/bash
# Bottle Inspection System — Start script
# Starts all services needed for the project

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/.app.pid"

cd "$PROJECT_DIR"

# Check if already running
if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "Application is already running (PID $(cat "$PID_FILE"))"
    echo "Use scripts/stop.sh to stop it first."
    exit 1
fi

echo "=== Bottle Inspection System ==="
echo "Working directory: $PROJECT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated"
fi

# Start the application
echo "Starting application..."
python3 -m src.main &
APP_PID=$!
echo "$APP_PID" > "$PID_FILE"

echo "Application started (PID $APP_PID)"
echo "Dashboard: http://localhost:8080"
echo "Stop with: scripts/stop.sh"

# Wait for the process (so Ctrl+C works in foreground mode)
wait "$APP_PID" 2>/dev/null
rm -f "$PID_FILE"
