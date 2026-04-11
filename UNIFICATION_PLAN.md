# MemeTrader Unification Plan
## Hermes Agent + NOFX Integration

---

## 1. Executive Summary

This document outlines the strategic plan to unify **Hermes Agent** (Python AI agent with 60+ tools) with **NOFX** (Go-based trading system) into a single unified platform called **MemeTrader**. The unification combines Hermes' powerful AI capabilities with NOFX's real-money trading across 15+ exchanges, creating a comprehensive AI-powered trading platform.

**Vision:** Hermes becomes the primary AI interface while NOFX handles all real trading execution, enabling fully autonomous AI trading with professional-grade tooling.

---

## 2. Background and Motivation

### 2.1 What is Hermes Agent?

Hermes Agent is a Python-based AI agent system featuring:
- **60+ built-in tools**: file operations, terminal execution, web search, browser automation, code execution, vision analysis, MCP integrations
- **Multiple interfaces**: CLI, Telegram, Discord, Slack, WhatsApp, Signal
- **Session management**: SQLite-backed conversation history with FTS5 search
- **Memory system**: Long-term memory with semantic search
- **Model flexibility**: Support for Anthropic, OpenAI, OpenCode, Ollama, and custom providers
- **Prompt caching**: Context compression and prompt optimization

**Current limitation:** Paper trading only (no real money execution)

### 2.2 What is NOFX?

NOFX is a Go-based trading system providing:
- **Multi-exchange support**: Binance, Bybit, OKX, Hyperliquid, KuCoin, Gate, Bitget, Mexc, BingX, Woo, CryptoCom, Bitfinex, HollaEx, BitMart, AscendEx
- **Real trading**: Live order execution, position management, portfolio tracking
- **Professional UI**: React dashboard, strategy studio, trading interface
- **Authentication**: Email + password → JWT (24h expiration)
- **x402 payments**: USDC wallet integration for premium features
- **Telegram bot**: Built-in trading notifications and commands

**Current limitation:** Limited AI integration (basic MCP only)

### 2.3 Why the Unification?

| Capability | Hermes Agent | NOFX |
|------------|-------------|------|
| AI Intelligence | ✅ 60+ tools | ❌ Basic |
| Real Trading | ❌ Paper only | ✅ 15+ exchanges |
| Professional UI | ❌ Basic CLI | ✅ React dashboard |
| Memory/Skills | ✅ SQLite + custom | ❌ None |
| Auth System | ❌ None | ✅ JWT |
| Payments | ❌ None | ✅ x402/USDC |

**The solution:** Combine the best of both worlds:
- **Hermes** provides the AI brain (reasoning, planning, tool use)
- **NOFX** provides the trading execution and professional UI

---

## 3. Current State Analysis

### 3.1 What's Already Done (Hermes)

| Component | Status | Details |
|-----------|--------|---------|
| FastAPI Server | ✅ Running | Port 8643 - full REST API |
| Gateway | ✅ Running | Port 8642 - messaging platforms |
| Config base_url | ✅ Fixed | `https://opencode.ai/zen/v1` |
| Model ID normalization | ✅ Fixed | Strips provider prefix |
| Session create endpoint | ✅ Fixed | Working |
| UI endpoint | ✅ Fixed | Points to FastAPI (8643) |
| start-hermes.sh | ✅ Working | Script exists |
| config.yaml | ✅ Configured | OpenCode Zen models |

### 3.2 What's Running Now

```
Port 8643: FastAPI (Hermes)
  ├── /chat - AI chat endpoint
  ├── /sessions - Session management
  ├── /memory - Long-term memory
  ├── /jobs - Background jobs
  ├── /skills - Skill management
  ├── /config - Configuration
  └── /trading - Trading endpoints

Port 8642: Gateway (Hermes)
  ├── Telegram bot
  ├── Discord bot
  ├── Slack bot
  └── WhatsApp integration

Port 8686: UI (TanStack Start - Old Hermes UI)
```

### 3.3 NOFX (Cloned to /workspaces/nofx)

```
/workspaces/nofx/
├── main.go              # Go entry point
├── api/                 # REST API endpoints
├── auth/                # JWT authentication
├── trader/              # Trading engine (13 subdirs)
├── web/                 # React frontend
├── mcp/                 # AI provider integrations
├── store/               # SQLite storage
├── config/              # Configuration
├── provider/            # Exchange connectors (15+)
├── telegram/            # Telegram bot
├── wallet/              # USDC/x402 payments
└── market/              # Market data
```

---

## 4. The Unification Plan

### Phase 1: Setup NOFX Backend (Local)

**Goal:** Run NOFX Go backend alongside Hermes

- Run NOFX Go on port 8080
- Test registration and login flow
- Verify exchange connections
- Test basic trading operations

**Commands:**
```bash
cd /workspaces/nofx
./start.sh  # or go run main.go
```

### Phase 2: Connect Hermes to NOFX Trading

**Goal:** Enable Hermes to execute real trades via NOFX

- Add `nofx_trade` tool to Hermes tools
- Add `nofx_portfolio` tool for portfolio viewing
- Add `nofx_positions` tool for position tracking
- Add `nofx_strategy` tool for strategy management
- Test end-to-end: Hermes AI → NOFX API → Exchange

### Phase 3: Deploy NOFX Frontend to Vercel

**Goal:** Professional trading UI accessible via web

- Fork NOFX web repository
- Deploy to Vercel (free tier)
- Connect to localhost NOFX via tunnel (Cloudflare)
- Configure CORS and authentication

### Phase 4: Full Integration

**Goal:** Complete unified trading platform

- Trading via Hermes AI commands
- Strategy management via Hermes
- Wallet integration (deposits/withdrawals)
- Unified authentication flow

---

## 5. Architecture Diagram

### Development Environment

```
┌─────────────────────────────────────────────────────────────┐
│                     MemeTrader (Unified)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌────────────┐ │
│  │   Hermes     │     │    NOFX      │     │   NOFX     │ │
│  │   Python     │────▶│     Go       │────▶│   React    │ │
│  │   AI Agent   │     │   Trading    │     │   Frontend │ │
│  │   Port 8643  │     │   Port 8080  │     │  :3000/    │ │
│  └──────────────┘     └──────────────┘     │  Vercel    │ │
│         │                   │              └────────────┘ │
│         │                   │                                  │
│         ▼                   ▼                                  │
│  ┌──────────────────────────────────────┐                   │
│  │         60+ Tools                    │                   │
│  │  Files, Terminal, Web, Browser,     │                   │
│  │  Vision, Code, Memory, Skills        │                   │
│  └──────────────────────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

External Connections:
  • 15+ Exchanges (Binance, Bybit, OKX, Hyperliquid...)
  • Messaging Platforms (Telegram, Discord, Slack)
  • Vercel (Frontend)
```

### Production Environment (Future)

```
┌─────────────────────────────────────────────────────────────┐
│                     Production MemeTrader                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Hermes Agent ──▶ NOFX Go ──▶ Exchanges                    │
│  (Flux Cloud)    (Cloud)     (15+)                         │
│                                                             │
│  NOFX React ──▶ Vercel (Frontend)                          │
│                                                             │
│  Gateway ──▶ Telegram/Discord/Slack                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. What Each System Handles

| Component | System | Responsibility |
|-----------|--------|----------------|
| **AI Agent** | Hermes | 60+ tools for files, terminal, web, browser, vision, code execution, MCP |
| **Trading Execution** | NOFX | 15+ exchange connections, order placement, position management |
| **Trading UI** | NOFX | Dashboard, charts, strategy builder, portfolio view |
| **x402 Payments** | NOFX | USDC wallet, premium feature payments |
| **Memory/Skills** | Hermes | SQLite session storage, custom skill loading |
| **Messaging** | Hermes Gateway | Telegram, Discord, Slack, WhatsApp, Signal |
| **Authentication** | NOFX | Email + password → JWT (24h) |
| **Market Data** | NOFX | Price feeds, order books, historical data |

---

## 7. File Changes

### NOFX to Copy

Copy entire `/workspaces/nofx` to `/workspaces/hermes-agent/nofx/`:

| Directory | Purpose |
|-----------|---------|
| `nofx/main.go` | Go entry point |
| `nofx/api/` | REST API endpoints |
| `nofx/auth/` | JWT authentication |
| `nofx/trader/` | Trading engine |
| `nofx/web/` | React frontend (deploy to Vercel) |
| `nofx/mcp/` | AI provider integrations |
| `nofx/store/` | SQLite storage |
| `nofx/provider/` | Exchange connectors |
| `nofx/telegram/` | Telegram bot |
| `nofx/wallet/` | USDC/x402 payments |

### Delete After Migration

| Directory | Reason |
|-----------|--------|
| `ui/` | Old Hermes UI - replaced by NOFX React |
| `archive/` | Old plans - superseded by this document |

---

## 8. Implementation Steps with Status

| Step | Task | Status |
|------|------|--------|
| 1 | Copy NOFX to `hermes-agent/nofx/` | ⏳ Pending |
| 2 | Update `start-hermes.sh` to run NOFX | ⏳ Pending |
| 3 | Add NOFX trading tools to Hermes | ⏳ Pending |
| 4 | Test Hermes → NOFX trading | ⏳ Pending |
| 5 | Deploy NOFX React to Vercel | ⏳ Pending |
| 6 | Delete old `ui/` directory | ⏳ Pending |
| 7 | Update documentation | ⏳ Pending |

---

## 9. Why This Migration?

### Current Problem

```
Hermes Agent:
  ✅ Powerful AI (60+ tools)
  ✅ Multiple interfaces
  ✅ Memory & sessions
  ❌ Paper trading only
  
NOFX:
  ✅ Real trading (15+ exchanges)
  ✅ Professional UI
  ✅ Auth & payments
  ❌ Limited AI integration
```

### The Solution

```
MemeTrader (Unified):
  ✅ Hermes AI (60+ tools) + NOFX trading (15+ exchanges)
  ✅ Professional UI (React) + CLI (Hermes)
  ✅ Full AI capabilities + real money
  ✅ Memory/sessions from Hermes
  ✅ Auth/payments from NOFX
```

### Benefits

1. **AI-Powered Trading**: Use Hermes' 60+ tools to research, analyze, and execute trades
2. **Professional Interface**: NOFX React UI for manual trading and strategy management
3. **Multi-Exchange**: Access 15+ exchanges from a single platform
4. **Unified Auth**: Single sign-on for both AI and trading
5. **Payment Ready**: x402/USDC for premium features

---

## 10. Open Questions for Discussion

### Q1: Multi-User Support

**Option A:** Keep single-user (current NOFX)
- Simpler, faster to implement
- Personal trading assistant use case

**Option B:** Modify for multi-user
- Proper user isolation
- Shareable strategies
- Team trading

**Recommendation:** Start with single-user (Option A) for faster deployment

### Q2: Exchange Priority

Which exchanges should be prioritized for initial integration?

| Priority | Exchanges |
|----------|-----------|
| Tier 1 | Binance, Bybit, OKX, Hyperliquid |
| Tier 2 | KuCoin, Gate, Bitget, Mexc |
| Tier 3 | Others (Woo, CryptoCom, etc.) |

**Recommendation:** Focus on Tier 1 first (Binance, Bybit, OKX, Hyperliquid)

### Q3: Vercel Deployment Details

**Questions:**
1. Which Vercel plan? (Free tier sufficient?)
2. Custom domain? (memetrader.ai or similar)
3. Environment variables for API URL
4. Authentication flow with NOFX backend

**Recommendation:** Use free tier initially, configure local tunnel for development

### Q4: Additional Considerations

- How to handle exchange API key storage?
- Should AI have trading limits/guards?
- Auto-trading vs. human-in-the-loop?
- Backtesting capabilities?

---

## Appendix: Quick Reference

### Port Mapping

| Service | Port | Description |
|---------|------|-------------|
| Hermes FastAPI | 8643 | AI chat, sessions, memory, jobs, skills, config |
| Hermes Gateway | 8642 | Messaging platforms |
| Hermes UI (old) | 8686 | Deprecated |
| NOFX Go | 8080 | Trading backend |
| NOFX React | 3000 | Trading UI (dev) / Vercel (prod) |

### API Endpoints (NOFX)

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login, get JWT
- `GET /portfolio` - View portfolio
- `GET /positions` - View open positions
- `POST /trade` - Execute trade
- `GET /strategies` - List strategies
- `POST /strategies` - Create strategy

### API Endpoints (Hermes)

- `POST /chat` - AI chat
- `GET /sessions` - List sessions
- `POST /sessions` - Create session
- `GET /memory` - Query memory
- `POST /memory` - Store memory
- `GET /skills` - List skills

---

*Document Version: 1.0*  
*Last Updated: 2026-04-10*  
*Status: Planning*