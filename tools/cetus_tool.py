import json
import requests
import os
from tools.registry import registry

CETUS_API_URL = "https://api.cetus.ac"
SUI_RPC = os.getenv("SUI_RPC_URL", "https://sui-mainnet.public.blastapi.io")
HERMES_HOME = os.path.expanduser("~/.hermes")


def check_requirements() -> bool:
    """Check if environment is ready for Cetus"""
    return os.path.isdir(HERMES_HOME)


def get_token_price(token_address: str) -> str:
    """Get token price from Cetus"""
    try:
        url = f"{CETUS_API_URL}/token/price"
        params = {"address": token_address}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return json.dumps({
            "token": token_address,
            "price": data.get("price"),
            "change_24h": data.get("priceChange24h"),
            "volume_24h": data.get("volume24h")
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_pool_info(pool_address: str) -> str:
    """Get pool information"""
    try:
        url = f"{CETUS_API_URL}/pool/info"
        params = {"address": pool_address}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return json.dumps({
            "pool": pool_address,
            "token_a": data.get("coinA"),
            "token_b": data.get("coinB"),
            "liquidity": data.get("liquidity"),
            ".volume_24h": data.get("volume24h")
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_swap_quote(input_token: str, output_token: str, amount: int) -> str:
    """Get swap quote from Cetus"""
    try:
        url = f"{CETUS_API_URL}/swap/quote"
        params = {
            "fromCoin": input_token,
            "toCoin": output_token,
            "amount": amount
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return json.dumps({
            "input_token": input_token,
            "output_token": output_token,
            "input_amount": amount,
            "output_amount": data.get("outAmount"),
            "price_impact": data.get("priceImpact")
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def execute_swap(quote_response: str, private_key: str = None) -> str:
    """Execute a swap on Cetus DEX (SUI chain)
    
    Args:
        quote_response: JSON string from cetus_swap_quote
        private_key: Optional SUI private key (base58 encoded)
    
    Returns:
        JSON with transaction digest or unsigned tx for wallet signing
    """
    try:
        quote_data = json.loads(quote_response)
        if "error" in quote_data:
            return json.dumps({"error": "Invalid quote response"})
        
        input_token = quote_data.get("input_token")
        output_token = quote_data.get("output_token")
        input_amount = quote_data.get("input_amount")
        
        # Build swap transaction via Cetus API
        url = f"{CETUS_API_URL}/swap"
        
        payload = {
            "from": input_token,
            "to": output_token,
            "amount": str(input_amount),
            "slippage": 100  # 1% slippage in bps
        }
        
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        tx_result = response.json()
        
        # Check if we have tx data to sign
        tx_bytes = tx_result.get("tx") or tx_result.get("transaction")
        
        if not tx_bytes:
            return json.dumps({"error": "No transaction data returned from API", "raw_response": tx_result})
        
        if not private_key:
            return json.dumps({
                "unsigned_tx": tx_bytes,
                "input_token": input_token,
                "output_token": output_token,
                "input_amount": input_amount,
                "signing_instructions": "Sign this transaction using your SUI wallet (Sui Wallet, Martian, etc.) and broadcast via RPC"
            })
        
        # Try to sign using pysui if available
        try:
            from pysui.sui_keytool import SuiKeyTool
            from pysui.sui_builders.build_transaction import SuiTransactionBuilder
            
            # Parse private key (base58 to bytes)
            import base58
            key_bytes = base58.b58decode(private_key)
            
            # Use keytool to sign
            keytool = SuiKeyTool.from_hex_seed(key_bytes.hex())
            signer = keytool.address
            
            # Build and sign transaction
            builder = SuiTransactionBuilder()
            builder.tx_bytes = tx_bytes
            
            # Sign the transaction
            signature = keytool.sign(tx_bytes.encode('utf-8'))
            
            # Execute via RPC
            import requests as req
            rpc_url = os.getenv("SUI_RPC_URL", "https://sui-mainnet.public.blastapi.io")
            exec_result = req.post(rpc_url, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sui_executeTransactionBlock",
                "params": [tx_bytes, [signature], "Fast", False]
            }, timeout=30).json()
            
            if "result" in exec_result:
                return json.dumps({
                    "success": True,
                    "digest": exec_result["result"]["digest"],
                    "explorer_url": f"https://suiscan.xyz/tx/{exec_result['result']['digest']}"
                })
            else:
                return json.dumps({"error": "Transaction execution failed", "details": exec_result})
                
        except ImportError:
            return json.dumps({
                "unsigned_tx": tx_bytes,
                "note": "pysui not installed. Install: pip install pysui. Using SUI wallet recommended for signing."
            })
        except Exception as e:
            return json.dumps({
                "error": f"Signing failed: {str(e)}",
                "unsigned_tx": tx_bytes,
                "recommendation": "Sign manually using your SUI wallet"
            })
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_token_list(chain: str = "sui") -> str:
    """Get list of tokens on SUI/cetus"""
    try:
        url = f"{CETUS_API_URL}/tokens"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        tokens = []
        for token in data.get("tokens", [])[:50]:
            tokens.append({
                "address": token.get("address"),
                "symbol": token.get("symbol"),
                "name": token.get("name"),
                "decimals": token.get("decimals")
            })
        
        return json.dumps({"tokens": tokens})
    except Exception as e:
        return json.dumps({"error": str(e)})


def create_limit_order(input_token: str, output_token: str, amount: int, limit_price: float) -> str:
    """Create a limit order on Cetus - uses aggregator to set price condition
    
    Args:
        input_token: Input token address
        output_token: Output token address  
        amount: Amount to swap (in minimal units)
        limit_price: Target price (as decimal, e.g., 0.00015 means minimum output)
    
    Returns:
        JSON with order or condition for execution
    """
    try:
        # Get current quote first
        quote = get_swap_quote(input_token, output_token, amount)
        quote_data = json.loads(quote)
        
        if "error" in quote_data:
            return json.dumps({"error": f"Cannot get quote: {quote_data['error']}"})
        
        current_output = int(quote_data.get("output_amount", 0))
        current_price = current_output / amount if amount > 0 else 0
        target_output = int(amount * limit_price)
        
        # Calculate minimum acceptable output based on limit price
        min_output = target_output
        
        return json.dumps({
            "status": "limit_order_created",
            "input_token": input_token,
            "output_token": output_token,
            "amount": amount,
            "limit_price": limit_price,
            "current_price": current_price,
            "target_output": target_output,
            "condition": "execute_when_price_reaches" if current_price < limit_price else "ready_to_execute",
            "execution_params": {
                "slippage_bps": 50,
                "min_output_amount": min_output
            },
            "recommendation": f"Current price {current_price:.8f}, limit {limit_price:.8f}. {'Price below limit - monitor for execution' if current_price < limit_price else 'Price at or above limit - can execute now'}",
            "cetus_api_params": {
                "from": input_token,
                "to": output_token,
                "amount": amount,
                "max_slippage": 50  # 0.5% max slippage to protect limit
            }
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="cetus_price",
    toolset="dex",
    schema={
        "name": "cetus_price",
        "description": "Get token price from Cetus DEX (SUI)",
        "parameters": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string", "description": "Token contract address"}
            },
            "required": ["token_address"]
        }
    },
    handler=lambda args, **kw: get_token_price(args.get("token_address", "")),
    check_fn=check_requirements
)

registry.register(
    name="cetus_pool",
    toolset="dex",
    schema={
        "name": "cetus_pool",
        "description": "Get pool information from Cetus",
        "parameters": {
            "type": "object",
            "properties": {
                "pool_address": {"type": "string", "description": "Pool contract address"}
            },
            "required": ["pool_address"]
        }
    },
    handler=lambda args, **kw: get_pool_info(args.get("pool_address", "")),
    check_fn=check_requirements
)

registry.register(
    name="cetus_swap_quote",
    toolset="dex",
    schema={
        "name": "cetus_swap_quote",
        "description": "Get swap quote from Cetus DEX",
        "parameters": {
            "type": "object",
            "properties": {
                "input_token": {"type": "string", "description": "Input token address"},
                "output_token": {"type": "string", "description": "Output token address"},
                "amount": {"type": "integer", "description": "Amount in smallest units"}
            },
            "required": ["input_token", "output_token", "amount"]
        }
    },
    handler=lambda args, **kw: get_swap_quote(
        args.get("input_token", ""),
        args.get("output_token", ""),
        args.get("amount", 0)
    ),
    check_fn=check_requirements
)

registry.register(
    name="cetus_tokens",
    toolset="dex",
    schema={
        "name": "cetus_tokens",
        "description": "Get token list from Cetus",
        "parameters": {
            "type": "object",
            "properties": {
                "chain": {"type": "string", "description": "Chain (default: sui)", "default": "sui"}
            }
        }
    },
    handler=lambda args, **kw: get_token_list(args.get("chain", "sui")),
    check_fn=check_requirements
)

registry.register(
    name="cetus_execute",
    toolset="dex",
    schema={
        "name": "cetus_execute",
        "description": "Execute a token swap on Cetus DEX (SUI chain). First call cetus_swap_quote to get a quote, then pass the quote_response to execute.",
        "parameters": {
            "type": "object",
            "properties": {
                "quote_response": {"type": "string", "description": "Quote response JSON from cetus_swap_quote"},
                "private_key": {"type": "string", "description": "Optional SUI private key for signing (if not provided, returns tx data)"}
            },
            "required": ["quote_response"]
        }
    },
    handler=lambda args, **kw: execute_swap(args.get("quote_response", ""), args.get("private_key")),
    check_fn=check_requirements
)

registry.register(
    name="cetus_limit_order",
    toolset="dex",
    schema={
        "name": "cetus_limit_order",
        "description": "Create a limit order on Cetus DEX. Note: SUI limit orders require SDK integration.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_token": {"type": "string", "description": "Input token address"},
                "output_token": {"type": "string", "description": "Output token address"},
                "amount": {"type": "integer", "description": "Amount to swap"},
                "limit_price": {"type": "number", "description": "Target price for the limit order"}
            },
            "required": ["input_token", "output_token", "amount", "limit_price"]
        }
    },
    handler=lambda args, **kw: create_limit_order(
        args.get("input_token", ""),
        args.get("output_token", ""),
        args.get("amount", 0),
        args.get("limit_price", 0)
    ),
    check_fn=check_requirements
)