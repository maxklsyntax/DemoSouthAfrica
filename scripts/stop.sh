#!/bin/bash
# Bottle Inspection System — Stop script
# Stops all services started by start.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/.app.pid"

echo "=== Stopping Bottle Inspection System ==="

stopped=false

# Stop via PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping application (PID $PID)..."
        kill "$PID" 2>/dev/null
        # Wait up to 5 seconds for graceful shutdown
        for i in $(seq 1 10); do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 0.5
        done
        # Force kill if still running
        if kill -0 "$PID" 2>/dev/null; then
            echo "Force killing (PID $PID)..."
            kill -9 "$PID" 2>/dev/null
        fi
        stopped=true
    fi
    rm -f "$PID_FILE"
fi

# Also kill any orphaned processes on port 8080
PORT_PID=$(lsof -ti :8080 2>/dev/null)
if [ -n "$PORT_PID" ]; then
    echo "Stopping process on port 8080 (PID $PORT_PID)..."
    kill "$PORT_PID" 2>/dev/null
    sleep 1
    # Force kill if still there
    if kill -0 "$PORT_PID" 2>/dev/null; then
        kill -9 "$PORT_PID" 2>/dev/null
    fi
    stopped=true
fi

if [ "$stopped" = true ]; then
    echo "Application stopped."
else
    echo "No running application found."
fi
