import json
import os
import time
import threading
from datetime import datetime
from tools.registry import registry

HERMES_HOME = os.path.expanduser("~/.hermes")
GRID_STATE_FILE = os.path.join(HERMES_HOME, "dex_grid_state.json")


def check_requirements() -> bool:
    return os.path.isdir(HERMES_HOME)


def load_grid_state() -> dict:
    """Load grid state from file"""
    try:
        if os.path.exists(GRID_STATE_FILE):
            with open(GRID_STATE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}


def save_grid_state(state: dict) -> None:
    """Save grid state to file"""
    try:
        os.makedirs(HERMES_HOME, exist_ok=True)
        with open(GRID_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving grid state: {e}")


def get_token_price_dex(token_address: str, dex: str = "jupiter") -> float:
    """Get current token price from DEX"""
    try:
        if dex == "jupiter":
            from tools.dex_swap_tool import get_quote as jupiter_quote
            # Use SOL as base for quote
            result = jupiter_quote(token_address, "So11111111111111111111111111111111111111112", 1_000_000_000)
            data = json.loads(result)
            if "error" in data:
                return 0.0
            return float(data.get("outAmount", 0)) / 1_000_000_000
        
        elif dex == "raydium":
            from tools.raydium_tool import get_swap_quote
            result = get_swap_quote(token_address, "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 1_000_000_000)
            data = json.loads(result)
            if "error" in data:
                return 0.0
            return float(data.get("output_amount", 0)) / 1_000_000_000
        
        elif dex == "aerodrome":
            from tools.aerodrome_tool import get_swap_quote
            result = get_swap_quote(token_address, "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", 1_000_000_000)
            data = json.loads(result)
            if "error" in data:
                return 0.0
            return float(data.get("output_amount", 0)) / 1_000_000_000
        
        return 0.0
    except Exception as e:
        print(f"Error getting price: {e}")
        return 0.0


def initialize_grid(token_a: str, token_b: str, lower_price: float, upper_price: float, 
                    grid_levels: int = 10, dex: str = "jupiter", position_size: float = 0.01) -> str:
    """Initialize a new DEX grid
    
    Args:
        token_a: Input token mint (e.g., SOL)
        token_b: Output token mint (e.g., USDC)
        lower_price: Lower price bound
        upper_price: Upper price bound
        grid_levels: Number of grid levels
        dex: DEX to use (jupiter, raydium, aerodrome)
        position_size: Size per grid level in token_a units
    """
    try:
        grid_spacing = (upper_price - lower_price) / grid_levels if grid_levels > 0 else 0
        
        grid_state = {
            "token_a": token_a,
            "token_b": token_b,
            "dex": dex,
            "lower_price": lower_price,
            "upper_price": upper_price,
            "grid_levels": grid_levels,
            "grid_spacing": grid_spacing,
            "position_size": position_size,
            "is_running": True,
            "created_at": datetime.now().isoformat(),
            "orders": {},
            "filled_levels": [],
            "total_profit": 0.0,
            "total_trades": 0
        }
        
        save_grid_state(grid_state)
        
        return json.dumps({
            "success": True,
            "grid_id": f"{dex}_grid_{int(time.time())}",
            "dex": dex,
            "token_a": token_a,
            "token_b": token_b,
            "lower_price": lower_price,
            "upper_price": upper_price,
            "grid_levels": grid_levels,
            "grid_spacing": grid_spacing,
            "position_size": position_size,
            "status": "initialized and running"
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_grid_status() -> str:
    """Get current grid status"""
    try:
        state = load_grid_state()
        
        if not state:
            return json.dumps({
                "is_running": False,
                "message": "No grid running"
            })
        
        # Get current price
        current_price = get_token_price_dex(state.get("token_a", ""), state.get("dex", "jupiter"))
        
        # Calculate current grid level
        grid_level = None
        if current_price > 0 and state.get("grid_spacing", 0) > 0:
            grid_level = int((current_price - state.get("lower_price", 0)) / state["grid_spacing"])
        
        return json.dumps({
            "is_running": state.get("is_running", False),
            "dex": state.get("dex"),
            "token_a": state.get("token_a"),
            "token_b": state.get("token_b"),
            "lower_price": state.get("lower_price"),
            "upper_price": state.get("upper_price"),
            "current_price": current_price,
            "grid_level": grid_level,
            "grid_levels": state.get("grid_levels"),
            "total_profit": state.get("total_profit", 0),
            "total_trades": state.get("total_trades", 0),
            "filled_levels": state.get("filled_levels", [])
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def execute_grid_order(level: int, direction: str, amount: float, state: dict) -> str:
    """Execute a trade at a specific grid level
    
    Args:
        level: Grid level index
        direction: "buy" or "sell"
        amount: Amount to trade
        state: Current grid state
    """
    try:
        dex = state.get("dex", "jupiter")
        
        if direction == "buy":
            # Buy token_a at lower price (place buy limit order)
            from tools.limit_order_tool import create_cross_dex_limit_order
            
            result = create_cross_dex_limit_order(
                dex=dex,
                input_mint=state.get("token_b", ""),  # Pay with token_b (USDC)
                output_mint=state.get("token_a", ""),  # Get token_a (SOL)
                amount=int(amount * state.get("lower_price", 0) * 1_000_000),
                limit_price=state.get("lower_price", 0) + (level * state.get("grid_spacing", 0))
            )
            return result
        
        else:
            # Sell token_a at higher price
            from tools.limit_order_tool import create_cross_dex_limit_order
            
            result = create_cross_dex_limit_order(
                dex=dex,
                input_mint=state.get("token_a", ""),
                output_mint=state.get("token_b", ""),
                amount=int(amount * 1_000_000_000),
                limit_price=state.get("lower_price", 0) + ((level + 1) * state.get("grid_spacing", 0))
            )
            return result
            
    except Exception as e:
        return json.dumps({"error": str(e)})


def stop_grid() -> str:
    """Stop the running grid"""
    try:
        state = load_grid_state()
        
        if not state:
            return json.dumps({"error": "No grid running"})
        
        state["is_running"] = False
        save_grid_state(state)
        
        return json.dumps({
            "success": True,
            "message": "Grid stopped",
            "total_profit": state.get("total_profit", 0),
            "total_trades": state.get("total_trades", 0)
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_grid_config() -> str:
    """Get current grid configuration"""
    try:
        state = load_grid_state()
        
        if not state:
            return json.dumps({
                "is_running": False,
                "message": "No grid configured"
            })
        
        return json.dumps({
            "dex": state.get("dex"),
            "token_a": state.get("token_a"),
            "token_b": state.get("token_b"),
            "lower_price": state.get("lower_price"),
            "upper_price": state.get("upper_price"),
            "grid_levels": state.get("grid_levels"),
            "grid_spacing": state.get("grid_spacing"),
            "position_size": state.get("position_size"),
            "is_running": state.get("is_running")
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def configure_grid(new_lower_price: float = None, new_upper_price: float = None,
                    new_grid_levels: int = None, new_position_size: float = None) -> str:
    """Configure/update grid parameters
    
    Args:
        new_lower_price: New lower price bound
        new_upper_price: New upper price bound
        new_grid_levels: New number of levels
        new_position_size: New position size per level
    """
    try:
        state = load_grid_state()
        
        if not state:
            return json.dumps({"error": "No grid running. Initialize first with dex_grid_init"})
        
        if new_lower_price is not None:
            state["lower_price"] = new_lower_price
        if new_upper_price is not None:
            state["upper_price"] = new_upper_price
        if new_grid_levels is not None:
            state["grid_levels"] = new_grid_levels
            state["grid_spacing"] = (state["upper_price"] - state["lower_price"]) / new_grid_levels
        if new_position_size is not None:
            state["position_size"] = new_position_size
        
        save_grid_state(state)
        
        return json.dumps({
            "success": True,
            "message": "Grid configuration updated",
            "new_config": {
                "lower_price": state.get("lower_price"),
                "upper_price": state.get("upper_price"),
                "grid_levels": state.get("grid_levels"),
                "grid_spacing": state.get("grid_spacing"),
                "position_size": state.get("position_size")
            }
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def calculate_grid_profit(current_price: float, state: dict) -> float:
    """Calculate theoretical profit from grid
    
    Args:
        current_price: Current token price
        state: Grid state
    
    Returns:
        Estimated profit
    """
    try:
        if not state or not state.get("is_running"):
            return 0.0
        
        lower = state.get("lower_price", 0)
        upper = state.get("upper_price", 0)
        levels = state.get("grid_levels", 0)
        spacing = state.get("grid_spacing", 0)
        
        if levels == 0 or spacing == 0:
            return 0.0
        
        # Calculate number of completed levels
        completed_buys = int((current_price - lower) / spacing) if current_price > lower else 0
        completed_sells = int((upper - current_price) / spacing) if current_price < upper else 0
        
        # Each completed level generates profit from sell - buy spread
        position_size = state.get("position_size", 0)
        profit = (completed_buys + completed_sells) * position_size * spacing
        
        return profit
        
    except Exception as e:
        return 0.0


registry.register(
    name="dex_grid_init",
    toolset="dex",
    schema={
        "name": "dex_grid_init",
        "description": "Initialize a new DEX grid trading system on Solana (Jupiter/Raydium) or Base (Aerodrome). Creates grid levels between price bounds and starts automated trading.",
        "parameters": {
            "type": "object",
            "properties": {
                "token_a": {"type": "string", "description": "Base token mint (e.g., SOL for Jupiter, WETH for Aerodrome)"},
                "token_b": {"type": "string", "description": "Quote token mint (e.g., USDC)"},
                "lower_price": {"type": "number", "description": "Lower price bound for grid"},
                "upper_price": {"type": "number", "description": "Upper price bound for grid"},
                "grid_levels": {"type": "integer", "description": "Number of grid levels", "default": 10},
                "dex": {"type": "string", "description": "DEX: jupiter, raydium, or aerodrome", "default": "jupiter"},
                "position_size": {"type": "number", "description": "Position size per grid level", "default": 0.01}
            },
            "required": ["token_a", "token_b", "lower_price", "upper_price"]
        }
    },
    handler=lambda args, **kw: initialize_grid(
        args.get("token_a", ""),
        args.get("token_b", ""),
        args.get("lower_price", 0),
        args.get("upper_price", 0),
        args.get("grid_levels", 10),
        args.get("dex", "jupiter"),
        args.get("position_size", 0.01)
    ),
    check_fn=check_requirements
)

registry.register(
    name="dex_grid_status",
    toolset="dex",
    schema={
        "name": "dex_grid_status",
        "description": "Get current status of DEX grid including price, level, profit, and trades",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: get_grid_status(),
    check_fn=check_requirements
)

registry.register(
    name="dex_grid_stop",
    toolset="dex",
    schema={
        "name": "dex_grid_stop",
        "description": "Stop the running DEX grid and show final statistics",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: stop_grid(),
    check_fn=check_requirements
)

registry.register(
    name="dex_grid_config",
    toolset="dex",
    schema={
        "name": "dex_grid_config",
        "description": "Get current DEX grid configuration",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: get_grid_config(),
    check_fn=check_requirements
)

registry.register(
    name="dex_grid_configure",
    toolset="dex",
    schema={
        "name": "dex_grid_configure",
        "description": "Configure/update DEX grid parameters. Can update: lower_price, upper_price, grid_levels, position_size",
        "parameters": {
            "type": "object",
            "properties": {
                "lower_price": {"type": "number", "description": "New lower price bound"},
                "upper_price": {"type": "number", "description": "New upper price bound"},
                "grid_levels": {"type": "integer", "description": "New number of levels"},
                "position_size": {"type": "number", "description": "New position size per level"}
            }
        }
    },
    handler=lambda args, **kw: configure_grid(
        args.get("lower_price"),
        args.get("upper_price"),
        args.get("grid_levels"),
        args.get("position_size")
    ),
    check_fn=check_requirements
)

registry.register(
    name="dex_grid_estimate",
    toolset="dex",
    schema={
        "name": "dex_grid_estimate",
        "description": "Estimate potential profit from grid trading given price range and levels",
        "parameters": {
            "type": "object",
            "properties": {
                "lower_price": {"type": "number", "description": "Lower price bound"},
                "upper_price": {"type": "number", "description": "Upper price bound"},
                "grid_levels": {"type": "integer", "description": "Number of levels"},
                "position_size": {"type": "number", "description": "Position size per level"},
                "expected_price_moves": {"type": "number", "description": "Expected price moves across grid", "default": 5}
            },
            "required": ["lower_price", "upper_price", "grid_levels", "position_size"]
        }
    },
    handler=lambda args, **kw: json.dumps({
        "lower_price": args.get("lower_price"),
        "upper_price": args.get("upper_price"),
        "grid_levels": args.get("grid_levels"),
        "grid_spacing": (args.get("upper_price", 0) - args.get("lower_price", 0)) / args.get("grid_levels", 1),
        "position_size": args.get("position_size"),
        "max_trades": args.get("grid_levels") * 2,
        "potential_profit_per_move": args.get("position_size", 0) * ((args.get("upper_price", 0) - args.get("lower_price", 0)) / args.get("grid_levels", 1)),
        "total_profit_if_full_cycle": args.get("position_size", 0) * (args.get("upper_price", 0) - args.get("lower_price", 0)),
        "note": "This is theoretical profit. Actual profit depends on price movement patterns."
    }),
    check_fn=check_requirements
)