# MemeTrader Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MEMETRADER UNIFIED                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐         ┌──────────────────┐         ┌────────────┐│
│  │    Hermes        │         │     NOFX         │         │  NOFX UI   ││
│  │    Python       │────────▶│     Go           │────────▶│  React     ││
│  │    AI Agent     │   API    │   Trading        │  API   │  Frontend  ││
│  │    Port 8643   │  :8080  │   Port 8080     │  :3000  │            ││
│  └──────────────────┘         └──────────────────┘         └────────────┘│
│           │                              │                                 │
│           │                              │                                 │
│           ▼                              ▼                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        60+ Tools (Hermes)                           │  │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐  │  │
│  │  │  Files   │ │Terminal  │ │   Web    │ │ Browser  │ │ Trading │  │  │
│  │  │  Tool   │ │  Tool    │ │  Tool    │ │  Tool   │ │  Tool   │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Hermes Architecture

### Core Components

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           HERMES AGENT                                     │
├─────────────────────────────────────────────────────────────���────────────┤
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │    CLI      │     │   Gateway   │     │   FastAPI  │              │
│  │  (cli.py)   │     │ (gateway/)  │     │  (run.py)   │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│          │                   │                   │                       │
│          └───────────────────┼───────────────────┘                       │
│                              ▼                                            │
│                    ┌─────────────────────┐                               │
│                    │    run_agent.py     │                               │
│                    │    AIAgent Class    │                               │
│                    └─────────────────────┘                               │
│                              │                                            │
│                              ▼                                            │
│                    ┌─────────────────────┐                               │
│                    │  model_tools.py     │                               │
│                    │ Tool Orchestration  │                               │
│                    └─────────────────────┘                               │
│                              │                                            │
│                              ▼                                            │
│                    ┌─────────────────────┐                               │
│                    │     tools/          │                               │
│                    │   Tool Registry     │                               │
│                    │  (60+ tools)       │                               │
│                    └─────────────────────┘                               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Hermes Tool Flow

```
User Message → AIAgent.run_conversation()
                    │
                    ▼
         ┌───────────────────────┐
         │   OpenAI API Call    │
         │   (with tool schemas) │
         └───────────────────────┘
                    │
                    ▼ (if tool_call)
         ┌───────────────────────┐
         │ handle_function_call│
         │  (model_tools.py)    │
         └───────────────────────┘
                    │
                    ▼
         ┌───────────────────────┐
         │   Tool Registry       │
         │   (tools/registry.py) │
         └───────────────────────┘
                    │
                    ▼
         ┌───────────────────────┐
         │   Tool Handler       │
         │   (e.g., nofx_trade) │
         └───────────────────────┘
                    │
                    ▼
         ┌───────────────────────┐
         │   Execute Tool      │
         │   Return JSON      │
         └───────────────────────┘
```

---

## NOFX Architecture

### Core Components

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              NOFX                                        │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │    HTTP API  │     │   Telegram  │     │   x402      │              │
│  │   (Gin)     │     │    Agent    │     │  Payments  │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│          │                   │                   │                       │
│          └───────────────────┼───────────────────┘                       │
│                              ▼                                            │
│                    ┌─────────────────────┐                               │
│                    │    Trading Engine   │                               │
│                    │    (trader/)       │                               │
│                    └─────────────────────┘                               │
│                              │                                            │
│          ┌───────────────────┼───────────────────┐                        │
│          ▼                   ▼                   ▼                        │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │  CEX        │     │   DEX      │     │  AI Model   │              │
│  │ Connectors  │     │ Connectors  │     │  Providers │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│       Binance        Hyperliquid           DeepSeek                     │
│       Bybit            Aster               Claude                        │
│       OKX               Lighter            GPT-4                      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### NOFX API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/trades` | POST | Execute a trade |
| `/api/portfolio` | GET | Get portfolio holdings |
| `/api/positions` | GET | Get open positions |
| `/api/strategies` | GET/POST | List/create strategies |
| `/api/account` | GET | Get account info |
| `/api/exchanges` | GET | List connected exchanges |
| `/api/status` | GET | System status |

---

## NOFX UI Architecture

### Page Structure

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            NOFX UI                                        │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │  Dashboard │     │   Strategy   │     │   Settings  │              │
│  │   Page     │     │   Studio     │     │    Page     │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│          │                   │                   │                       │
│          └───────────────────┼───────────────────┘                       │
│                              ▼                                            │
│                    ┌─────────────────────┐                               │
│                    │    API Client       │                               │
│                    │  (lib/api.ts)       │                               │
│                    └─────────────────────┘                               │
│                              │                                            │
│                              ▼                                            │
│                    ┌─────────────────────┐                               │
│                    │   NOFX Go Backend   │                               │
│                    │   (port 8080)     │                               │
│                    └─────────────────────┘                               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### Hermes → NOFX (nofx_trading_tool.py)

```python
# tools/nofx_trading_tool.py makes REST calls to NOFX
url = f"http://localhost:8080/api/trades"
response = requests.post(url, json=trade_params)
```

### NOFX UI → NOFX (lib/api.ts)

```typescript
// nofx-ui/src/lib/api.ts makes REST calls to NOFX
const response = await axios.get('http://localhost:8080/api/positions');
```

---

## Database Schema

### Hermes (SQLite)

Tables:
- `sessions` - Conversation sessions
- `memory` - Persistent memory entries
- `jobs` - Scheduled cron jobs

### NOFX (SQLite)

Tables:
- `traders` - Trader configurations
- `strategies` - Trading strategies
- `positions` - Open positions
- `trades` - Trade history
- `exchanges` - Exchange connections

---

## Authentication

| Service | Method | Configuration |
|---------|--------|---------------|
| Hermes → LLM | API Key | Config in `config.yaml` |
| Hermes Gateway | Per-platform | Bot tokens per platform |
| NOFX | JWT | `JWT_SECRET` env var |
| NOFX UI | JWT | Via NOFX Go backend |

---

## Next Steps

- [cross-project-understanding.md](cross-project-understanding.md) - How projects connect
- [development-guide.md](development-guide.md) - Developing new features
- [troubleshooting.md](troubleshooting.md) - Common issues