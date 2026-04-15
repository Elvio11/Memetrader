# Decision: Paper Trading Migration

**Date**: 2026-04-12  
**Status**: APPROVED  
**Owner**: MemeTrader Team

---

## Summary

Remove Hermes' internal paper trading engine and migrate to NOFX's native paper trading/testnet features across all supported exchanges.

---

## Background

### Current State
- Hermes has its own paper trading engine in `tools/trading/paper_engine.py`
- NOFX (Go backend) supports 10+ exchanges with varying testnet/paper support
- Some exchanges have built-in testnet modes (Hyperliquid, Lighter, OKX)
- Others require manual testnet API credentials

### Problem
- Duplicate functionality between Hermes paper engine and NOFX
- Paper engine maintenance burden
- Inconsistent behavior vs real exchange APIs

---

## Decision

### 1. Remove Hermes Paper Trading Engine

**DELETE** - Remove entirely:
```
tools/trading/
├── __init__.py
└── paper_engine.py
```

Also remove from:
- `toolsets.py` - Remove trading toolset
- `model_tools.py` - Remove imports

### 2. NOFX Tools in Hermes - Rename for Clarity

Rename file: `tools/nofx_trading_tool.py` → `tools/nofx_tools.py`

**Tool Naming - New Cleaner Names:**

| Old Tool | New Tool | Purpose |
|----------|----------|---------|
| `nofx_trade` | `trade_execute` | Execute a trade |
| `nofx_portfolio` | `portfolio` | Get portfolio holdings |
| `nofx_positions` | `positions` | Get open positions |
| `nofx_strategies` | `strategies` | Manage strategies |
| `nofx_account` | `account` | Get account info |
| `nofx_exchanges` | `exchanges` | List connected exchanges |
| `paper_trade` | `trade_paper` | Paper trade execution |

**New Helper Tools:**

| Tool | Purpose |
|------|---------|
| `trade_mode` | Set/get paper/live mode |
| `exchange_connect` | Configure exchange connection |
| `exchange_status` | Check exchange connectivity |

### 3. Config Flag - Option A (Global Setting)

In `config.yaml`:

```yaml
nofx:
  enabled: true
  api_url: http://localhost:8080
  api_token: your-jwt-token
  paper_trading: true  # GLOBAL FLAG - all exchanges use paper mode
```

### 4. Exchange Configuration

In `config.yaml` with per-exchange settings:

```yaml
nofx:
  enabled: true
  api_url: http://localhost:8080
  api_token: your-jwt-token
  paper_trading: true  # Default: paper mode
  
  exchanges:
    - name: binance
      testnet: true     # Override: use testnet
      api_key: YOUR_KEY
      secret_key: YOUR_SECRET
    
    - name: bybit
      testnet: false    # Override: use live
      api_key: YOUR_KEY
      secret_key: YOUR_SECRET
      
    - name: hyperliquid
      testnet: true     # Built-in testnet supported
      private_key: YOUR_PK
      wallet_addr: YOUR_ADDR
```

---

## Supported Exchanges & Testnet Status

| # | Exchange | Type | Testnet | Implementation |
|---|----------|------|---------|----------------|
| 1 | Binance | CEX | ⚠️ Manual | Use testnet API keys |
| 2 | Bybit | CEX | ❌ | Use testnet.bybit.com |
| 3 | OKX | CEX | ✅ Built-in | `x-simulated-trading` header |
| 4 | Bitget | CEX | ❓ TBD | Needs verification |
| 5 | KuCoin | CEX | ❓ TBD | Needs verification |
| 6 | Gate | CEX | ❓ TBD | Needs verification |
| 7 | Hyperliquid | DEX | ✅ Yes | `testnet` param |
| 8 | Aster DEX | DEX | ❓ TBD | Needs verification |
| 9 | Lighter | DEX | ✅ Yes | `testnet` param |
| 10 | Indodax | CEX | ❌ No | Indonesia only |

### Legend
- ✅ Yes = Built-in testnet support in NOFX code
- ⚠️ Manual = Must use separate testnet API credentials
- ❌ No = No testnet available
- ❓ TBD = Needs code verification before implementation

---

## Implementation Phases

### Phase 1: Remove Hermes Paper Engine
- [ ] Delete `tools/trading/` directory
- [ ] Remove from `toolsets.py`
- [ ] Remove from `model_tools.py`
- [ ] Verify build still works

### Phase 2: Rename & Update NOFX Tools
- [ ] Rename `nofx_trading_tool.py` → `nofx_tools.py`
- [ ] Update tool registry names (cleaner names)
- [ ] Add `trade_mode` tool
- [ ] Add `exchange_connect` tool
- [ ] Add `exchange_status` tool
- [ ] Implement paper_trading config flag

### Phase 3: Config Integration
- [ ] Add `nofx.paper_trading` to DEFAULT_CONFIG
- [ ] Add `nofx.exchanges` config structure
- [ ] Update config loader if needed

### Phase 4: Test & Verify
- [ ] Test paper trade execution
- [ ] Test live trade execution
- [ ] Test mode switching
- [ ] Verify all 10 exchanges connect

---

## Files to Modify

| File | Action |
|------|--------|
| `tools/trading/` | DELETE |
| `tools/nofx_trading_tool.py` | RENAME → `nofx_tools.py` |
| `toolsets.py` | UPDATE |
| `model_tools.py` | UPDATE |
| `hermes_cli/config.py` | UPDATE (config defaults) |

---

## Notes

- Documentation updates deferred (per user request)
- Some exchange testnet support still needs verification
- May need to add missing testnet parameters to NOFX Go code for some exchanges
- Config migration for existing users - not addressed yet

---

## Reference

For complete documentation reference, see: **[docs/MASTERR.md](./docs/MASTERR.md)**

This master reference contains links to all 651 .md files in the repository, organized by category.