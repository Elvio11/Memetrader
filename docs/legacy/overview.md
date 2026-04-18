# MemeTrader Documentation - Overview

## What is MemeTrader?

**MemeTrader** is the unified AI-powered trading platform combining:

1. **Hermes Agent** (Python AI) - 60+ tools for AI-powered conversations, file operations, terminal, web, browser, vision, code execution, memory, and trading integration

2. **NOFX** (Go Trading Backend) - Real-money cryptocurrency and stock trading across 15+ exchanges

3. **NOFX UI** (React Frontend) - Professional trading dashboard and strategy studio

---

## Three Projects Summary

| Project | Language | Purpose | Primary Port |
|---------|----------|---------|--------------|
| Hermes Agent | Python 3 | AI Agent with 60+ tools | 8643 (FastAPI) |
| NOFX | Go 1.25+ | Trading execution engine | 8080 (HTTP) |
| NOFX UI | React/TypeScript | Trading dashboard | 3000 (dev) |

---

## Quick Links

| Document | Description |
|----------|-------------|
| [getting-started.md](getting-started.md) | Installation and setup |
| [architecture.md](architecture.md) | System architecture |
| [cross-project-understanding.md](cross-project-understanding.md) | How the projects connect |
| [development-guide.md](development-guide.md) | How to develop features |
| [troubleshooting.md](troubleshooting.md) | Common issues |

---

## Tech Stacks

### Hermes Agent

- **Language**: Python 3.11+
- **AI Client**: OpenAI SDK, Anthropic SDK
- **CLI**: prompt_toolkit, Rich
- **Session Store**: SQLite (FTS5)
- **HTTP**: FastAPI, aiohttp
- **Messaging**: python-telegram-bot, discord.py

### NOFX

- **Language**: Go 1.25+
- **HTTP Framework**: Gin
- **Database**: SQLite (modernc.org/sqlite)
- **Auth**: JWT (golang-jwt/jwt)
- **Exchange APIs**: adshao/go-binance, bybit.go.api, etc.

### NOFX UI

- **Framework**: React 18
- **Build**: Vite
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Data Fetching**: SWR
- **Charts**: recharts, lightweight-charts

---

## Key Files

### Integration Files

| File | Purpose |
|------|---------|
| `tools/nofx_trading_tool.py` | Hermes → NOFX API connection |
| `nofx/api/server.go` | NOFX HTTP API endpoints |
| `nofx-ui/src/lib/api.ts` | NOFX UI → NOFX API client |

### Entry Points

| File | Project | Description |
|------|---------|-------------|
| `cli.py` | Hermes | Interactive CLI entry |
| `run_agent.py` | Hermes | AIAgent class |
| `nofx/main.go` | NOFX | Go entry point |
| `nofx-ui/src/main.tsx` | NOFX UI | React entry |

---

## Terminology

| Term | Definition |
|------|------------|
| **Hermes** | Python AI agent with 60+ tools |
| **NOFX** | Go trading backend (real-money execution) |
| **Paper Trading** | Simulated trading (no real money) |
| **Gateway** | Hermes messaging platform connector (Telegram, Discord, etc.) |
| **Toolset** | Group of related tools in Hermes |
| **Skill** | Reusable prompt-based capability in Hermes |

---

## Project Directory Structure

```
/workspaces/Memetrader/
├── # Hermes (Python AI)
├── cli.py                    # CLI entry point
├── run_agent.py             # AIAgent class
├── model_tools.py            # Tool orchestration
├── toolsets.py               # Toolset definitions
├── hermes_state.py            # SQLite session store
├── gateway/                  # Messaging platforms
├── tools/                    # 60+ tools
│   └── nofx_trading_tool.py # NOFX integration
├── hermes_cli/               # CLI subcommands
├── skills/                  # Hermes skills
├── plugins/                  # Memory plugins
├── acp_adapter/             # ACP server
├── cron/                    # Scheduler
│
├── # NOFX (Go Trading)
├── nofx/
│   ├── main.go              # Entry point
│   ├── api/                 # HTTP API
│   ├── trader/              # Trading engine + 15+ exchanges
│   ├── store/               # SQLite operations
│   ├── auth/               # JWT auth
│   ├── mcp/                # AI providers
│   ├── telegram/            # Telegram bot
│   └── wallet/              # x402 payments
│
├── # NOFX UI (React)
├── nofx-ui/
│   ├── src/
│   │   ├── pages/           # Dashboard, Strategy Studio
│   │   ├── lib/api.ts       # API client
│   │   ├── stores/          # Zustand
│   │   └── contexts/        # Auth, Language
│   └── package.json
│
└── # Documentation
├── docs/
│   ├── overview.md          # This file
│   ├── getting-started.md  # Installation
│   ├── architecture.md     # System architecture
│   ├── cross-project-understanding.md
│   └── development-guide.md
```

---

## Next Steps

1. **[getting-started.md](getting-started.md)** - Install and run the full system
2. **[architecture.md](architecture.md)** - Deep dive into system design
3. **[cross-project-understanding.md](cross-project-understanding.md)** - How projects integrate