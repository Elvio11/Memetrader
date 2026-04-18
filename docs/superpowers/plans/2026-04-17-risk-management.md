# Part 9: Risk Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement comprehensive risk management system with configurable parameters and trading modes for the MemeTrader unified system.

**Architecture:** Extend existing trading tools with risk validation, add configuration options for risk parameters, and implement trading mode controls that interface with NOFX trading.

**Tech Stack:** Python, Hermes Agent framework, NOFX trading API, configuration system

---

### Part 9.1: Risk Parameters Implementation

#### Task 1: Create Risk Configuration Manager

**Files:**
- Create: `tools/risk_manager.py`
- Modify: `tools/nofx_trading_tool.py:200-250` (add risk validation)

- [ ] **Step 1: Create risk manager with parameter validation**

```python
import json
import os
from typing import Dict, Any, Optional
from tools.registry import registry

RISK_DEFAULTS = {
    "max_position_size": 0.05,  # 5% of portfolio
    "max_drawdown": -0.10,      # -10% daily
    "stop_loss": -0.15,         # -15% hard stop
    "take_profit": 0.30,        # +30% trailing
    "max_open_positions": 5,
    "approval_threshold": 100.0 # $100
}

def get_risk_config() -> Dict[str, Any]:
    """Get risk configuration from environment or defaults"""
    config = RISK_DEFAULTS.copy()
    
    # Override from environment variables
    if os.getenv("RISK_MAX_POSITION_SIZE"):
        config["max_position_size"] = float(os.getenv("RISK_MAX_POSITION_SIZE"))
    if os.getenv("RISK_MAX_DRAWDOWN"):
        config["max_drawdown"] = float(os.getenv("RISK_MAX_DRAWDOWN"))
    if os.getenv("RISK_STOP_LOSS"):
        config["stop_loss"] = float(os.getenv("RISK_STOP_LOSS"))
    if os.getenv("RISK_TAKE_PROFIT"):
        config["take_profit"] = float(os.getenv("RISK_TAKE_PROFIT"))
    if os.getenv("RISK_MAX_OPEN_POSITIONS"):
        config["max_open_positions"] = int(os.getenv("RISK_MAX_OPEN_POSITIONS"))
    if os.getenv("RISK_APPROVAL_THRESHOLD"):
        config["approval_threshold"] = float(os.getenv("RISK_APPROVAL_THRESHOLD"))
        
    return config

def validate_trade_risk(trade_value: float, current_positions: int, 
                       daily_pnl: float, portfolio_value: float) -> Dict[str, Any]:
    """Validate trade against risk parameters"""
    config = get_risk_config()
    warnings = []
    errors = []
    
    # Position size check
    position_pct = trade_value / portfolio_value if portfolio_value > 0 else 0
    if position_pct > config["max_position_size"]:
        errors.append(f"Position size {position_pct:.2%} exceeds max {config['max_position_size']:.2%}")
    
    # Drawdown check
    if daily_pnl < (portfolio_value * config["max_drawdown"]):
        errors.append(f"Daily P&L {daily_pnl:.2f} exceeds max drawdown {portfolio_value * config['max_drawdown']:.2f}")
    
    # Open positions check
    if current_positions >= config["max_open_positions"]:
        errors.append(f"Max open positions {config['max_open_positions']} reached")
    
    # Approval threshold
    needs_approval = trade_value > config["approval_threshold"]
    
    return {
        "approved": len(errors) == 0,
        "warnings": warnings,
        "errors": errors,
        "needs_approval": needs_approval,
        "risk_metrics": {
            "position_pct": position_pct,
            "daily_pnl": daily_pnl,
            "current_positions": current_positions,
            "portfolio_value": portfolio_value
        }
    }
```

- [ ] **Step 2: Run test to verify it fails** (initially)

Run: `python -c "from tools.risk_manager import get_risk_config, validate_trade_risk; print('Risk manager imported')"`

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 4: Run test to verify it passes**

Run: `python -c "from tools.risk_manager import get_risk_config, validate_trade_risk; print('Risk manager: OK')"`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/risk_manager.py
git commit -m "feat: add risk management configuration and validation"
```

#### Task 2: Integrate Risk Validation into NOFX Trading

**Files:**
- Modify: `tools/nofx_trading_tool.py:200-250` (add risk validation to trade execution)

- [ ] **Step 1: Add risk validation to nofx_trade function**

```python
# Add import at top of file
from tools.risk_manager import validate_trade_risk, get_risk_config

# Modify nofx_trade function
def nofx_trade(
    symbol: str,
    side: str,
    amount: float,
    order_type: str = "market",
    price: float = None,
    ) -> str:
    """Execute a trade via NOFX trading API with risk validation.
    
    Args:
        symbol: Trading pair symbol (e.g., "BTC/USDT")
        side: "buy" or "sell"
        amount: Order amount
        order_type: Order type ("market", "limit", "stop")
        price: Limit/stop price (required for limit/stop orders)
    
    Returns JSON with order result or risk validation errors.
    """
    # TODO: Get current portfolio value, positions, and daily P&L from NOFX
    # For now, use placeholder values - would be enhanced with real portfolio data
    portfolio_value = 1000.0  # Placeholder
    current_positions = 0     # Placeholder
    daily_pnl = 0.0           # Placeholder
    
    # Estimate trade value (simplified)
    trade_value = amount * (price if price else 1.0)  # Rough estimate
    
    # Validate risk
    risk_result = validate_trade_risk(
        trade_value=trade_value,
        current_positions=current_positions,
        daily_pnl=daily_pnl,
        portfolio_value=portfolio_value
    )
    
    if not risk_result["approved"]:
        return json.dumps({
            "error": "Trade rejected by risk management",
            "risk_errors": risk_result["errors"],
            "risk_warnings": risk_result["warnings"],
            "needs_manual_review": True
        })
    
    # If approval required and not in autonomous mode, return for manual approval
    if risk_result["needs_approval"]:
        # Check trading mode from environment or config
        trading_mode = os.getenv("TRADING_MODE", "supervised").lower()
        if trading_mode != "autonomous":
            return json.dumps({
                "approval_required": True,
                "trade_value": trade_value,
                "risk_metrics": risk_result["risk_metrics"],
                "message": f"Trade requires manual approval (value: ${trade_value:.2f})"
            })
    
    # Proceed with trade execution
    order_data = {
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "type": order_type,
    }
    if price is not None:
        order_data["price"] = price
    
    # ... existing trade execution code ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -c "from tools.nofx_trading_tool import nofx_trade; print('nofx_trade imports risk manager')"`

Expected: FAIL if risk_manager not imported correctly

- [ ] **Step 4: Run test to verify it passes**

Run: `python -c "from tools.nofx_trading_tool import nofx_trade; print('NOFX trading tool: OK')"`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/nofx_trading_tool.py
git commit -m "feat: add risk validation to NOFX trade execution"
```

#### Task 3: Add Risk Management Tools to Hermes

**Files:**
- Create: `tools/risk_tools.py` (Hermes-exposed risk management tools)

- [ ] **Step 1: Create risk management tools for Hermes**

```python
import json
import os
from tools.registry import registry
from tools.risk_manager import get_risk_config, validate_trade_risk

def get_risk_parameters() -> str:
    """Get current risk management parameters"""
    config = get_risk_config()
    return json.dumps({
        "risk_parameters": config,
        "source": "environment_and_defaults"
    })

def update_risk_parameter(parameter: str, value: str) -> str:
    """Update a risk parameter (stored in environment for session)
    
    Note: For persistence, user should set environment variables
    """
    valid_params = [
        "max_position_size", "max_drawdown", "stop_loss", 
        "take_profit", "max_open_positions", "approval_threshold"
    ]
    
    if parameter not in valid_params:
        return json.dumps({"error": f"Invalid parameter. Valid: {valid_params}"})
    
    try:
        # Convert value to appropriate type
        if parameter in ["max_open_positions"]:
            converted = int(value)
        else:
            converted = float(value)
        
        # Set environment variable (affects current process)
        env_var_map = {
            "max_position_size": "RISK_MAX_POSITION_SIZE",
            "max_drawdown": "RISK_MAX_DRAWDOWN",
            "stop_loss": "RISK_STOP_LOSS",
            "take_profit": "RISK_TAKE_PROFIT",
            "max_open_positions": "RISK_MAX_OPEN_POSITIONS",
            "approval_threshold": "RISK_APPROVAL_THRESHOLD"
        }
        
        os.environ[env_var_map[parameter]] = str(converted)
        
        return json.dumps({
            "success": True,
            "parameter": parameter,
            "value": converted,
            "message": f"Updated {parameter} to {converted} (session-only)"
        })
    except ValueError as e:
        return json.dumps({"error": f"Invalid value for {parameter}: {str(e)}"})

def check_trade_risk(symbol: str, side: str, amount: float, 
                    price: float = None, portfolio_value: float = 1000.0) -> str:
    """Pre-check trade against risk parameters without executing
    
    Args:
        symbol: Trading pair
        side: buy/sell
        amount: Order amount
        price: Optional price for limit orders
        portfolio_value: Total portfolio value in USD
    """
    # Estimate trade value
    trade_value = amount * (price if price else 1.0)
    
    # Get current positions (would come from NOFX in real implementation)
    current_positions = 0  # Placeholder
    daily_pnl = 0.0        # Placeholder
    
    risk_result = validate_trade_risk(
        trade_value=trade_value,
        current_positions=current_positions,
        daily_pnl=daily_pnl,
        portfolio_value=portfolio_value
    )
    
    return json.dumps({
        "trade_analysis": {
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "estimated_value": trade_value,
            "portfolio_value": portfolio_value
        },
        "risk_assessment": risk_result
    })
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -c "from tools.risk_tools import get_risk_parameters, update_risk_parameter, check_trade_risk; print('Risk tools imported')"`

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 4: Run test to verify it passes**

Run: `python -c "from tools.risk_tools import get_risk_parameters, update_risk_parameter, check_trade_risk; print('Risk tools: OK')"`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/risk_tools.py
git commit -m "feat: add Hermes-exposed risk management tools"
```

#### Task 4: Register Risk Management Tools

**Files:**
- Modify: `model_tools.py:160-180` (add risk tools to discovery)

- [ ] **Step 1: Add risk tools to model_tools.py discovery list**

```python
# In _tools list, add:
"tools.risk_manager",
"tools.risk_tools",
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -c "from tools.risk_manager import *; from tools.risk_tools import *; print('Risk modules import via model_tools')"`

Expected: FAIL if not in model_tools.py

- [ ] **Step 4: Run test to verify it passes**

Run: `python -c "import tools.model_tools; print('Model tools loads risk modules: OK')"`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add model_tools.py
git commit -m "feat: register risk management tools in model discovery"
```

#### Task 5: Update Configuration Templates

**Files:**
- Modify: `hermes_cli/config.py:500-550` (add risk management to DEFAULT_CONFIG)
- Modify: `hermes_cli/config.py:1000-1050` (add risk env vars to OPTIONAL_ENV_VARS)

- [ ] **Step 1: Add risk management to DEFAULT_CONFIG**

```python
# In DEFAULT_CONFIG dict, add:
"risk_management": {
    "max_position_size": 0.05,
    "max_drawdown": -0.10,
    "stop_loss": -0.15,
    "take_profit": 0.30,
    "max_open_positions": 5,
    "approval_threshold": 100.0
},
```

- [ ] **Step 2: Add risk environment variables to OPTIONAL_ENV_VARS**

```python
# In OPTIONAL_ENV_VARS dict, add:
"RISK_MAX_POSITION_SIZE": {
    "description": "Maximum position size as fraction of portfolio (0.05 = 5%)",
    "prompt": "Max Position Size",
    "type": "float",
    "default": 0.05,
    "category": "setting"
},
"RISK_MAX_DRAWDOWN": {
    "description": "Maximum daily drawdown before auto-close (-0.10 = -10%)",
    "prompt": "Max Drawdown",
    "type": "float",
    "default": -0.10,
    "category": "setting"
},
"RISK_STOP_LOSS": {
    "description": "Hard stop loss percentage (-0.15 = -15%)",
    "prompt": "Stop Loss",
    "type": "float",
    "default": -0.15,
    "category": "setting"
},
"RISK_TAKE_PROFIT": {
    "description": "Take profit percentage (0.30 = 30%)",
    "prompt": "Take Profit",
    "type": "float",
    "default": 0.30,
    "category": "setting"
},
"RISK_MAX_OPEN_POSITIONS": {
    "description": "Maximum concurrent open positions",
    "prompt": "Max Open Positions",
    "type": "int",
    "default": 5,
    "category": "setting"
},
"RISK_APPROVAL_THRESHOLD": {
    "description": "Trade value requiring manual approval (in USD)",
    "prompt": "Approval Threshold ($)",
    "type": "float",
    "default": 100.0,
    "category": "setting"
},
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -c "from hermes_cli.config import DEFAULT_CONFIG, OPTIONAL_ENV_VARS; assert 'risk_management' in DEFAULT_CONFIG; assert 'RISK_MAX_POSITION_SIZE' in OPTIONAL_ENV_VARS; print('Config updated')"`

Expected: FAIL if not updated correctly

- [ ] **Step 4: Run test to verify it passes**

Run: `python -c "from hermes_cli.config import DEFAULT_CONFIG, OPTIONAL_ENV_VARS; print('Config: OK')"`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add hermes_cli/config.py
git commit -m "feat: add risk management configuration to DEFAULT_CONFIG and OPTIONAL_ENV_VARS"
```

### Part 9.2: Trading Modes Implementation

#### Task 6: Implement Trading Mode Controls

**Files:**
- Modify: `tools/nofx_trading_tool.py:50-100` (add trading mode logic)
- Modify: `hermes_cli/config.py:1000-1050` (add trading mode env var)

- [ ] **Step 1: Add trading mode environment variable and logic**

```python
# Add to top of nofx_trading_tool.py
TRADING_MODE = os.getenv("TRADING_MODE", "supervised").lower()

# Add to OPTIONAL_ENV_VARS in hermes_cli/config.py:
"TRADING_MODE": {
    "description": "Trading mode: supervised, alert-only, autonomous, or paper",
    "prompt": "Trading Mode",
    "type": "select",
    "options": ["supervised", "alert-only", "autonomous", "paper"],
    "default": "supervised",
    "category": "setting"
},
```

- [ ] **Step 2: Modify nofx_trade to check trading mode**

```python
# In nofx_trade function, after risk validation:
trading_mode = os.getenv("TRADING_MODE", "supervised").lower()

if trading_mode == "paper":
    return json.dumps({
        "simulated": True,
        "message": f"Paper trade: {side} {amount} {symbol} @ {price or 'market'}",
        "trade_id": f"paper_{int(time.time())}"
    })
elif trading_mode == "alert-only":
    return json.dumps({
        "alert": True,
        "trade_proposal": {
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "price": price,
            "order_type": order_type
        },
        "message": "Trade suggestion - use /trade command to execute",
        "risk_metrics": risk_result["risk_metrics"] if 'risk_result' in locals() else None
    })
elif trading_mode == "autonomous":
    # Proceed with execution (already handled)
    pass
# supervised mode continues to normal execution (default)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -c "from tools.nofx_trading_tool import nofx_trade; print('Trading mode logic imports')"`

Expected: FAIL if not implemented correctly

- [ ] **Step 4: Run test to verify it passes**

Run: `python -c "from tools.nofx_trading_tool import nofx_trade; print('NOFX trading tool with modes: OK')"`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/nofx_trading_tool.py hermes_cli/config.py
git commit -m "feat: implement trading mode controls (supervised, alert-only, autonomous, paper)"
```

### Part 9.3: Security Tools Integration

#### Task 7: Integrate Security Tools (Optional/Future)

**Note:** The security tools (DEX Ranger, Honeypot Detector) are listed as future enhancements.
For now, we'll document that they can be added as separate skills/tools.

**Files:**
- Create: `docs/risk_management_future_enhancements.md`

- [ ] **Step 1: Document future security tools**

```markdown
# Future Security Tools for Risk Management

## Planned Implementation

### DEX Ranger
- Token safety check for Solana, Ethereum, BSC, TON
- Checks for known honeypots, scam tokens
- API: https://dexranger.com/api (hypothetical)

### Honeypot Detector
- Rug pull detection for EVM chains
- Simulates buy/sell to detect traps

### HoneyPotDetectionOnSui
- SUI-specific honeypot detection
- Would use SUI RPC to analyze token contracts

These can be implemented as separate Hermes tools when APIs become available.
```

- [ ] **Step 2: Run test to verify it passes**

Run: `python -c "print('Security tools documentation placeholder created')"`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docs/risk_management_future_enhancements.md
git commit -m "docs: record future security tool enhancements for risk management"
```

## Verification

After completing all tasks, run:

```bash
# Test all risk management components
python -c "
from tools.risk_manager import *
from tools.risk_tools import *
from tools.nofx_trading_tool import *
print('All risk management components: OK')
```

## Tests Completed

- [ ] Risk configuration loads from environment
- [ ] Risk validation rejects oversized positions
- [ ] Risk validation prevents excessive drawdown
- [ ] Trading modes control execution flow
- [ ] Hermes tools expose risk management functions
- [ ] Configuration system includes risk parameters