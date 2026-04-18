import json
import os
import requests
from tools.registry import registry

NOFX_API_URL = os.getenv("NOFX_API_URL", "http://localhost:8080")
NOFX_API_TOKEN = os.getenv("NOFX_API_TOKEN", "")
HERMES_HOME = os.path.expanduser("~/.hermes")


def check_requirements() -> bool:
    """Check if Hermes home exists (NOFX connection is optional, checked per-call)"""
    return os.path.isdir(HERMES_HOME)


def get_headers() -> dict:
    if NOFX_API_TOKEN:
        return {"Authorization": f"Bearer {NOFX_API_TOKEN}"}
    return {}


def get_traders() -> str:
    """Get list of available traders from NOFX"""
    try:
        url = f"{NOFX_API_URL}/api/traders"
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            traders = response.json()
            return json.dumps({"traders": traders, "count": len(traders) if isinstance(traders, list) else 0})
        elif response.status_code == 401:
            return json.dumps({"error": "NOFX API token required", "hint": "Set NOFX_API_TOKEN env var"})
        else:
            return json.dumps({"error": f"NOFX API returned {response.status_code}"})
    except Exception as e:
        return json.dumps({"error": str(e), "hint": "Make sure NOFX is running at " + NOFX_API_URL})


def get_trader_status(trader_id: str) -> str:
    """Get status of a specific trader including grid info"""
    try:
        url = f"{NOFX_API_URL}/api/traders/{trader_id}"
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            trader = response.json()
            return json.dumps({
                "trader_id": trader_id,
                "name": trader.get("name"),
                "is_running": trader.get("is_running", False),
                "exchange": trader.get("exchange"),
                "strategy": trader.get("strategy"),
                "status": "running" if trader.get("is_running") else "stopped"
            })
        elif response.status_code == 404:
            return json.dumps({"error": f"Trader {trader_id} not found"})
        else:
            return json.dumps({"error": f"NOFX API returned {response.status_code}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def start_grid(trader_id: str) -> str:
    """Start grid trading on a NOFX trader"""
    try:
        url = f"{NOFX_API_URL}/api/traders/{trader_id}/start"
        response = requests.post(url, headers=get_headers(), timeout=30)
        
        if response.status_code == 200:
            return json.dumps({
                "success": True,
                "trader_id": trader_id,
                "message": "Grid trading started"
            })
        elif response.status_code == 401:
            return json.dumps({"error": "NOFX API token required"})
        else:
            return json.dumps({"error": f"Failed to start: {response.status_code}", "details": response.text})
    except Exception as e:
        return json.dumps({"error": str(e)})


def stop_grid(trader_id: str) -> str:
    """Stop grid trading on a NOFX trader"""
    try:
        url = f"{NOFX_API_URL}/api/traders/{trader_id}/stop"
        response = requests.post(url, headers=get_headers(), timeout=30)
        
        if response.status_code == 200:
            return json.dumps({
                "success": True,
                "trader_id": trader_id,
                "message": "Grid trading stopped"
            })
        elif response.status_code == 401:
            return json.dumps({"error": "NOFX API token required"})
        else:
            return json.dumps({"error": f"Failed to stop: {response.status_code}", "details": response.text})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_grid_config(trader_id: str) -> str:
    """Get current grid configuration for a trader"""
    try:
        url = f"{NOFX_API_URL}/api/traders/{trader_id}/config"
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            config = response.json()
            return json.dumps({
                "trader_id": trader_id,
                "config": config
            })
        elif response.status_code == 404:
            return json.dumps({"error": f"Trader {trader_id} not found"})
        else:
            return json.dumps({"error": f"NOFX API returned {response.status_code}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def configure_grid(trader_id: str, grid_levels: int = None, grid_spacing: float = None, 
                   position_size: float = None, max_position: float = None,
                   upper_price: float = None, lower_price: float = None) -> str:
    """Configure grid trading parameters
    
    Args:
        trader_id: Trader ID to configure
        grid_levels: Number of grid levels
        grid_spacing: Percentage spacing between levels
        position_size: Size per grid level
        max_position: Maximum total position size
        upper_price: Upper price bound
        lower_price: Lower price bound
    """
    try:
        url = f"{NOFX_API_URL}/api/traders/{trader_id}"
        
        # Build config update
        config = {}
        if grid_levels is not None:
            config["grid_levels"] = grid_levels
        if grid_spacing is not None:
            config["grid_spacing"] = grid_spacing
        if position_size is not None:
            config["position_size"] = position_size
        if max_position is not None:
            config["max_position"] = max_position
        if upper_price is not None:
            config["upper_price"] = upper_price
        if lower_price is not None:
            config["lower_price"] = lower_price
        
        response = requests.put(url, json={"config": config}, headers=get_headers(), timeout=15)
        
        if response.status_code == 200:
            return json.dumps({
                "success": True,
                "trader_id": trader_id,
                "updated_config": config,
                "message": "Grid configuration updated"
            })
        elif response.status_code == 401:
            return json.dumps({"error": "NOFX API token required"})
        elif response.status_code == 404:
            return json.dumps({"error": f"Trader {trader_id} not found"})
        else:
            return json.dumps({"error": f"Failed to configure: {response.status_code}", "details": response.text})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_grid_risk_info(trader_id: str) -> str:
    """Get grid trading risk information"""
    try:
        url = f"{NOFX_API_URL}/api/traders/{trader_id}/grid-risk"
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            risk_info = response.json()
            return json.dumps({
                "trader_id": trader_id,
                "risk_info": risk_info
            })
        elif response.status_code == 404:
            return json.dumps({"error": f"Trader {trader_id} not found or no grid running"})
        else:
            return json.dumps({"error": f"NOFX API returned {response.status_code}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_grid_status(trader_id: str) -> str:
    """Get comprehensive grid status including positions and orders"""
    try:
        # Get trader status
        status_result = get_trader_status(trader_id)
        status_data = json.loads(status_result)
        
        if "error" in status_data:
            return status_result
        
        # Get risk info if running
        risk_result = get_grid_risk_info(trader_id)
        risk_data = json.loads(risk_result)
        
        if "error" in risk_data:
            return json.dumps({
                "trader_id": trader_id,
                "status": status_data.get("status"),
                "exchange": status_data.get("exchange"),
                "grid_not_running": True
            })
        
        return json.dumps({
            "trader_id": trader_id,
            "status": status_data.get("status"),
            "exchange": status_data.get("exchange"),
            "grid_running": True,
            "risk": risk_data.get("risk_info", {})
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="grid_traders_list",
    toolset="trading",
    schema={
        "name": "grid_traders_list",
        "description": "Get list of available NOFX traders that support grid trading",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: get_traders(),
    check_fn=check_requirements
)

registry.register(
    name="grid_trader_status",
    toolset="trading",
    schema={
        "name": "grid_trader_status",
        "description": "Get status of a specific NOFX trader (running/stopped)",
        "parameters": {
            "type": "object",
            "properties": {
                "trader_id": {"type": "string", "description": "Trader ID to query"}
            },
            "required": ["trader_id"]
        }
    },
    handler=lambda args, **kw: get_trader_status(args.get("trader_id", "")),
    check_fn=check_requirements
)

registry.register(
    name="grid_start",
    toolset="trading",
    schema={
        "name": "grid_start",
        "description": "Start grid trading on a NOFX trader. The trader must be configured with grid strategy.",
        "parameters": {
            "type": "object",
            "properties": {
                "trader_id": {"type": "string", "description": "Trader ID to start grid on"}
            },
            "required": ["trader_id"]
        }
    },
    handler=lambda args, **kw: start_grid(args.get("trader_id", "")),
    check_fn=check_requirements
)

registry.register(
    name="grid_stop",
    toolset="trading",
    schema={
        "name": "grid_stop",
        "description": "Stop grid trading on a NOFX trader",
        "parameters": {
            "type": "object",
            "properties": {
                "trader_id": {"type": "string", "description": "Trader ID to stop grid on"}
            },
            "required": ["trader_id"]
        }
    },
    handler=lambda args, **kw: stop_grid(args.get("trader_id", "")),
    check_fn=check_requirements
)

registry.register(
    name="grid_config_get",
    toolset="trading",
    schema={
        "name": "grid_config_get",
        "description": "Get current grid configuration for a NOFX trader",
        "parameters": {
            "type": "object",
            "properties": {
                "trader_id": {"type": "string", "description": "Trader ID to get config for"}
            },
            "required": ["trader_id"]
        }
    },
    handler=lambda args, **kw: get_grid_config(args.get("trader_id", "")),
    check_fn=check_requirements
)

registry.register(
    name="grid_configure",
    toolset="trading",
    schema={
        "name": "grid_configure",
        "description": "Configure grid trading parameters for a NOFX trader. Can update: grid_levels, grid_spacing, position_size, max_position, upper_price, lower_price",
        "parameters": {
            "type": "object",
            "properties": {
                "trader_id": {"type": "string", "description": "Trader ID to configure"},
                "grid_levels": {"type": "integer", "description": "Number of grid levels"},
                "grid_spacing": {"type": "number", "description": "Percentage spacing between levels (e.g., 1.0 = 1%)"},
                "position_size": {"type": "number", "description": "Position size per grid level"},
                "max_position": {"type": "number", "description": "Maximum total position size"},
                "upper_price": {"type": "number", "description": "Upper price bound for grid"},
                "lower_price": {"type": "number", "description": "Lower price bound for grid"}
            },
            "required": ["trader_id"]
        }
    },
    handler=lambda args, **kw: configure_grid(
        args.get("trader_id", ""),
        args.get("grid_levels"),
        args.get("grid_spacing"),
        args.get("position_size"),
        args.get("max_position"),
        args.get("upper_price"),
        args.get("lower_price")
    ),
    check_fn=check_requirements
)

registry.register(
    name="grid_risk_info",
    toolset="trading",
    schema={
        "name": "grid_risk_info",
        "description": "Get grid trading risk information including position, drawdown, and exposure",
        "parameters": {
            "type": "object",
            "properties": {
                "trader_id": {"type": "string", "description": "Trader ID to get risk info for"}
            },
            "required": ["trader_id"]
        }
    },
    handler=lambda args, **kw: get_grid_risk_info(args.get("trader_id", "")),
    check_fn=check_requirements
)

registry.register(
    name="grid_status",
    toolset="trading",
    schema={
        "name": "grid_status",
        "description": "Get comprehensive grid status including running state, positions, orders, and risk",
        "parameters": {
            "type": "object",
            "properties": {
                "trader_id": {"type": "string", "description": "Trader ID to get status for"}
            },
            "required": ["trader_id"]
        }
    },
    handler=lambda args, **kw: get_grid_status(args.get("trader_id", "")),
    check_fn=check_requirements
)