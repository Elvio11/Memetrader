# Getting Started with MemeTrader

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | Required for Hermes |
| Go | 1.25+ | Required for NOFX |
| Node.js | 18+ | Required for NOFX UI |
| Git | Any | Clone the repo |

---

## Quick Install (All-in-One)

### Step 1: Clone and Setup

```bash
git clone https://github.com/NousResearch/Memetrader.git
cd Memetrader
```

### Step 2: Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[all]"
```

### Step 3: Configure NOFX

Create or edit `nofx/.env`:

```bash
cp nofx/.env.example nofx/.env
# Edit with your API keys and exchange credentials
```

### Step 4: Start NOFX (Go Backend)

```bash
cd nofx
go build -o nofx ./cmd/nofx
./nofx
```

### Step 5: Start NOFX UI (React)

```bash
cd nofx-ui
npm install
npm run dev
```

Access at http://localhost:3000

### Step 6: Start Hermes

```bash
hermes model           # Choose your LLM
hermes tools          # Enable NOFX tools
hermes                # Start CLI
```

---

## Environment Variables

### Hermes

| Variable | Default | Description |
|----------|---------|-------------|
| `NOFX_API_URL` | http://localhost:8080 | NOFX API endpoint |
| `NOFX_API_TOKEN` | - | JWT token for NOFX auth |
| `ANTHROPIC_API_KEY` | - | Anthropic API key |
| `OPENAI_API_KEY` | - | OpenAI API key |

### NOFX

| Variable | Description |
|----------|-------------|
| `JWT_SECRET` | JWT signing secret |
| `BINANCE_API_KEY` | Binance API key |
| `BINANCE_SECRET` | Binance secret |
| `BYBIT_API_KEY` | Bybit API key |
| `BYBIT_SECRET` | Bybit secret |
| `TRANSPORT_ENCRYPTION` | Set to true for HTTPS |

---

## Verify Integration

### Test Hermes → NOFX Connection

```python
# In Hermes CLI, these tools should work:
hermes> What exchanges does NOFX have connected?
```

Expected: Returns list of connected exchanges via `nofx_exchanges` tool

### Test Trade Flow

```python
# In Hermes CLI:
hermes> Show my current positions
```

Expected: Returns positions via `nofx_positions` tool calling NOFX API

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| NOFX API not responding | Check port 8080 is available: `lsof -i :8080` |
| Hermes can't find NOFX | Verify `NOFX_API_URL` in config |
| NOFX UI shows blank | Ensure NOFX Go is running on port 8080 |
| Auth errors | Verify JWT token in `NOFX_API_TOKEN` |

See [troubleshooting.md](troubleshooting.md) for more issues.

---

## Next Steps

- [architecture.md](architecture.md) - System architecture deep dive
- [cross-project-understanding.md](cross-project-understanding.md) - How projects connect
- [development-guide.md](development-guide.md) - Developing new features