# MemeTrader Local Setup Guide for DEX-Only Trading

This guide provides step-by-step instructions for setting up MemeTrader locally for DEX-only trading strategies, enabling you to test the $10 → $100K goal using direct Hermes DEX tools without requiring NOFX backend involvement.

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Repository Setup](#2-repository-setup)
3. [Backend Setup (NOFX)](#3-backend-setup-nofx)
4. [Hermes Setup (Python AI Agent)](#4-hermes-setup-python-ai-agent)
5. [Frontend Setup (NOFX-UI)](#5-frontend-setup-nofx-ui)
6. [Service Initialization & Testing](#6-service-initialization--testing)
7. [Testing Strategy for $10 → $100K Goal](#7-testing-strategy-for-10--100k-goal)
8. [Troubleshooting](#8-troubleshooting)
9. [Next Steps](#9-next-steps)

## 1. Prerequisites

### System Requirements
- **Python 3.12+** (verified compatible with 3.12.1)
- **Node.js 18+ LTS** (for NOFX-UI React frontend)
- **Go 1.20+** (for NOFX backend)
- **Git** (for repository management)
- **SQLite** (typically pre-installed on most systems)

### Verification Commands
After installation, verify:
```bash
python3 --version  # Should show 3.12.x
node --version     # Should show v18.x or higher
go version         # Should show go1.20.x or higher
git --version
```

## 2. Repository Setup

### Clone Repository
```bash
git clone https://github.com/Elvio11/Memetrader.git
cd Memetrader
```

### Initial Directory Structure
Confirm these key directories exist:
```
memetrader/
├── gateway/          # Hermes FastAPI server (Port 8643)
├── hermes_cli/       # CLI interface
├── hermes_agent/     # Core agent logic
├── nofx/             # Go-based trading backend (Port 8080)
├── nofx-ui/          # React frontend (Port 3000)
├── tools/            # 60+ trading/data/source tools
├── mcp-servers/      # External MCP integrations
└── external-repos/   # Cloned GitHub integrations
```

## 3. Backend Setup (NOFX - Go Trading Engine)

### Go Dependencies & Build
```bash
cd nofx
go mod download        # Download dependencies
# Build command may vary - check for Makefile or build script
go build -o nofx ./cmd/nofx  # Adjust path if needed
cd ..
```
*Note: If there's a Makefile, you might use `make build` instead*

### NOFX Configuration
```bash
mkdir -p ~/.nofx
# Create config based on defaults or copy example if exists
# Example structure for ~/.nofx/config.yaml:
# server:
#   address: ":8080"
#   mode: "devtest"  # or "paper", "testnet"
# dex:
#   solana:
#     rpc_url: "https://api.devnet.solana.com"
```

### NOFX Environment Variables
Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
export NOFX_API_URL="http://localhost:8080"
export NOFX_API_TOKEN=""  # Empty for local testing if auth disabled
```

## 4. Hermes Setup (Python AI Agent)

### Python Virtual Environment (Strongly Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR .\venv\Scripts\activate  # Windows
```

### Python Dependencies
```bash
pip install --upgrade pip
# Install from requirements file if exists
pip install -r requirements.txt  # or pyproject.toml
# If no explicit file, Hermes should work with standard library + requests
```

### Hermes Configuration Directory
```bash
mkdir -p ~/.hermes
```

### Create Hermes Config File (`~/.hermes/config.yaml`)
```yaml
# Single AI Configuration
model:
  default: "openrouter/anthropic/claude-3-haiku-20240307"  # Free tier option

# Providers (get free API keys from openrouter.ai if needed)
providers:
  openrouter:
    api_key: "${OPENROUTER_API_KEY}"  # Set in .env if desired

# Trading Configuration (NOFX)
nofx:
  enabled: true
  api_url: http://localhost:8080
  api_token: ""  # Set via NOFX_API_TOKEN env var

# Data Sources (mostly free tiers)
data_sources:
  coingecko:
    enabled: true
  dexscreener:
    enabled: true
  birdeye:
    enabled: true

# UI Settings
ui:
  theme: dark
  hermes_tab: true

# DEX Configuration (for direct Hermes tools)
dex:
  solana:
    agent_wallet_private_key: "${SOLANA_AGENT_KEY}"  # Set in .env
    main_wallet_address: "${SOLANA_MAIN_WALLET}"
  sui:
    agent_wallet_private_key: "${SUI_AGENT_KEY}"
    main_wallet_address: "${SUI_MAIN_WALLET}"
```

### Create Hermes Environment File (`~/.hermes/.env`)
```bash
# LLM Provider (get free key from openrouter.ai - optional for basic testing)
OPENROUTER_API_KEY="your_free_key_here"  # Optional - can leave empty for testing

# Solana Devnet Wallet (get from faucet: https://faucet.solana.com)
SOLANA_AGENT_KEY="your_devnet_wallet_private_key_base58"
SOLANA_MAIN_WALLET="your_devnet_main_wallet_address"

# SUI Devnet Wallet (get from faucet: https://faucet.devnet.sui.io/)
SUI_AGENT_KEY="your_sui_devnet_private_key"
SUI_MAIN_WALLET="your_sui_main_wallet_address"

# Optional: Increase logging for debugging
HERMES_LOG_LEVEL="info"
```

### Verify Hermes Dependencies
```bash
source venv/bin/activate
python -c "import tools.registry; print('Hermes tools registry loaded')"
python -c "from tools.coingecko_tool import coingecko_price; print('Coingecko tool ready')"
```

## 5. Frontend Setup (NOFX-UI - React)

### Node.js Dependencies
```bash
cd nofx-ui
npm install  # or yarn install
cd ..
```

### NOFX-UI Configuration
Create `.env` file in `nofx-ui/` directory:
```bash
REACT_APP_NOFX_API_URL=http://localhost:8080
REACT_APP_HERMES_API_URL=http://localhost:8643
REACT_APP_HERMES_WS_URL=ws://localhost:8643  # if using websockets
```

## 6. Service Initialization & Testing

### Startup Sequence (Recommended Order)

**Terminal 1: Start NOFX Backend**
```bash
cd nofx
./nofx  # or however the binary is started
# Should show: NOFX API listening on :8080
```

**Terminal 2: Start Hermes API**
```bash
source venv/bin/activate
cd gateway
python fastapi_server.py  # or however it's started
# Should show: Hermes FastAPI running on :8643
```

**Terminal 3: Start NOFX-UI**
```bash
cd nofx-ui
npm start  # or yarn start
# Should open browser at http://localhost:3000
```

### Verification Steps

**Check Service Health:**
- NOFX API: `curl -s http://localhost:8080/health` 
- Hermes API: `curl -s http://localhost:8643/health` or `/api/sessions`
- NOFX-UI: Should load in browser at `http://localhost:3000/hermes`

**Test Hermes CLI:**
```bash
source venv/bin/activate
hermes --help  # Should show available commands
hermes version  # Should show version info
```

**Test DEX Functionality (Devnet):**
```bash
# Test Jupiter swap (devnet) - microscopic amount to start
hermes dex_swap --input SOL --output USDC --amount 0.001 --dex jupiter --network devnet

# Test Raydium limit order (our implementation)
hermes raydium_limit_create --input SOL --output USDC --amount 1000000 --limit-price 0.001 --network devnet

# Test Aerodrome limit order (our implementation)
hermes aerodrome_limit_create --input SOL --output USDC --amount 1000000 --limit-price 0.001 --network devnet
```

## 7. Testing Strategy for $10 → $100K Goal

### Devnet-Only Testing Protocol

**Phase 1: Mechanics Validation (Day 1)**
- Test swap accuracy/slippage across all 3 DEXes with tiny amounts ($0.001)
- Verify limit order trigger mechanics
- Confirm transaction success on devnet explorers:
  - Solana: https://explorer.solana.com/?cluster=devnet
  - SUI: https://suiscan.xyz/devnet/tx/
  - Base: https://baserain.com/ (use sepolia testnet faucet)

**Phase 2: Strategy Development (Days 2-5)**
- Develop simple strategies using Hermes CLI:
  - Arbitrage scanning between DEXes
  - Limit order cascading (buy low/sell high orders)
  - Profit compounding rules
- Use `hermes memory_tool` to track all trades
- Implement basic risk management via CLI commands

**Phase 3: Scaling & Optimization (Week 2+)**
- Gradually increase trade sizes as consistency proven
- Test strategy across different market conditions (volatile/ranging)
- Optimize gas fees through DEX selection/juggling
- Implement automated profit-taking and stop-loss via Hermes automation

### Risk Management Essentials
- **Never exceed 1% of test capital per trade** during learning phase
- **Use only devnet/testnet funds** - get from official faucets
- **Maintain detailed trade journal** via Hermes memory system
- **Set hard daily loss limits** (e.g., stop if down 20% in day)
- **Validate each transaction** succeeds before increasing size

### Progression Checklist
Before increasing trade size, confirm:
- [ ] 10+ consecutive successful swap transactions
- [ ] Limit orders execute correctly at target prices
- [ ] Profit/loss calculations are accurate
- [ ] Transaction confirmation times are acceptable
- [ ] No failed transactions due to insufficient funds/slippage
- [ ] Strategy shows positive expectancy over 20+ trades

## 8. Troubleshooting

### Common Issues & Checks
- **Wallet not funded**: Verify devnet faucet dispensing worked
- **RPC endpoint issues**: Try alternative public RPCs if default fails
- **Transaction failed**: Check slippage tolerance or insufficient liquidity
- **API connection errors**: Verify services are running on correct ports
- **Permission errors**: Ensure proper file permissions on config files
- **Dependency conflicts**: Use clean virtual environments

### Log Locations
- Hermes logs: `stdout` of `fastapi_server.py` process
- NOFX logs: `stdout` of `nofx` binary process
- UI errors: Browser developer console

## 9. Next Steps After Local Validation

Once devnet testing shows consistent profitability:
1. Repeat verification on multiple chains (Solana devnet, SUI testnet, Base sepolia)
2. Test strategy robustness across different market conditions
3. Only then consider minimal mainnet exposure ($1-$5) with extreme caution
4. Scale up only after demonstrating >55% win rate and positive expectancy over 100+ trades

## Important Notes

### DEX-Only Trading Works Today
You can begin DEX-only trading strategy development and testing immediately using only the Hermes direct DEX tools:
- `/hermes dex_swap` - Direct DEX swap execution (all DEXes)
- `/hermes raydium_limit_create` / `query` / `cancel` - Raydium limit orders
- `/hermes aerodrome_limit_create` / `query` / `cancel` - Aerodrome limit orders
- `/hermes jupiter_limit_create` / `query` / `cancel` - Jupiter true limit orders
- `/hermes dex_grid_start` - DEX grid trading strategies
- `/hermes memory_tool` - Track trade history and outcomes
- `/hermes trade_analysis_tool` - Analyze performance

### Wallet Funding for Testing
- **Solana Devnet**: https://faucet.solana.com
- **SUI Devnet**: https://faucet.devnet.sui.io/
- **Base Sepolia**: https://sepoliafaucet.com/ or similar

### Security Best Practices
- Never commit private keys to git
- Use environment variables for secrets
- Start with microscopic amounts ($0.001) to validate mechanics
- Keep devnet and mainnet wallets completely separate
- Regularly rotate test wallet keys

## Quick Start Summary

```bash
# 1. Clone repo
git clone https://github.com/Elvio11/Memetrader.git
cd Memetrader

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies (if requirements.txt exists)
pip install -r requirements.txt

# 4. Setup directories and config files
mkdir -p ~/.hermes ~/.nofx
# Create ~/.hermes/config.yaml and ~/.hermes/.env (see above)
# Create ~/.nofx/config.yaml (see above)
# Create nofx-ui/.env (see above)

# 5. Start services
# Terminal 1: cd nofx && ./nofx
# Terminal 2: source venv/bin/activate && cd gateway && python fastapi_server.py
# Terminal 3: cd nofx-ui && npm start

# 6. Test DEX functionality
source venv/bin/activate
hermes dex_swap --input SOL --output USDC --amount 0.001 --dex jupiter --network devnet
```

You now have a complete DEX-only trading environment ready for strategy development and testing toward your $10 → $100K goal!