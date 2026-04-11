#!/bin/bash
set -e

echo "====================================="
echo "MemeTrader Setup - memetrader-unification"
echo "====================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Verifying branch${NC}"
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH (expected: memetrader-unification)"
if [ "$CURRENT_BRANCH" != "memetrader-unification" ]; then
    echo "WARNING: Not on memetrader-unification branch!"
    git checkout memetrader-unification || echo "Could not checkout branch"
fi
echo ""

echo -e "${BLUE}Step 2: Setting up Python virtual environment${NC}"
if [ ! -d ".venv" ]; then
    python3.12 -m venv .venv --copies
    echo "✓ Created virtual environment"
else
    echo "✓ Virtual environment already exists"
fi

source .venv/bin/activate
python --version
pip --version
echo ""

echo -e "${BLUE}Step 3: Installing core dependencies${NC}"
pip install --upgrade pip setuptools wheel
echo "✓ Core tools upgraded"
echo ""

echo -e "${BLUE}Step 4: Installing Hermes Agent with all extras${NC}"
echo "Installing: hermes-agent[dev,voice,messaging,cli,tts-premium,pty,honcho,mcp,homeassistant,sms,acp,cron,all,crypto]"
pip install -e ".[dev,voice,messaging,cli,tts-premium,pty,honcho,mcp,homeassistant,sms,acp,cron,crypto]" 2>&1 | tail -20
echo "✓ Hermes Agent installed"
echo ""

echo -e "${BLUE}Step 5: Verifying tool discovery${NC}"
python -c "import model_tools; tools = model_tools.get_all_tool_names(); print(f'✓ Discovered {len(tools)} tools'); print(f'  - web_search: {\"web_search\" in tools}'); print(f'  - browser tools: {any(\"browser\" in t for t in tools)}'); print(f'  - terminal: {\"terminal\" in tools}')" || echo "⚠ Tool verification skipped"
echo ""

echo -e "${BLUE}Step 6: Checking NOFX requirements${NC}"
if [ -f "nofx/requirements.txt" ]; then
    pip install -r nofx/requirements.txt 2>&1 | tail -10
    echo "✓ NOFX Python requirements installed"
elif [ -f "nofx/go.mod" ]; then
    echo "✓ NOFX is a Go project (backend setup requires Go)"
else
    echo "⚠ No NOFX requirements found"
fi
echo ""

echo -e "${BLUE}Step 7: Checking Node/npm for NOFX React UI${NC}"
if command -v node &> /dev/null; then
    echo "Node version: $(node --version)"
    echo "npm version: $(npm --version)"
    if [ -d "nofx-ui" ] && [ -f "nofx-ui/package.json" ]; then
        echo "Installing nofx-ui dependencies..."
        cd nofx-ui && npm ci 2>&1 | tail -10 && cd ..
        echo "✓ NOFX UI dependencies installed"
    fi
else
    echo "⚠ Node.js not detected"
fi
echo ""

echo -e "${BLUE}Step 8: Git configuration for memetrader branch${NC}"
echo "Git remotes:"
git remote -v | grep -E 'origin|upstream'
echo ""
echo "Branch tracking:"
git branch -vv | grep memetrader
echo ""

echo -e "${GREEN}====================================="
echo "✓ MemeTrader setup complete!"
echo "=====================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Hermes Agent: source .venv/bin/activate && python -m hermes_cli.main"
echo "  2. NOFX Backend:  cd nofx && go run ."
echo "  3. NOFX UI:       cd nofx-ui && npm run dev"
echo ""
echo "Port mapping:"
echo "  - Hermes API:      http://localhost:8643"
echo "  - Hermes Gateway:  http://localhost:8642"
echo "  - NOFX Backend:    http://localhost:8080"
echo "  - NOFX React UI:   http://localhost:3000"
echo ""
