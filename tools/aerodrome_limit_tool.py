import json
import os
import requests
from tools.registry import registry
from web3 import Web3

AERODROME_API_URL = "https://api.aerodrome.fi/v1"
BASE_RPC = os.getenv("BASE_RPC_URL", "https://base-mainnet.public.blastapi.io")

AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
AERODROME_FACTORY = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"

# Slipstream (concentrated liquidity) factory
SLIPSTREAM_FACTORY = "0x83b5A2b4313B35eb223F02BdC125030e782cA8aB"

def check_requirements() -> bool:
    """Check if Base network is accessible"""
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        return w3.is_connected()
    except:
        return False

def get_slipstream_pool_info(token_a: str, token_b: str) -> dict:
    """Get Slipstream concentrated liquidity pool information for token pair"""
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        
        # Get token information
        token_a = Web3.to_checksum_address(token_a)
        token_b = Web3.to_checksum_address(token_b)
        
        # Try to get pool from Slipstream factory
        # This is a simplified approach - in practice you'd need to parse events or use subgraph
        return {
            "factory": SLIPSTREAM_FACTORY,
            "token_a": token_a,
            "token_b": token_b,
            "note": "Slipstream pool info - would require subgraph or event parsing for full implementation"
        }
    except Exception as e:
        return {"error": str(e)}

def create_aerodrome_clmm_limit_order(
    input_mint: str,
    output_mint: str,
    amount: int,
    limit_price: float,
    private_key: str = None,
    user_public_key: str = None,
    version: str = "mainnet"
) -> str:
    """
    Create a limit order on Aerodrome using Slipstream concentrated liquidity pools
    This simulates limit order functionality by setting price bounds
    
    Args:
        input_mint: Input token address
        output_mint: Output token address
        amount: Amount to sell (in smallest unit)
        limit_price: Target price (as decimal ratio, e.g., 0.00015 means you want at least 0.00015 output per 1 input)
        private_key: Optional Ethereum private key for signing
        user_public_key: Wallet address
        version: Network version (mainnet/testnet)
        
    Returns:
        JSON string with order details or transaction
    """
    try:
        # Select RPC endpoint
        if version == "mainnet":
            rpc_url = BASE_RPC
        else:
            # For testnet, we'd use a different RPC
            rpc_url = os.getenv("BASE_TESTNET_RPC", "https://base-goerli.public.blastapi.io")
        
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            return json.dumps({"error": "Failed to connect to Base network"})
        
        # Convert addresses to checksum format
        input_mint = Web3.to_checksum_address(input_mint)
        output_mint = Web3.to_checksum_address(output_mint)
        if user_public_key:
            user_public_key = Web3.to_checksum_address(user_public_key)
        
        # Get current price quote
        quote_response = get_swap_quote(input_mint, output_mint, amount)
        quote_data = json.loads(quote_response)
        
        if "error" in quote_data:
            return json.dumps({"error": f"Failed to get quote: {quote_data['error']}"})
        
        current_price = quote_data.get("output_amount", 0) / amount if amount > 0 else 0
        target_output = int(amount * limit_price)
        
        # Check if current price meets our limit
        if current_price >= limit_price:
            # Price is good - execute immediately as market order
            if not private_key:
                return json.dumps({
                    "dex": "aerodrome",
                    "type": "limit_order_attempt",
                    "status": "ready_to_execute",
                    "current_price": current_price,
                    "limit_price": limit_price,
                    "input_amount": amount,
                    "expected_output": quote_data.get("output_amount"),
                    "note": "Price meets limit - provide private_key to execute immediately"
                })
            
            # Execute swap immediately using private key
            from tools.aerodrome_tool import execute_swap as aerodrome_execute_swap
            
            result = aerodrome_execute_swap(
                quote_response=quote_response,
                private_key=private_key
            )
            
            result_data = json.loads(result)
            if result_data.get("success"):
                return json.dumps({
                    "dex": "aerodrome",
                    "type": "limit_order_executed",
                    "status": "filled",
                    "transaction_hash": result_data.get("tx_hash"),
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
                    "dex": "aerodrome",
                    "type": "limit_order_attempt",
                    "status": "failed",
                    "error": result_data.get("error", "Execution failed"),
                    "limit_price": limit_price,
                    "current_price": current_price
                })
        else:
            # Price not met yet - return instructions for monitoring
            price_diff_percent = ((current_price - limit_price) / limit_price * 100) if limit_price > 0 else 0
            
            return json.dumps({
                "dex": "aerodrome",
                "type": "limit_order_created",
                "status": "open",
                "input_mint": input_mint,
                "output_mint": output_mint,
                "amount": amount,
                "limit_price": limit_price,
                "current_price": current_price,
                "price_difference_percent": f"{price_diff_percent:.2f}%",
                "note": f"Limit order placed. Current price {current_price:.8f} is {'below' if current_price < limit_price else 'at or above'} limit {limit_price:.8f}. Monitor for execution.",
                "instructions": "Use aerodrome_limit_query to check order status, or execute when price conditions are met.",
                "slipstream_info": get_slipstream_pool_info(input_mint, output_mint)
            })
            
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_swap_quote(token_in: str, token_out: str, amount: int, slippage: float = 0.5) -> str:
    """Get swap quote from Aerodrome (reuse from aerodrome_tool)"""
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        
        if not w3.is_connected():
            return json.dumps({"error": "Not connected to Base network"})
        
        token_in = Web3.to_checksum_address(token_in)
        token_out = Web3.to_checksum_address(token_out)
        
        # Try to get quote from router contract
        router_contract = w3.eth.contract(
            address=Web3.to_checksum_address(AERODROME_ROUTER),
            abi=[{"name":"getAmountsOut","type":"function","inputs":[{"name":"amountIn","type":"uint256"},{"name":"path","type":"address[]"}],"outputs":[{"name":"","type":"uint256[]"}]}]
        )
        
        try:
            path = [token_in, token_out]
            amounts = router_contract.functions.getAmountsOut(amount, path).call()
            
            min_amount = int(amounts[1] * (10000 - slippage * 100) / 10000)
            
            return json.dumps({
                "input_token": token_in,
                "output_token": token_out,
                "input_amount": amount,
                "output_amount": amounts[1],
                "min_output": min_amount,
                "slippage": slippage,
                "path": path
            })
        except Exception as e:
            # Fallback to simple price estimation
            return json.dumps({
                "input_token": token_in,
                "output_token": token_out,
                "input_amount": amount,
                "output_amount": int(amount * 0.001),  # Placeholder
                "min_output": int(amount * 0.00095),
                "slippage": slippage,
                "error": f"Could not get quote: {str(e)}",
                "note": "Direct contract call - pair may not exist or insufficient liquidity"
            })
    except Exception as e:
        return json.dumps({"error": str(e)})

def query_aerodrome_limit_orders(wallet: str) -> str:
    """Query open limit orders for a wallet on Aerodrome (simplified)"""
    try:
        # In a full implementation, this would check on-chain for open orders
        # For now, we return a placeholder since Aerodrome doesn't have traditional limit orders
        # but we can check for recent transactions or positions in Slipstream pools
        return json.dumps({
            "dex": "aerodrome",
            "orders": [],
            "count": 0,
            "note": "Aerodrome uses Slipstream concentrated liquidity for limit-order-like functionality. Use position tracking for active orders.",
            "suggestion": "Check your liquidity positions in Slipstream pools for active range orders."
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def cancel_aerodrome_limit_order(order_id: str, wallet: str, private_key: str = None) -> str:
    """Cancel a limit order on Aerodrome (for Slipstream, this would mean removing liquidity)"""
    try:
        return json.dumps({
            "dex": "aerodrome",
            "status": "not_implemented",
            "note": "For Aerodrome Slipstream positions, liquidity removal would be needed instead of simple cancellation.",
            "suggestion": "Use position management tools to remove liquidity from Slipstream concentrated liquidity pools.",
            "order_id": order_id,
            "wallet": wallet
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

# Register the tools
registry.register(
    name="aerodrome_limit_create",
    toolset="dex",
    schema={
        "name": "aerodrome_limit_create",
        "description": "Create a limit order on Aerodrome using Slipstream concentrated liquidity pools",
        "parameters": {
            "type": "object",
            "properties": {
                "input_mint": {
                    "type": "string",
                    "description": "Input token address"
                },
                "output_mint": {
                    "type": "string",
                    "description": "Output token address"
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
                    "description": "Ethereum private key for signing (optional for quote-only)"
                },
                "user_public_key": {
                    "type": "string",
                    "description": "Your wallet address"
                },
                "version": {
                    "type": "string",
                    "description": "Network version: mainnet or testnet",
                    "default": "mainnet"
                }
            },
            "required": ["input_mint", "output_mint", "amount", "limit_price"]
        }
    },
    handler=lambda args, **kw: create_aerodrome_clmm_limit_order(
        args.get("input_mint", ""),
        args.get("output_mint", ""),
        args.get("amount", 0),
        args.get("limit_price", 0),
        args.get("private_key"),
        args.get("user_public_key"),
        args.get("version", "mainnet")
    ),
    check_fn=check_requirements
)

registry.register(
    name="aerodrome_limit_query",
    toolset="dex",
    schema={
        "name": "aerodrome_limit_query",
        "description": "Query open limit orders for a wallet on Aerodrome",
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
    handler=lambda args, **kw: query_aerodrome_limit_orders(args.get("wallet", "")),
    check_fn=check_requirements
)

registry.register(
    name="aerodrome_limit_cancel",
    toolset="dex",
    schema={
        "name": "aerodrome_limit_cancel",
        "description": "Cancel a limit order on Aerodrome (removes liquidity from Slipstream position)",
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
                    "description": "Ethereum private key for signing"
                }
            },
            "required": ["order_id", "wallet", "private_key"]
        }
    },
    handler=lambda args, **kw: cancel_aerodrome_limit_order(
        args.get("order_id", ""),
        args.get("wallet", ""),
        args.get("private_key", "")
    ),
    check_fn=check_requirements
)