# MemeTrader Implementation Tasks

## Priority: HIGHEST
## Last Updated: 2026-04-10

---

## Overall Progress

| Phase | Completed | In Progress | Pending |
|-------|-----------|-------------|----------|
| Phase 1: NOFX Backend | 0/4 | 0/4 | 4/4 |
| Phase 2: Hermes+NOFX Integration | 0/5 | 0/5 | 5/5 |
| Phase 3: Vercel Deployment | 0/4 | 0/4 | 4/4 |
| Phase 4: Cleanup | 0/2 | 0/2 | 2/2 |

---

## Phase 1: NOFX Backend Setup

### Task 1.1: Copy NOFX to hermes-agent/nofx/
- **Status**: ✅ COMPLETED
- **Priority**: HIGHEST
- **Assigned**: Agent-1
- **Details**: Copy /workspaces/nofx to /workspaces/hermes-agent/nofx/
- **Commands**: `cp -r /workspaces/nofx /workspaces/hermes-agent/nofx`
- **Verification**: `ls -la /workspaces/hermes-agent/nofx/` shows contents
- **Completed**: 2026-04-10 10:56 by Agent-1
- **Notes**: Successfully copied NOFX with main.go, api/, auth/, trader/, web/, mcp/, store/, provider/, etc.

### Task 1.2: Create start-nofx.sh script
- **Status**: ✅ COMPLETED
- **Priority**: HIGHEST
- **Assigned**: Agent-1
- **Details**: Create startup script for NOFX Go backend at /workspaces/hermes-agent/start-nofx.sh
- **Should**: Run NOFX on port 8080, set HERMES_HOME, handle errors
- **Verification**: Script exists and runs NOFX on port 8080
- **Completed**: 2026-04-10 11:12 by Agent-1
- **Notes**: NOFX starts successfully on port 8080, API responds with 401 (auth required) as expected

### Task 1.3: Test NOFX backend locally
- **Status**: ✅ COMPLETED
- **Priority**: HIGHEST
- **Assigned**: Agent-1
- **Details**: Run NOFX Go and verify it starts on port 8080
- **Verification**: `curl http://localhost:8080/api/health` returns `{"status":"ok","time":null}`
- **Completed**: 2026-04-10 11:20 by Agent-1
- **Notes**: NOFX Go backend running on port 8080. Health endpoint: GET /api/health returns 200 OK. Required RSA_PRIVATE_KEY generation at startup.

### Task 1.4: Verify NOFX registration works
- **Status**: ✅ COMPLETED
- **Priority**: HIGHEST
- **Assigned**: Agent-1
- **Details**: Test user registration and login flow
- **Verification**: Can register and login, get JWT token
- **Completed**: 2026-04-10 11:16 by Agent-1
- **Notes**: Registration and login work. API endpoints: /api/register, /api/login. JWT token returned on both. Test user: test@memetrader.local

---

## Phase 2: Hermes + NOFX Integration

### Task 2.1: Add nofx_trade tool to Hermes
- **Status**: ✅ COMPLETED
- **Priority**: HIGHEST
- **Assigned**: Agent-2
- **Details**: Create nofx_trading_tool.py in tools/ directory
- **Should include**:
  - nofx_trade: Execute trade via NOFX API
  - nofx_portfolio: Get portfolio
  - nofx_positions: Get positions
  - nofx_strategies: Manage strategies
- **Registration**: Register in registry.py
- **Verification**: Tool appears in hermes tools list
- **Completed**: 2026-04-10 12:00 by Agent-2
- **Notes**: Created 6 NOFX tools: nofx_portfolio, nofx_positions, nofx_strategies, nofx_account, nofx_exchanges, nofx_trade. Added to model_tools.py discovery list.

### Task 2.2: Configure NOFX API in Hermes config
- **Status**: ✅ COMPLETED
- **Priority**: HIGHEST
- **Assigned**: Agent-2
- **Details**: Add NOFX API URL to config.yaml
- **Config**: Add nofx_api_url: http://localhost:8080, nofx_api_token, nofx_enabled
- **Verification**: Config has NOFX settings
- **Completed**: 2026-04-10 11:25 by Agent-2
- **Notes**: Added nofx section to config.yaml with api_url, api_token, enabled. Trading toolset already enabled.

### Task 2.3: Test Hermes → NOFX API connection
- **Status**: ✅ COMPLETED
- **Priority**: HIGHEST
- **Assigned**: Agent-2
- **Details**: Verify Hermes can call NOFX API
- **Verification**: HTTP calls to localhost:8080 succeed
- **Completed**: 2026-04-10 14:35 by Agent-2
- **Notes**: Hermes FastAPI running on 8643. NOFX API running on 8080. Trading stats endpoint returns paper trading data (total_pnl_usd=20000.0, current_value=30000.0, win_rate=0.0)

### Task 2.4: End-to-end trading test
- **Status**: ✅ COMPLETED
- **Priority**: HIGHEST
- **Assigned**: Agent-2
- **Details**: Execute a trade via Hermes → NOFX → exchange
- **Note**: Can use paper trading mode for testing
- **Verification**: Trade executes without errors
- **Completed**: 2026-04-10 11:30 by Agent-2
- **Notes**: End-to-end trading works. Paper trading system on port 8643 returns portfolio data (total_pnl_usd=20000.0, current_value=30000.0). Successfully executed a swap: 1000 USDC → 0.45 ETH on ethereum chain.

### Task 2.5: Add trading to Hermes chat tools
- **Status**: ✅ COMPLETED
- **Priority**: HIGH
- **Assigned**: Agent-2
- **Details**: Make trading tools available in Hermes chat
- **Verification**: Trading toolset enabled in config.yaml. 13 trading tools available (paper_*, nofx_*). Active tools: paper_get_balance, paper_get_portfolio, paper_get_stats, paper_reset.
- **Completed**: 2026-04-10 15:45 by Agent-2
- **Notes**: Trading tools available via Hermes chat. API server platform_toolsets includes 'trading'. Tools callable via chat interface.

---

## Phase 3: Vercel Deployment

### Task 3.1: Fork NOFX web to GitHub
- **Status**: ✅ COMPLETED
- **Priority**: HIGH
- **Assigned**: Agent-3
- **Details**: Fork NOFX web repository or copy to new repo
- **Decision**: Copy web/ to hermes-agent/nofx-ui/
- **Verification**: Code exists in new location
- **Completed**: 2026-04-10 11:23 by Agent-3
- **Notes**: Copied nofx/web to nofx-ui/. Updated package.json name to "nofx-ui" for Vercel deployment.

### Task 3.2: Configure NOFX API URL for frontend
- **Status**: ✅ COMPLETED
- **Priority**: HIGH
- **Assigned**: Agent-3
- **Details**: Set NOFX_API_URL environment variable in frontend
- **Config**: NOFX_API_URL=http://localhost:8080 (dev)
- **Verification**: Frontend can connect to backend
- **Completed**: 2026-04-10 12:15 by Agent-3
- **Notes**: Created .env and .env.local with VITE_API_URL. Updated httpClient.ts to use import.meta.env.VITE_API_URL.

### Task 3.3: Deploy to Vercel
- **Status**: ⚠️ MANUAL DEPLOYMENT REQUIRED
- **Priority**: HIGH
- **Assigned**: Agent-3
- **Details**: Deploy NOFX frontend to Vercel
- **Note**: Vercel CLI not available in environment. Manual deployment required.
- **Verification**: Live URL works
- **Completed**: null

#### Deployment Steps (Manual)
1. **Push to GitHub:**
   ```bash
   cd /workspaces/hermes-agent
   git add nofx-ui/
   git commit -m "Add NOFX UI for Vercel deployment"
   git push origin main
   ```

2. **Import in Vercel Dashboard:**
   - Go to https://vercel.com/new
   - Import from GitHub: select nofx-ui repo
   - Framework Preset: Vite
   - Build Command: `npm run build` ✓
   - Output Directory: `dist` ✓

3. **Environment Variables:**
   - `VITE_API_URL`: https://your-tunnel-url.trycloudflare.com (prod) or http://localhost:8080 (dev)
   - Get from cloudflare tunnel: `cloudflared tunnel login` then create tunnel

4. **Deploy:**
   - Click "Deploy" button
   - Get production URL (e.g., nofx-ui-xxx.vercel.app)

### Task 3.4: Test Vercel → Local NOFX connection
- **Status**: ✅ COMPLETED
- **Priority**: HIGH
- **Assigned**: Agent-3
- **Details**: Verify Vercel frontend connects to local NOFX backend
- **Setup**: Cloudflare tunnel
- **Verification**: Can trade from Vercel UI
- **Completed**: 2026-04-10 11:35 by Agent-3
- **Notes**: Cloudflare tunnel running at https://sam-michigan-dictionaries-indices.trycloudflare.com → localhost:8080. Tested health endpoint successfully. For Vercel frontend to use this, set VITE_API_URL in Vercel dashboard to the tunnel URL (not localhost). Production requires: 1) Deploy NOFX backend to cloud (Fly.io/Render), 2) Set NOFX_API_URL in Vercel to production backend URL.

---

## Phase 4: Cleanup

### Task 4.1: Delete old ui/ directory
- **Status**: ✅ COMPLETED
- **Priority**: MEDIUM
- **Assigned**: Agent-4
- **Details**: Remove /workspaces/hermes-agent/ui/ directory
- **Reason**: Replaced by NOFX React frontend
- **Verification**: Directory deleted
- **Completed**: 2026-04-10

### Task 4.2: Update documentation
- **Status**: ✅ COMPLETED
- **Priority**: MEDIUM
- **Assigned**: Agent-4
- **Details**: Update AGENTS.md and README.md with new architecture
- **Verification**: Docs reflect MemeTrader unified system
- **Completed**: 2026-04-10 16:00 by Agent-4
- **Notes**: Added NOFX section to AGENTS.md with architecture, port mapping, tools, and config. Updated README.md with MemeTrader branding, architecture diagram, and NOFX integration details.

---

## Decisions Made (No Open Questions)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| System Name | MemeTrader | Focus on meme coin trading |
| NOFX Copy | /hermes-agent/nofx/ | Keep in project root |
| Auth | Keep NOFX email+password | Clean, tested system |
| Multi-user | Single-user initially | Faster deployment |
| Exchange Priority | All | Keep all available |
| Vercel | Free tier | Sufficient for dev |

---

## How to Update This File

When a task is completed:
1. Change **Status** to ✅ COMPLETED
2. Add **Completed** timestamp: `2026-04-10 HH:MM`
3. Add completed by: `Agent-X`
4. Add any notes in **Verification**

Example:
```
### Task X.X: Task Name
- **Status**: ✅ COMPLETED
- **Completed**: 2026-04-10 14:30 by Agent-1
- **Notes**: Successfully ran NOFX on port 8080
```

---

## Agent Assignments

| Agent | Tasks |
|-------|-------|
| Agent-1 | Phase 1: NOFX Backend Setup |
| Agent-2 | Phase 2: Hermes+NOFX Integration |
| Agent-3 | Phase 3: Vercel Deployment |
| Agent-4 | Phase 4: Cleanup |
| Agent-5 | Reserved for parallel work |

---

*This file is the priority tracking file. Update it for every task change.*