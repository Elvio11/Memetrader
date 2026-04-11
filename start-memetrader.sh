#!/bin/bash
# MemeTrader Unified Startup Script
# Starts all services: Hermes FastAPI, Hermes Gateway, NOFX Backend, NOFX UI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🚀 MemeTrader - Starting All Services      ║"
echo "╚════════════════════════════════════════════════════════════╝"

# ============================================================
# 1. Cleanup Old Processes
# ============================================================
echo ""
echo "[1/5] Cleaning up old processes..."
pkill -f "python.*fastapi_server" 2>/dev/null
pkill -f "hermes.*gateway" 2>/dev/null
pkill -f "go run main.go" 2>/dev/null
pkill -f "vite.*port.*3000" 2>/dev/null
sleep 2

# ============================================================
# 2. Start Hermes FastAPI (8643)
# ============================================================
echo "[2/5] Starting Hermes FastAPI (port 8643)..."
export HERMES_HOME="$SCRIPT_DIR/.hermes"
nohup python3 -m gateway.fastapi_server >/tmp/hermes-fastapi.log 2>&1 &
FASTAPI_PID=$!
echo "    PID: $FASTAPI_PID"

# ============================================================
# 3. Start Hermes Gateway (8642) - Optional
# ============================================================
echo "[3/5] Starting Hermes Gateway (port 8642)..."
nohup .venv/bin/hermes gateway run >/tmp/hermes-gateway.log 2>&1 &
GATEWAY_PID=$!
echo "    PID: $GATEWAY_PID"

# Wait for Hermes services
sleep 6

# ============================================================
# 4. Start NOFX Go Backend (8080)
# ============================================================
echo "[4/5] Starting NOFX Backend (port 8080)..."
cd "$SCRIPT_DIR/nofx"
nohup go run main.go >/tmp/nofx-backend.log 2>&1 &
NOFX_PID=$!
echo "    PID: $NOFX_PID"

# Wait for NOFX to start
sleep 5

# ============================================================
# 5. Start NOFX React UI (3000)
# ============================================================
echo "[5/5] Starting NOFX UI (port 3000)..."
cd "$SCRIPT_DIR/nofx-ui"
nohup ./node_modules/.bin/vite --host 0.0.0.0 --port 3000 >/tmp/nofx-ui.log 2>&1 &
UI_PID=$!
echo "    PID: $UI_PID"

# Wait for UI to start
sleep 8

# ============================================================
# Final Status Check
# ============================================================
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ✅ MemeTrader - All Running!               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "  Port   Service           URL"
echo "  ----- ----------------- ---------------------------------------"
echo "  8643  Hermes FastAPI    http://127.0.0.1:8643"
echo "  8642  Hermes Gateway   http://127.0.0.1:8642"
echo "  8080  NOFX Backend    http://127.0.0.1:8080"
echo "  3000  NOFX UI         http://127.0.0.1:3000"
echo ""
echo "  Logs: /tmp/hermes-fastapi.log, /tmp/hermes-gateway.log,"
echo "        /tmp/nofx-backend.log, /tmp/nofx-ui.log"
echo ""
echo "  To stop: pkill -f 'python.*fastapi_server|go run main.go|vite'"
echo "=============================================="

# Health check
sleep 2
echo ""
echo "Health Checks:"
curl -s http://127.0.0.1:8643/health | python3 -c "import sys,json;d=json.load(sys.stdin);print('  8643:',d.get('status','ok'))"
curl -s http://127.0.0.1:8080/api/health | python3 -c "import sys,json;d=json.load(sys.stdin);print('  8080:',d.get('status','ok'))"