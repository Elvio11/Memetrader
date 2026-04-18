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
    """Update a risk parameter (stored in environment for session)"""
    valid_params = [
        "max_position_size", "max_drawdown", "stop_loss", 
        "take_profit", "max_open_positions", "approval_threshold"
    ]
    
    if parameter not in valid_params:
        return json.dumps({"error": f"Invalid parameter. Valid: {valid_params}"})
    
    try:
        if parameter in ["max_open_positions"]:
            converted = int(value)
        else:
            converted = float(value)
        
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
    """Pre-check trade against risk parameters without executing"""
    trade_value = amount * (price if price else 1.0)
    current_positions = 0
    daily_pnl = 0.0
    
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


registry.register(
    name="risk_parameters",
    toolset="trading",
    schema={
        "name": "risk_parameters",
        "description": "Get current risk management parameters including max position size, drawdown limits, stop loss, and approval thresholds",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: get_risk_parameters(),
)

registry.register(
    name="risk_update_parameter",
    toolset="trading",
    schema={
        "name": "risk_update_parameter",
        "description": "Update a risk management parameter. Note: changes are session-only.",
        "parameters": {
            "type": "object",
            "properties": {
                "parameter": {
                    "type": "string",
                    "description": "Parameter name: max_position_size, max_drawdown, stop_loss, take_profit, max_open_positions, approval_threshold"
                },
                "value": {
                    "type": "string",
                    "description": "New value for the parameter"
                }
            },
            "required": ["parameter", "value"]
        }
    },
    handler=lambda args, **kw: update_risk_parameter(
        args.get("parameter", ""),
        args.get("value", "")
    ),
)

registry.register(
    name="risk_check_trade",
    toolset="trading",
    schema={
        "name": "risk_check_trade",
        "description": "Pre-check a trade proposal against risk parameters without executing",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Trading pair"},
                "side": {"type": "string", "description": "buy or sell"},
                "amount": {"type": "number", "description": "Order amount"},
                "price": {"type": "number", "description": "Optional price"},
                "portfolio_value": {"type": "number", "description": "Total portfolio value", "default": 1000.0}
            },
            "required": ["symbol", "side", "amount"]
        }
    },
    handler=lambda args, **kw: check_trade_risk(
        args.get("symbol", ""),
        args.get("side", ""),
        args.get("amount", 0),
        args.get("price"),
        args.get("portfolio_value", 1000.0)
    ),
)