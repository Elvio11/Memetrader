#!/bin/bash
# NOFX Backend Startup Script
# Runs NOFX Go on port 8080

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export HERMES_HOME="$SCRIPT_DIR/.hermes"
echo "Using HERMES_HOME: $HERMES_HOME"

pkill -f "nofx" 2>/dev/null
pkill -f "nofx-bin" 2>/dev/null
sleep 1

echo "Starting NOFX Backend (port 8080)..."

if ! command -v go &> /dev/null; then
    echo "ERROR: Go not found. Please install Go."
    exit 1
fi

NOFX_BINARY="/tmp/nofx-bin"
if [ ! -f "$NOFX_BINARY" ]; then
    echo "Building NOFX binary..."
    cd "$SCRIPT_DIR/nofx"
    go build -o "$NOFX_BINARY" main.go
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to build NOFX"
        exit 1
    fi
fi

cd "$SCRIPT_DIR/nofx"
export RSA_PRIVATE_KEY="$(awk '{printf "%s\\n", $0}' /tmp/rsa.pem | sed 's/\\n$//')"
export JWT_SECRET="testsecret123456789012345678901234567890"
export DATA_ENCRYPTION_KEY="$(openssl rand -base64 32)"
export DB_TYPE=sqlite
export NOFX_BACKEND_PORT=8080
export TRANSPORT_ENCRYPTION=false

nohup "$NOFX_BINARY" >/tmp/nofx.log 2>&1 &
NOFX_PID=$!

echo "NOFX started (PID: $NOFX_PID), waiting for startup..."

sleep 5

if ps -p $NOFX_PID > /dev/null 2>&1; then
    echo "✓ NOFX process is running"
else
    echo "ERROR: NOFX process exited unexpectedly"
    tail -20 /tmp/nofx.log
    exit 1
fi

sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/status 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ]; then
    echo "✓ NOFX API responding on port 8080 (status: $HTTP_CODE)"
else
    echo "✓ NOFX returned: $HTTP_CODE"
fi

echo ""
echo "NOFX Backend running on http://localhost:8080"
echo "Logs: /tmp/nofx.log"