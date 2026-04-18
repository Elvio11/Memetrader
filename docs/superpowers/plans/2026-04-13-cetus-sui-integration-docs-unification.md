# Cetus SUI Integration & Documentation Unification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Cetus DEX integration for NOFX and unify fragmented documentation into single source

**Architecture:** Two independent tracks - (1) Docs restructure (2) Cetus integration following existing exchange pattern

**Tech Stack:** Go (NOFX), Python (Hermes), Markdown docs

---

## Phase 1: Documentation Unification (Priority - Lower Risk)

### Task 1: Create Unified Documentation Structure

**Files:**
- Create: `docs/memetrader/index.md`
- Create: `docs/memetrader/architecture/`
- Create: `docs/memetrader/integrations/`
- Create: `docs/memetrader/trading/`
- Create: `docs/memetrader/deployment/`
- Create: `docs/memetrader/reference/`

- [ ] **Step 1: Create memetrader directory structure**

```bash
mkdir -p docs/memetrader/{architecture,integrations/exchanges,integrations/dex,integrations/providers,trading,deployment,reference}
```

- [ ] **Step 2: Create index.md entry point**

```markdown
# MemeTrader Documentation

Unified documentation for MemeTrader - AI-powered trading system

## Systems

- [Hermes Agent](./architecture/hermes-agent.md) - AI assistant framework
- [NOFX Trading](./architecture/nofx.md) - Go-based trading backend
- [Integration](./architecture/integration.md) - How systems connect

## Quick Links

- [Exchanges](./integrations/exchanges/) - Supported exchanges
- [DEX](./integrations/dex/) - Decentralized exchanges
- [Trading](./trading/) - Trading strategies and debugging
- [Deployment](./deployment/) - Setup guides
- [Reference](./reference/) - CLI, environment variables
```

- [ ] **Step 3: Commit**

```bash
git add docs/memetrader/
git commit -m "docs: create unified documentation structure"
```

---

### Task 2: Move and Categorize Existing Docs

**Files:**
- Modify: `docs/architecture.md` → Move to `docs/memetrader/architecture/`
- Modify: `docs/overview.md` → Move to `docs/memetrader/architecture/overview.md`
- Modify: `docs/troubleshooting.md` → Move to `docs/memetrader/reference/`

- [ ] **Step 1: Move docs/architecture.md to memetrader**

```bash
mv docs/architecture.md docs/memetrader/architecture/system.md
```

- [ ] **Step 2: Move docs/overview.md to memetrader**

```bash
mv docs/overview.md docs/memetrader/architecture/overview.md
```

- [ ] **Step 3: Move docs/troubleshooting.md to memetrader**

```bash
mv docs/troubleshooting.md docs/memetrader/reference/troubleshooting.md
```

- [ ] **Step 4: Commit**

```bash
git add docs/
git commit -m "docs: move existing docs to unified structure"
```

---

### Task 3: Create Architecture Documentation

**Files:**
- Create: `docs/memetrader/architecture/hermes-agent.md`
- Create: `docs/memetrader/architecture/nofx.md`
- Create: `docs/memetrader/architecture/integration.md`

- [ ] **Step 1: Create hermes-agent.md**

```markdown
# Hermes Agent

AI assistant framework for MemeTrader

## Overview

Hermes is a Python-based AI agent that provides:
- Natural language interface via Telegram, Discord, Slack
- 60+ tools for file operations, terminal, web browsing
- Session memory and context
- MCP tool integration

## Key Files

- `run_agent.py` - Main agent loop
- `model_tools.py` - Tool orchestration
- `cli.py` - Interactive CLI
- `gateway/` - Messaging platform adapters
- `tools/` - Tool implementations

## Configuration

Config: `~/.hermes/config.yaml`
```

- [ ] **Step 2: Create nofx.md**

```markdown
# NOFX Trading Backend

Go-based trading system for MemeTrader

## Overview

NOFX is a Go trading engine that connects to 9+ exchanges:
- OKX, Bybit, Gate, KuCoin, HyperLiquid, Bitget, Aster, Indodax, Lighter

## Architecture

```
User → Hermes → NOFX API (8080) → Exchanges
```

## Key Files

- `nofx/main.go` - Entry point
- `nofx/trader/` - Exchange integrations
- `nofx/api/` - REST API handlers
- `nofx/mcp/` - AI provider integrations

## API Endpoints

- `GET /api/portfolio` - Portfolio holdings
- `GET /api/positions` - Open positions
- `POST /api/trades` - Execute trade
- `GET /api/account` - Account info
```

- [ ] **Step 3: Create integration.md**

```markdown
# System Integration

How Hermes and NOFX work together

## Communication Flow

1. User sends message via Telegram/Discord/Slack
2. Hermes processes using AI + tools
3. For trades, Hermes calls NOFX API (localhost:8080)
4. NOFX executes on connected exchange
5. Result returned to Hermes, then to user

## Available Tools

- `nofx_portfolio` - Get portfolio
- `nofx_positions` - Get positions
- `nofx_trade` - Execute trade
- `nofx_strategies` - Manage strategies
- `nofx_account` - Account info
- `nofx_exchanges` - List exchanges

## Configuration

```yaml
nofx:
  enabled: true
  api_url: http://localhost:8080
  api_token: your-jwt-token
```
```

- [ ] **Step 4: Commit**

```bash
git add docs/memetrader/architecture/
git commit -m "docs: add architecture documentation for Hermes and NOFX"
```

---

### Task 4: Create Integration Documentation

**Files:**
- Create: `docs/memetrader/integrations/exchanges/index.md`
- Create: `docs/memetrader/integrations/exchanges/okx.md`
- Create: `docs/memetrader/integrations/exchanges/bybit.md`

- [ ] **Step 1: Create exchanges index**

```markdown
# Exchange Integrations

NOFX supports the following exchanges:

| Exchange | Type | Status |
|----------|------|--------|
| OKX | CEX | Active |
| Bybit | CEX | Active |
| Gate | CEX | Active |
| KuCoin | CEX | Active |
| HyperLiquid | CEX | Active |
| Bitget | CEX | Active |
| Aster | CEX | Active |
| Indodax | CEX | Active |
| Lighter | DEX | Active |
```

- [ ] **Step 2: Create okx.md example**

```markdown
# OKX Integration

## Overview

OKX is a centralized exchange (CEX) integration in NOFX.

## Features

- Spot trading
- Futures trading
- Margin trading
- Account management
- Position tracking

## Configuration

Required environment variables:
- `OKX_API_KEY`
- `OKX_SECRET_KEY`
- `OKX_PASSPHRASE`

## File Location

`nofx/trader/okx/`
```

- [ ] **Step 3: Create bybit.md**

```markdown
# Bybit Integration

## Overview

Bybit is a CEX integration in NOFX.

## Features

- Spot trading
- Derivatives
- Account management
- Position tracking

## Configuration

Required environment variables:
- `BYBIT_API_KEY`
- `BYBIT_SECRET_KEY`

## File Location

`nofx/trader/bybit/`
```

- [ ] **Step 4: Commit**

```bash
git add docs/memetrader/integrations/
git commit -m "docs: add exchange integration documentation"
```

---

### Task 5: Archive Legacy Docs

**Files:**
- Create: `docs/legacy/`
- Modify: Move outdated docs to legacy/

- [ ] **Step 1: Create legacy directory**

```bash
mkdir -p docs/legacy
```

- [ ] **Step 2: Check for outdated docs in root docs/**

```bash
ls docs/*.md
```

- [ ] **Step 3: Move outdated docs to legacy (review each)**

```bash
# Move docs that are outdated
mv docs/cleanup-refactoring-guidance.md docs/legacy/ 2>/dev/null || true
mv docs/getting-started.md docs/legacy/ 2>/dev/null || true
mv docs/development-guide.md docs/legacy/ 2>/dev/null || true
mv docs/cross-project-understanding.md docs/legacy/ 2>/dev/null || true
mv docs/MASTERR.md docs/legacy/ 2>/dev/null || true
```

- [ ] **Step 4: Create legacy index**

```markdown
# Legacy Documentation

These docs are outdated but kept for reference.

## Contents

- Old getting started guides
- Deprecated features
- Historical architecture

**Use memetrader/ for current documentation**
```

- [ ] **Step 5: Commit**

```bash
git add docs/legacy/
git commit -m "docs: archive legacy documentation"
```

---

## Phase 2: Cetus SUI Integration (Priority - Higher Risk)

### Task 6: Explore Cetus API/SDK

**Files:**
- Research: External Cetus documentation
- Create: `docs/memetrader/integrations/dex/cetus.md` (research notes)

- [ ] **Step 1: Web search for Cetus SUI SDK**

Search: "Cetus SUI DEX SDK Go"

- [ ] **Step 2: Check for existing Go SDK**

Check: https://github.com/cetusfinance
Check: https://docs.cetus.fi

- [ ] **Step 3: Document findings**

Create `docs/memetrader/integrations/dex/cetus.md` with:
- API endpoints available
- Authentication method
- Rate limits
- Testnet availability

- [ ] **Step 4: Commit research findings**

```bash
git add docs/memetrader/integrations/dex/
git commit -m "research: document Cetus API exploration"
```

---

### Task 7: Create Cetus Trader Skeleton

**Files:**
- Create: `nofx/trader/cetus/trader.go`
- Create: `nofx/trader/cetus/types.go`

- [ ] **Step 1: Create directory**

```bash
mkdir -p nofx/trader/cetus
```

- [ ] **Step 2: Create types.go**

```go
package cetus

import "context"

type CetusTrader struct {
    ctx       context.Context
    wallet    string
    baseURL   string
    testnet   bool
}

func NewCetusTrader(wallet string, testnet bool) *CetusTrader {
    return &CetusTrader{
        ctx:     context.Background(),
        wallet:  wallet,
        baseURL: "https://api.cetus.fi",
        testnet: testnet,
    }
}
```

- [ ] **Step 3: Create trader.go with interface**

```go
package cetus

import (
    "context"
    "errors"
    "nofx/trader/types"
)

type Order struct {
    Symbol    string
    Side      string
    Amount    float64
    Price     float64
    OrderType string
}

type Account struct {
    Wallet   string
    Balances map[string]float64
}

type Position struct {
    Symbol  string
    Side    string
    Amount  float64
    EntryPrice float64
}

func (c *CetusTrader) PlaceOrder(ctx context.Context, order Order) (string, error) {
    return "", errors.New("not implemented")
}

func (c *CetusTrader) CancelOrder(ctx context.Context, orderID string) error {
    return errors.New("not implemented")
}

func (c *CetusTrader) GetAccount(ctx context.Context) (*Account, error) {
    return nil, errors.New("not implemented")
}

func (c *CetusTrader) GetPositions(ctx context.Context) ([]Position, error) {
    return nil, errors.New("not implemented")
}
```

- [ ] **Step 4: Commit skeleton**

```bash
git add nofx/trader/cetus/
git commit -m "feat: add Cetus trader skeleton"
```

---

### Task 8: Implement Cetus Authentication

**Files:**
- Modify: `nofx/trader/cetus/trader.go`

- [ ] **Step 1: Add wallet authentication**

```go
import (
    "github.com/moveyourfeet/cetus-sdk/wallet"
)

type CetusTrader struct {
    // ... existing fields
    privateKey string
}

func (c *CetusTrader) SetPrivateKey(key string) {
    c.privateKey = key
}

func (c *CetusTrader) SignTransaction(tx []byte) ([]byte, error) {
    // Use SUI wallet to sign
    return wallet.Sign(tx, c.privateKey)
}
```

- [ ] **Step 2: Commit**

```bash
git add nofx/trader/cetus/
git commit -m "feat: add Cetus wallet authentication"
```

---

### Task 9: Implement Cetus Trading Operations

**Files:**
- Modify: `nofx/trader/cetus/trader.go`
- Create: `nofx/trader/cetus/orders.go`

- [ ] **Step 1: Implement PlaceOrder**

```go
func (c *CetusTrader) PlaceOrder(ctx context.Context, order Order) (string, error) {
    // Build swap transaction
    // Sign with wallet
    // Submit to Cetus
    return orderID, nil
}
```

- [ ] **Step 2: Implement CancelOrder**

```go
func (c *CetusTrader) CancelOrder(ctx context.Context, orderID string) error {
    // Cancel pending order
    return nil
}
```

- [ ] **Step 3: Commit**

```bash
git add nofx/trader/cetus/
git commit -m "feat: implement Cetus trading operations"
```

---

### Task 10: Implement Cetus Account/Positions

**Files:**
- Create: `nofx/trader/cetus/account.go`
- Create: `nofx/trader/cetus/positions.go`

- [ ] **Step 1: Implement GetAccount**

```go
func (c *CetusTrader) GetAccount(ctx context.Context) (*Account, error) {
    // Query wallet balances from SUI
    return &Account{
        Wallet:   c.wallet,
        Balances: balances,
    }, nil
}
```

- [ ] **Step 2: Implement GetPositions**

```go
func (c *CetusTrader) GetPositions(ctx context.Context) ([]Position, error) {
    // Query open positions from Cetus pools
    return positions, nil
}
```

- [ ] **Step 3: Commit**

```bash
git add nofx/trader/cetus/
git commit -m "feat: implement Cetus account and positions"
```

---

### Task 11: Create Cetus Documentation

**Files:**
- Modify: `docs/memetrader/integrations/dex/cetus.md`

- [ ] **Step 1: Document Cetus integration**

```markdown
# Cetus DEX Integration

## Overview

Cetus is a concentrated liquidity DEX on SUI blockchain.

## Features

- Swap trading
- Liquidity positions
- Wallet-based authentication

## Configuration

Required:
- SUI wallet private key
- SUI RPC endpoint

## File Location

`nofx/trader/cetus/`

## API

- PlaceOrder - Execute swap
- CancelOrder - Cancel swap
- GetAccount - Wallet balances
- GetPositions - Open positions
```

- [ ] **Step 2: Commit**

```bash
git add docs/memetrader/integrations/dex/
git commit -m "docs: add Cetus DEX integration docs"
```

---

## Execution Choice

**Plan complete and saved to `docs/superpowers/plans/2026-04-13-cetus-sui-integration-docs-unification.md`**

Two execution options:

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
