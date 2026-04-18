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