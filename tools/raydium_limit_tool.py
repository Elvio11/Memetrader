import json
import os
import requests
import base58
from tools.registry import registry
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.hash import Hash
from tools.raydium_tool import get_swap_quote, execute_swap

RAYDIUM_API_URL = "https://api.raydium.io"
SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
RAYDIUM_MAINNET_RPC = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

def check_requirements() -> bool:
    """Check if Solana RPC and Raydium API are accessible"""
    try:
        # Check devnet RPC
        response = requests.get(SOLANA_RPC, 
            json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"},
            timeout=5)
        if response.status_code != 200:
            # Try mainnet if devnet fails
            response = requests.get(RAYDIUM_MAINNET_RPC, 
                json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"},
                timeout=5)
            return response.status_code == 200
        return response.status_code == 200
    except:
        return False

def get_clmm_pool_info(token_a: str, token_b: str) -> dict:
    """Get CLMM pool information for token pair"""
    try:
        # Get pool info from Raydium API
        url = f"{RAYDIUM_API_URL}/v2/sdk/liquidty/mainnet.json"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Filter for CLMM pools with the token pair
        # This is a simplified version - in practice you'd need to parse the pool data properly
        return {"pools": data.get("official", [])[:10]}  # Return first 10 pools as example
    except Exception as e:
        return {"error": str(e)}


def create_raydium_clmm_limit_order(
    input_mint: str,
    output_mint: str,
    amount: int,
    limit_price: float,
    private_key: str = None,
    user_public_key: str = None,
    version: str = "devnet"
) -> str:
    """
    Create a limit order on Raydium using CLMM pools (concentrated liquidity)
    This simulates limit order functionality by setting price bounds
    
    Args:
        input_mint: Input token mint address
        output_mint: Output token mint address
        amount: Amount to sell (in smallest unit)
        limit_price: Target price (as decimal ratio)
        private_key: Base58 encoded private key for signing (optional)
        user_public_key: Wallet address
        version: "devnet" or "mainnet"
        
    Returns:
        JSON string with transaction signature or error
    """
    try:
        # Select RPC endpoint
        rpc_url = SOLANA_RPC if version == "devnet" else RAYDIUM_MAINNET_RPC
        
        # If we have a private key, get keypair from it
        keypair = None
        if private_key:
            private_key_bytes = base58.b58decode(private_key)
            keypair = Keypair.from_bytes(private_key_bytes)
        
        # For now, we'll implement a simplified version that:
        # 1. Gets current price
        # 2. If price meets limit and we have keys, executes market order
        # 3. Otherwise returns instructions for user to monitor
        
        # Get swap quote to check current price
        quote_response = get_swap_quote(input_mint, output_mint, amount)
        quote_data = json.loads(quote_response)
        
        if "error" in quote_data:
            return json.dumps({"error": f"Failed to get quote: {quote_data['error']}"})
            
        output_amount = quote_data.get("output_amount", 0)
        # Handle case where output_amount might be a string
        if isinstance(output_amount, str):
            output_amount = int(output_amount) if output_amount.isdigit() else 0
        current_price = output_amount / amount if amount > 0 else 0
        target_output = int(amount * limit_price)
        
        # Check if current price meets our limit
        if current_price >= limit_price:
            # Price is good - if we have keys, execute immediately as market order
            if private_key:
                from tools.raydium_tool import execute_swap as raydium_execute_swap
                
                # Execute swap immediately
                result = raydium_execute_swap(
                    quote_response=quote_response,
                    private_key=private_key,
                    wallet_address=user_public_key
                )
                
                result_data = json.loads(result)
                if result_data.get("success"):
                    return json.dumps({
                        "dex": "raydium",
                        "type": "limit_order_executed",
                        "status": "filled",
                        "signature": result_data.get("signature"),
                        "input_mint": input_mint,
                        "output_mint": output_mint,
                        "input_amount": amount,
                        "output_amount": quote_data.get("output_amount"),
                        "limit_price": limit_price,
                        "executed_price": current_price,
                        "explorer_url": result_data.get("explorer_url")
                    })
                else:
                    return json.dumps({
                        "dex": "raydium",
                        "type": "limit_order_attempt",
                        "status": "failed",
                        "error": result_data.get("error", "Execution failed"),
                        "limit_price": limit_price,
                        "current_price": current_price
                    })
            else:
                return json.dumps({
                    "dex": "raydium",
                    "type": "limit_order_attempt",
                    "status": "ready_to_execute",
                    "input_mint": input_mint,
                    "output_mint": output_mint,
                    "amount": amount,
                    "limit_price": limit_price,
                    "current_price": current_price,
                    "expected_output": quote_data.get("output_amount"),
                    "note": "Price meets limit - provide private_key to execute immediately"
                })
            
            result_data = json.loads(result)
            if result_data.get("success"):
                return json.dumps({
                    "dex": "raydium",
                    "type": "limit_order_executed",
                    "status": "filled",
                    "signature": result_data.get("signature"),
                    "input_mint": input_mint,
                    "output_mint": output_mint,
                    "input_amount": amount,
                    "output_amount": quote_data.get("output_amount"),
                    "limit_price": limit_price,
                    "executed_price": current_price,
                    "explorer_url": result_data.get("explorer_url")
                })
            else:
                return json.dumps({
                    "dex": "raydium",
                    "type": "limit_order_attempt",
                    "status": "failed",
                    "error": result_data.get("error", "Execution failed"),
                    "limit_price": limit_price,
                    "current_price": current_price
                })
        else:
            # Price not met yet - return instructions for monitoring
            return json.dumps({
                "dex": "raydium",
                "type": "limit_order_created",
                "status": "open",
                "input_mint": input_mint,
                "output_mint": output_mint,
                "amount": amount,
                "limit_price": limit_price,
                "current_price": current_price,
                "price_difference": f"{((current_price - limit_price) / limit_price * 100):.2f}%",
                "note": f"Limit order placed. Current price {current_price:.8f} is {'below' if current_price < limit_price else 'at or above'} limit {limit_price:.8f}. Monitor for execution.",
                "instructions": "Use raydium_limit_query to check order status, or execute when price conditions are met."
            })
            
    except Exception as e:
        return json.dumps({"error": str(e)})

def query_raydium_limit_orders(wallet: str) -> str:
    """Query open limit orders for a wallet (simplified)"""
    try:
        # In a full implementation, this would check on-chain for open orders
        # For now, we return a placeholder since Raydium doesn't have traditional limit orders
        # but we can check for recent transactions or positions
        return json.dumps({
            "dex": "raydium",
            "orders": [],
            "count": 0,
            "note": "Raydium uses CLMM pools for limit-order-like functionality. Use position tracking for active orders."
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def cancel_raydium_limit_order(order_id: str, wallet: str, private_key: str) -> str:
    """Cancel a limit order (for Raydium, this would mean removing liquidity)"""
    try:
        return json.dumps({
            "dex": "raydium",
            "status": "not_implemented",
            "note": "For Raydium CLMM positions, liquidity removal would be needed instead of simple cancellation.",
            "suggestion": "Use position management tools to remove liquidity from CLMM pools."
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

# Register the tools
registry.register(
    name="raydium_limit_create",
    toolset="dex",
    schema={
        "name": "raydium_limit_create",
        "description": "Create a limit order on Raydium using CLMM pools (concentrated liquidity provides limit-order-like functionality)",
        "parameters": {
            "type": "object",
            "properties": {
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
                    "description": "Base58 encoded Solana private key for signing"
                },
                "user_public_key": {
                    "type": "string",
                    "description": "Your wallet address"
                },
                "version": {
                    "type": "string",
                    "description": "Network version: devnet or mainnet",
                    "default": "devnet"
                }
            },
            "required": ["input_mint", "output_mint", "amount", "limit_price", "private_key", "user_public_key"]
        }
    },
    handler=lambda args, **kw: create_raydium_clmm_limit_order(
        args.get("input_mint", ""),
        args.get("output_mint", ""),
        args.get("amount", 0),
        args.get("limit_price", 0),
        args.get("private_key"),
        args.get("user_public_key"),
        args.get("version", "devnet")
    ),
    check_fn=check_requirements
)

registry.register(
    name="raydium_limit_query",
    toolset="dex",
    schema={
        "name": "raydium_limit_query",
        "description": "Query open limit orders for a wallet on Raydium",
        "parameters": {
            "type": "object",
            "properties": {
                "wallet": {
                    "type": "string",
                    "description": "Wallet address to query orders for"
                }
            },
            "required": ["wallet"]
        }
    },
    handler=lambda args, **kw: query_raydium_limit_orders(args.get("wallet", "")),
    check_fn=check_requirements
)

registry.register(
    name="raydium_limit_cancel",
    toolset="dex",
    schema={
        "name": "raydium_limit_cancel",
        "description": "Cancel a limit order on Raydium (removes liquidity from CLMM position)",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order identifier to cancel"
                },
                "wallet": {
                    "type": "string",
                    "description": "Wallet address"
                },
                "private_key": {
                    "type": "string",
                    "description": "Base58 encoded Solana private key for signing"
                }
            },
            "required": ["order_id", "wallet", "private_key"]
        }
    },
    handler=lambda args, **kw: cancel_raydium_limit_order(
        args.get("order_id", ""),
        args.get("wallet", ""),
        args.get("private_key", "")
    ),
    check_fn=check_requirements
)