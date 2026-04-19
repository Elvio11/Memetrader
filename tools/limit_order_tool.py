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
            from tools.raydium_limit_tool import create_raydium_clmm_limit_order
            
            return create_raydium_clmm_limit_order(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=amount,
                limit_price=limit_price,
                private_key=private_key,
                user_public_key=user_public_key,
                version="devnet"  # Default to devnet, could be made configurable
            )
        
        elif dex.lower() == "cetus":
            from tools.cetus_tool import create_limit_order as cetus_limit
            
            return cetus_limit(input_mint, output_mint, amount, limit_price)
        
        elif dex.lower() == "aerodrome":
            from tools.aerodrome_limit_tool import create_aerodrome_clmm_limit_order
            
            return create_aerodrome_clmm_limit_order(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=amount,
                limit_price=limit_price,
                private_key=private_key,
                user_public_key=user_public_key,
                version="mainnet"  # Default to mainnet for Aerodrome
            )
        
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
        
        if dex.lower() in ("raydium", "all"):
            from tools.raydium_limit_tool import query_raydium_limit_orders
            results["raydium"] = json.loads(query_raydium_limit_orders(wallet))
            
        if dex.lower() in ("aerodrome", "all"):
            from tools.aerodrome_limit_tool import query_aerodrome_limit_orders
            results["aerodrome"] = json.loads(query_aerodrome_limit_orders(wallet))
            
        # Cetus limit order query - Cetus doesn't have a separate query function, 
        # so we'll note that limit orders are handled through position tracking
        if dex.lower() in ("cetus", "all") and "cetus" not in results:
            results["cetus"] = json.dumps({
                "dex": "cetus",
                "orders": [],
                "count": 0,
                "note": "Cetus uses concentrated liquidity pools for limit-order-like functionality. Use position tracking for active orders."
            })
        
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
        
        elif dex.lower() == "raydium":
            from tools.raydium_limit_tool import cancel_raydium_limit_order
            return cancel_raydium_limit_order(
                order_id=order_public_key,
                wallet=user_public_key,
                private_key=private_key
            )
        elif dex.lower() == "aerodrome":
            from tools.aerodrome_limit_tool import cancel_aerodrome_limit_order
            return cancel_aerodrome_limit_order(
                order_id=order_public_key,
                wallet=user_public_key,
                private_key=private_key
            )
        else:
            return json.dumps({
                "error": f"Cancel not supported for {dex}. Supported: jupiter, raydium, aerodrome"
            })
    
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="limit_order_create",
    toolset="dex",
    schema={
        "name": "limit_order_create",
        "description": "Create a limit order across multiple DEXs. Supports Jupiter (Solana), Raydium (Solana) using CLMM pools, Cetus (SUI), and Aerodrome (Base) using Slipstream concentrated liquidity pools.",
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
        "description": "Cancel a limit order. Supports Jupiter (Solana), Raydium (Solana), and Aerodrome (Base).",
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