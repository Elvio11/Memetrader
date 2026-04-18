# MemeTrader Grid Trading Implementation Plan

## Completed ✅

### Phase 1: Expose NOFX Grid to Hermes (Low Effort, High Value)

**Created Hermes tools:**
- `grid_traders_list` - List available NOFX traders
- `grid_trader_status` - Get trader status
- `grid_start` - Start grid on a trader
- `grid_stop` - Stop grid on a trader
- `grid_config_get` - Get current config
- `grid_configure` - Update grid parameters
- `grid_risk_info` - Get risk info
- `grid_status` - Comprehensive status

**Location:** `tools/nofx_grid_tool.py`

### Phase 2: DEX Grid in Python (Medium Effort, High Value)

**Created Hermes tools:**
- `dex_grid_init` - Initialize DEX grid (Jupiter/Raydium/Aerodrome)
- `dex_grid_status` - Get grid status
- `dex_grid_stop` - Stop grid
- `dex_grid_config` - Get config
- `dex_grid_configure` - Update config
- `dex_grid_estimate` - Estimate profit potential

**Location:** `tools/dex_grid_tool.py`

---

## Future Plan (Not Started)

### Phase 3: CEX Spot Support (Higher Effort, Medium Value)

**Scope:**
- Build spot trading support for CEX exchanges
- Priority: Binance Spot, OKX Spot
- Existing CEX futures support to remain

**Notes:**
- NOFX currently only supports futures on CEX
- Indodax is the only spot-only exchange with limited features
- Grid trading works well on futures; spot would require additional logic

**When to implement:**
- After DEX grid is proven and users request CEX spot
- Requires: CEX API integration for spot orders

---

## Implementation Details

### NOFX Grid Tools (8 tools)
- Call NOFX API to control existing grid system
- Works with all 10+ CEX exchanges (Binance, Bybit, OKX, etc.)
- Requires: NOFX_API_URL and NOFX_API_TOKEN env vars

### DEX Grid Tools (6 tools)
- Python-native grid trading on DEXes
- Supports: Jupiter (Solana), Raydium (Solana), Aerodrome (Base)
- Uses limit orders for grid levels
- State persisted to `~/.hermes/dex_grid_state.json`

### Usage Examples

**NOFX Grid:**
```
grid_traders_list                    # Get available traders
grid_start trader_id=abc123         # Start grid
grid_status trader_id=abc123        # Check status
grid_configure trader_id=abc123 grid_levels=20 grid_spacing=0.5
grid_stop trader_id=abc123          # Stop grid
```

**DEX Grid:**
```
dex_grid_init token_a=SOL token_b=USDC lower_price=100 upper_price=150 grid_levels=10
dex_grid_status                     # Check grid status
dex_grid_configure lower_price=95 upper_price=155
dex_grid_stop                       # Stop grid
```

---

*Last updated: 2026-04-18*
*Status: Phase 1 & 2 Complete, Phase 3 Future*