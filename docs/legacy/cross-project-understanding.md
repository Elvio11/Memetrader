# Cross-Project Understanding

## How the Three Projects Connect

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MEMETRADER UNIFIED                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐         ┌──────────────────┐         ┌────────────┐│
│  │    Hermes        │         │     NOFX         │         │  NOFX UI   ││
│  │    Python       │────────▶│     Go           │────────▶│  React     ││
│  │    AI Agent     │   API    │   Trading        │   API   │  Frontend  ││
│  │    Port 8643   │  :8080  │   Port 8080     │  :3000  │            ││
│  └──────────────────┘         └──────────────────┘         └────────────┘│
│           │                              │                                 │
│           │                              │                                 │
│           ▼                              ▼                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        60+ Tools (Hermes)                           │  │
│  │   Files • Terminal • Web • Browser • Vision • Code • Memory • Trading  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Connection 1: Hermes → NOFX

**Integration File**: `tools/nofx_trading_tool.py`

Hermes Agent communicates with NOFX Go backend via REST API calls:

| Hermes Tool | NOFX Endpoint | Purpose |
|-----------|---------------|---------|
| `nofx_trade` | POST /api/trades | Execute a trade |
| `nofx_portfolio` | GET /api/portfolio | Get portfolio holdings |
| `nofx_positions` | GET /api/positions | Get open positions |
| `nofx_strategies` | GET/POST /api/strategies | List/create strategies |
| `nofx_account` | GET /api/account | Get account info |
| `nofx_exchanges` | GET /api/exchanges | List connected exchanges |

**Configuration (config.yaml)**:
```yaml
nofx:
  enabled: true
  api_url: http://localhost:8080
  api_token: your-jwt-token-here
```

**Environment Variables**:
- `NOFX_API_URL`: Default `http://localhost:8080`
- `NOFX_API_TOKEN`: Bearer token for authentication

**Code Location**: `tools/nofx_trading_tool.py:164` - registered in `model_tools.py`

---

### Connection 2: NOFX → Exchange

**Integration File**: `nofx/trader/` - Go exchange connectors

NOFX connects to 15+ cryptocurrency exchanges:

| Exchange | Type | Connector |
|----------|------|-----------|
| Binance | CEX | `trader/binance/` |
| Bybit | CEX | `trader/bybit/` |
| OKX | CEX | `trader/okx/` |
| Bitget | CEX | `trader/bitget/` |
| KuCoin | CEX | `trader/kucoin/` |
| Gate | CEX | `trader/gate/` |
| Hyperliquid | DEX | `trader/hyperliquid/` |
| Aster DEX | DEX | `trader/aster/` |
| Lighter | DEX | `trader/lighter/` |

---

### Connection 3: NOFX → NOFX UI

**Integration File**: `nofx-ui/src/lib/api.ts`

NOFX UI (React frontend) queries NOFX Go backend:

```typescript
// API client connects to NOFX Go on port 8080
const API_BASE = 'http://localhost:8080/api';
```

| Frontend Page | API Endpoint | Data |
|---------------|--------------|------|
| Dashboard | GET /api/status | System status |
| Dashboard | GET /api/account | Account info |
| Dashboard | GET /api/positions | Open positions |
| Dashboard | GET /api/decisions | Decision logs |
| Strategy Studio | GET/POST /api/strategies | Trading strategies |

---

## Data Flow

### Trading Flow Diagram

```
┌─────────┐     ┌──────────────┐     ┌─────────┐     ┌───────────┐     ┌──────────┐
│  User   │────▶│  Hermes    │────▶│  NOFX   │────▶│  Exchange │────▶│ Market   │
│ Message │     │  AI Agent  │     │   Go    │     │    API    │     │  Data    │
└─────────┘     └──────────────┘     └─────────┘     └───────────┘     └──────────┘
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │  NOFX UI   │
                                    │  Dashboard │
                                    └─────────────┘
```

### Step-by-Step Flow

1. **User Request**: User sends message to Hermes (CLI, Telegram, Discord, etc.)
2. **AI Decision**: Hermes AI analyzes request, decides on trading action
3. **Tool Call**: Hermes executes `nofx_trade` tool with parameters
4. **API Call**: `nofx_trading_tool.py` sends POST to NOFX `/api/trades`
5. **Execution**: NOFX Go validates and executes on exchange
6. **Confirmation**: NOFX returns trade result to Hermes
7. **Display**: User sees result in chat; can also view in NOFX UI dashboard

---

## Shared Dependencies

### Duplicate Frontend Code

**Issue**: Two identical frontend directories exist:

| Directory | Status |
|-----------|--------|
| `nofx/web/` | Original NOFX React frontend |
| `nofx-ui/` | Duplicate (appears to be merge artifact) |

Both contain:
- Same `package.json` dependencies
- Same `src/` structure with pages, components, lib/api.ts

**Action Needed**: Consolidate to single frontend (recommend keeping `nofx-ui/`)

---

### Paper Trading vs Live Trading

**Unclear Relationship**:

| Component | Location | Purpose |
|-----------|----------|---------|
| Paper Trading | `tools/trading/` | Simulated trading in Hermes |
| Live Trading | `tools/nofx_trading_tool.py` | Real trading via NOFX |

**Question**: Should NOFX replace paper trading, or coexist?

---

## Database Separation

| Project | Database | Location |
|---------|----------|----------|
| Hermes | SQLite (FTS5) | `~/.hermes/hermes.db` |
| NOFX | SQLite | `nofx/data/nofx.db` |

**Note**: Separate databases; no shared state between projects.

---

## Integration Summary

| Integration | Type | Status | Notes |
|------------|------|--------|-------|
| Hermes → NOFX | REST API | ✅ Working | 6 tools defined |
| NOFX → Exchanges | Go Connectors | ✅ Working | 15+ exchanges |
| NOFX → NOFX UI | REST API | ✅ Working | Axios calls |
| Authentication | JWT | ⚠️ Partial | Configured but not enforced |

---

## Port Mapping

| Service | Port | Protocol |
|---------|------|----------|
| Hermes FastAPI | 8643 | HTTP |
| Hermes Gateway | 8642 | WebSocket/HTTP |
| Hermes UI (deprecated) | 8686 | HTTP |
| NOFX Go | 8080 | HTTP |
| NOFX UI (dev) | 3000 | HTTP |

---

## Next Steps

See [development-guide.md](development-guide.md) for how to develop new features across projects.