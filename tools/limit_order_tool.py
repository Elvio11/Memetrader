import json
import os
from tools.registry import registry

HERMES_HOME = os.path.expanduser("~/.hermes")


def check_requirements() -> bool:
    return os.path.isdir(HERMES_HOME)


def create_cross_dex_limit_order(
    dex: str,
    input_mint: str,
    output_mint: str,
    amount: int,
    limit_price: float,
    private_key: str = None,
    user_public_key: str = None
) -> str:
    """Create a limit order across multiple DEXs
    
    Args:
        dex: DEX to use - "jupiter", "raydium", "cetus", "aerodrome"
        input_mint: Input token mint/address
        output_mint: Output token mint/address
        amount: Amount to sell (in smallest unit)
        limit_price: Target price (as a ratio, e.g., 0.00015 SOL/USDC = 0.00015)
        private_key: Optional private key for signing
        user_public_key: Wallet address
    
    Returns:
        JSON with order details or transaction
    """
    try:
        if dex.lower() == "jupiter":
            from tools.jupiter_limit_tool import create_limit_order as jupiter_create
            
            out_amount = int(amount * limit_price)
            
            if not private_key or not user_public_key:
                return json.dumps({
                    "dex": "jupiter",
                    "input_mint": input_mint,
                    "output_mint": output_mint,
                    "amount": amount,
                    "limit_price": limit_price,
                    "status": "pending",
                    "note": "Provide private_key and user_public_key to create the order"
                })
            
            return jupiter_create(input_mint, output_mint, amount, out_amount, user_public_key, private_key)
        
        elif dex.lower() == "raydium":
            from tools.raydium_tool import get_swap_quote as raydium_quote
            
            quote = json.loads(raydium_quote(input_mint, output_mint, amount))
            
            if "error" in quote:
                return json.dumps({"error": f"Raydium quote failed: {quote['error']}"})
            
            out_amount = int(quote.get("output_amount", 0))
            target_amount = int(amount * limit_price)
            
            if out_amount >= target_amount:
                return json.dumps({
                    "dex": "raydium",
                    "status": "ready_to_execute",
                    "current_price": out_amount / amount,
                    "limit_price": limit_price,
                    "input_amount": amount,
                    "expected_output": out_amount,
                    "note": "Price above limit - would execute as market order"
                })
            else:
                return json.dumps({
                    "dex": "raydium",
                    "status": "price_below_limit",
                    "current_price": out_amount / amount,
                    "limit_price": limit_price,
                    "input_amount": amount,
                    "expected_output": out_amount,
                    "note": f"Current price {out_amount/amount:.8f} below limit {limit_price:.8f} - order not triggered"
                })
        
        elif dex.lower() == "cetus":
            from tools.cetus_tool import create_limit_order as cetus_limit
            
            return cetus_limit(input_mint, output_mint, amount, limit_price)
        
        elif dex.lower() == "aerodrome":
            from tools.aerodrome_tool import get_swap_quote as aero_quote
            
            quote = json.loads(aero_quote(input_mint, output_mint, amount))
            
            if "error" in quote:
                return json.dumps({"error": f"Aerodrome quote failed: {quote['error']}"})
            
            return json.dumps({
                "dex": "aerodrome",
                "status": "pending",
                "input_mint": input_mint,
                "output_mint": output_mint,
                "amount": amount,
                "limit_price": limit_price,
                "quote": quote,
                "note": "Aerodrome limit orders require SDK integration"
            })
        
        else:
            return json.dumps({"error": f"Unknown DEX: {dex}. Supported: jupiter, raydium, cetus, aerodrome"})
    
    except Exception as e:
        return json.dumps({"error": str(e)})


def query_limit_orders(dex: str, wallet: str) -> str:
    """Query open limit orders across multiple DEXs
    
    Args:
        dex: DEX to query - "jupiter", "raydium", "cetus", "aerodrome", "all"
        wallet: Wallet address to query orders for
    
    Returns:
        JSON with open orders
    """
    try:
        results = {}
        
        if dex.lower() in ("jupiter", "all"):
            from tools.jupiter_limit_tool import query_open_orders
            results["jupiter"] = json.loads(query_open_orders(wallet))
        
        return json.dumps(results)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


def cancel_limit_order(dex: str, order_public_key: str, user_public_key: str, private_key: str) -> str:
    """Cancel a limit order
    
    Args:
        dex: DEX - "jupiter", "raydium", "cetus", "aerodrome"
        order_public_key: Order public key to cancel
        user_public_key: User's wallet address
        private_key: Private key for signing
    
    Returns:
        JSON with cancellation result
    """
    try:
        if dex.lower() == "jupiter":
            from tools.jupiter_limit_tool import cancel_limit_order
            return cancel_limit_order(order_public_key, user_public_key, private_key)
        
        else:
            return json.dumps({
                "error": f"Cancel not supported for {dex}. Only Jupiter cancel is available."
            })
    
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="limit_order_create",
    toolset="dex",
    schema={
        "name": "limit_order_create",
        "description": "Create a limit order across multiple DEXs. Currently supports Jupiter (Solana), Raydium (Solana), Cetus (SUI), and Aerodrome (Base). Jupiter is fully functional.",
        "parameters": {
            "type": "object",
            "properties": {
                "dex": {
                    "type": "string",
                    "description": "DEX to use: jupiter, raydium, cetus, aerodrome"
                },
                "input_mint": {
                    "type": "string",
                    "description": "Input token mint address"
                },
                "output_mint": {
                    "type": "string",
                    "description": "Output token mint address"
                },
                "amount": {
                    "type": "integer",
                    "description": "Amount to sell (in smallest unit)"
                },
                "limit_price": {
                    "type": "number",
                    "description": "Target price (as decimal ratio, e.g., 0.00015 means you want at least 0.00015 output per 1 input)"
                },
                "private_key": {
                    "type": "string",
                    "description": "Optional private key for signing"
                },
                "user_public_key": {
                    "type": "string",
                    "description": "Your wallet address"
                }
            },
            "required": ["dex", "input_mint", "output_mint", "amount", "limit_price"]
        }
    },
    handler=lambda args, **kw: create_cross_dex_limit_order(
        args.get("dex", ""),
        args.get("input_mint", ""),
        args.get("output_mint", ""),
        args.get("amount", 0),
        args.get("limit_price", 0),
        args.get("private_key"),
        args.get("user_public_key")
    ),
    check_fn=check_requirements
)

registry.register(
    name="limit_order_query",
    toolset="dex",
    schema={
        "name": "limit_order_query",
        "description": "Query open limit orders across multiple DEXs",
        "parameters": {
            "type": "object",
            "properties": {
                "dex": {
                    "type": "string",
                    "description": "DEX to query: jupiter, raydium, cetus, aerodrome, all",
                    "default": "all"
                },
                "wallet": {
                    "type": "string",
                    "description": "Wallet address to query orders for"
                }
            },
            "required": ["wallet"]
        }
    },
    handler=lambda args, **kw: query_limit_orders(
        args.get("dex", "all"),
        args.get("wallet", "")
    ),
    check_fn=check_requirements
)

registry.register(
    name="limit_order_cancel",
    toolset="dex",
    schema={
        "name": "limit_order_cancel",
        "description": "Cancel a limit order. Currently supports Jupiter (Solana).",
        "parameters": {
            "type": "object",
            "properties": {
                "dex": {
                    "type": "string",
                    "description": "DEX: jupiter (only supported currently)",
                    "default": "jupiter"
                },
                "order_public_key": {
                    "type": "string",
                    "description": "Order public key to cancel"
                },
                "user_public_key": {
                    "type": "string",
                    "description": "Your wallet address"
                },
                "private_key": {
                    "type": "string",
                    "description": "Private key for signing"
                }
            },
            "required": ["dex", "order_public_key", "user_public_key", "private_key"]
        }
    },
    handler=lambda args, **kw: cancel_limit_order(
        args.get("dex", "jupiter"),
        args.get("order_public_key", ""),
        args.get("user_public_key", ""),
        args.get("private_key", "")
    ),
    check_fn=check_requirements
)