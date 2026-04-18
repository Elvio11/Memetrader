import json
import os
import requests
from tools.registry import registry
from web3 import Web3

AERODROME_API_URL = "https://api.aerodrome.fi/v1"
BASE_RPC = os.getenv("BASE_RPC_URL", "https://base-mainnet.public.blastapi.io")

AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
AERODROME_ROUTER_ABI = """[{"name":"swapExactTokensForTokens","type":"function","inputs":[{"name":"amountIn","type":"uint256"},{"name":"amountOutMin","type":"uint256"},{"name":"path","type":"address[]"},{"name":"to","type":"address"},{"name":"deadline","type":"uint256"}],"outputs":[{"name":"","type":"uint256"}]}]"""


def check_requirements() -> bool:
    """Check if Base network is accessible or Hermes home exists"""
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        if w3.is_connected():
            return True
    except:
        pass
    return os.path.isdir(os.path.expanduser("~/.hermes"))


def get_pairs(token_address: str = None) -> str:
    """Get trading pairs from Aerodrome via direct contract query
    
    Args:
        token_address: Optional token to filter pairs
    
    Returns:
        JSON with trading pairs
    """
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        
        # Aerodrome factory contract to get pools
        factory = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"
        
        # Get recent events for pool creation
        # For now, return known popular pairs
        popular_pairs = [
            {"token0": "0x940181a94A35A4569E4529A3CDfB74e38FD98631", "token1": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "symbol": "AERO/USDC", "stable": False},
            {"token0": "0x4200000000000000000000000000000000000006", "token1": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "symbol": "WETH/USDC", "stable": False},
            {"token0": "0x4200000000000000000000000000000000000006", "token1": "0x940181a94A35A4569E4529A3CDfB74e38FD98631", "symbol": "WETH/AERO", "stable": False},
            {"token0": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "token1": "0xd9aAEc86B65D86f6A7B5b0c42FFA531710b6CA", "symbol": "USDC/USD+", "stable": True},
        ]
        
        return json.dumps({"pairs": popular_pairs, "count": len(popular_pairs)})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_token_price(token_address: str) -> str:
    """Get token price from Aerodrome via contract
    
    Args:
        token_address: Base chain token address
    
    Returns:
        JSON with price data
    """
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        
        # Common token addresses
        tokens = {
            "0x940181a94A35A4569E4529A3CDfB74e38FD98631": {"symbol": "AERO", "name": "Aerodrome"},
            "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913": {"symbol": "USDC", "name": "USD Coin"},
            "0x4200000000000000000000000000000000000006": {"symbol": "WETH", "name": "Wrapped Ether"},
            "0xd9aAEc86B65D86f6A7B5b0c42FFA531710b6CA": {"symbol": "USD+", "name": "USD+"},
        }
        
        token_info = tokens.get(token_address.lower(), {"symbol": "UNKNOWN", "name": "Unknown"})
        
        # Get price from pair if available
        return json.dumps({
            "address": token_address,
            "symbol": token_info["symbol"],
            "name": token_info["name"],
            "note": "Direct price from contract reading not implemented - use quote for swap pricing"
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_swap_quote(token_in: str, token_out: str, amount: int, slippage: float = 0.5) -> str:
    """Get swap quote from Aerodrome via contract
    
    Args:
        token_in: Input token address
        token_out: Output token address
        amount: Amount in wei
        slippage: Slippage tolerance in percentage
    
    Returns:
        JSON with quote
    """
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        
        if not w3.is_connected():
            return json.dumps({"error": "Not connected to Base network"})
        
        token_in = w3.to_checksum_address(token_in)
        token_out = w3.to_checksum_address(token_out)
        
        # Check if we have reserves via getReserves on pair
        # For now, calculate using simple price estimation
        
        # Try to get quote from router contract
        router_contract = w3.eth.contract(
            address=w3.to_checksum_address(AERODROME_ROUTER),
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


def execute_swap(quote_response: str, private_key: str = None) -> str:
    """Execute a swap on Aerodrome DEX (Base chain)
    
    Args:
        quote_response: JSON string from aerodrome_quote
        private_key: Optional Ethereum private key for signing
    
    Returns:
        JSON with transaction hash or unsigned tx for wallet signing
    """
    try:
        quote_data = json.loads(quote_response)
        if "error" in quote_data:
            return json.dumps({"error": "Invalid quote response"})
        
        # Get the transaction data from quote response
        tx_to = quote_data.get("to") or "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
        tx_value = int(quote_data.get("value", 0))
        tx_data = quote_data.get("data", "0x")
        
        if not private_key:
            return json.dumps({
                "unsigned_tx": {
                    "to": tx_to,
                    "value": hex(tx_value),
                    "data": tx_data,
                    "chainId": 8453
                },
                "signing_instructions": "Import this into MetaMask or other EVM wallet to sign and broadcast",
                "explorer": "https://basescan.org"
            })
        
        from web3 import Web3
        w3 = Web3()
        
        if not w3.is_address(private_key) and len(private_key) in (64, 66):
            # It's a private key, not an address
            account = w3.eth.account.from_key(private_key)
        else:
            return json.dumps({"error": "Invalid private key format"})
        
        # Get nonce and gas info
        try:
            nonce = w3.eth.get_transaction_count(account.address)
            gas_price = w3.eth.gas_price
        except Exception:
            nonce = 0
            gas_price = 1000000000  # 1 gwei fallback
        
        tx_params = {
            "from": account.address,
            "to": tx_to,
            "value": tx_value,
            "data": tx_data,
            "chainId": 8453,
            "gas": 300000,
            "nonce": nonce,
            "maxFeePerGas": gas_price * 2,
            "maxPriorityFeePerGas": gas_price
        }
        
        signed = account.sign_transaction(tx_params)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        return json.dumps({
            "success": True,
            "tx_hash": tx_hash.hex(),
            "from": account.address,
            "explorer_url": f"https://basescan.org/tx/{tx_hash.hex()}"
        })
        
    except ImportError:
        return json.dumps({
            "error": "web3 not installed",
            "resolution": "Install: pip install web3",
            "alternative": "Use MetaMask or other EVM wallet to sign"
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_token_list(limit: int = 50) -> str:
    """Get list of tokens on Aerodrome
    
    Args:
        limit: Number of tokens to return
    """
    try:
        url = f"{AERODROME_API_URL}/tokens"
        params = {"limit": limit}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return json.dumps({"tokens": data, "count": len(data)})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_gas_price() -> str:
    """Get current Base gas price"""
    try:
        url = f"{AERODROME_API_URL}/gas"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="aerodrome_pairs",
    toolset="dex",
    schema={
        "name": "aerodrome_pairs",
        "description": "Get trading pairs from Aerodrome DEX on Base chain",
        "parameters": {
            "type": "object",
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "Optional token address to filter pairs"
                }
            }
        }
    },
    handler=lambda args, **kw: get_pairs(args.get("token_address")),
    check_fn=check_requirements
)

registry.register(
    name="aerodrome_price",
    toolset="dex",
    schema={
        "name": "aerodrome_price",
        "description": "Get token price from Aerodrome DEX on Base",
        "parameters": {
            "type": "object",
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "Base chain token address"
                }
            },
            "required": ["token_address"]
        }
    },
    handler=lambda args, **kw: get_token_price(args.get("token_address", "")),
    check_fn=check_requirements
)

registry.register(
    name="aerodrome_quote",
    toolset="dex",
    schema={
        "name": "aerodrome_quote",
        "description": "Get swap quote from Aerodrome DEX",
        "parameters": {
            "type": "object",
            "properties": {
                "token_in": {
                    "type": "string",
                    "description": "Input token address"
                },
                "token_out": {
                    "type": "string",
                    "description": "Output token address"
                },
                "amount": {
                    "type": "integer",
                    "description": "Amount in wei (smallest unit)"
                }
            },
            "required": ["token_in", "token_out", "amount"]
        }
    },
    handler=lambda args, **kw: get_swap_quote(
        args.get("token_in", ""),
        args.get("token_out", ""),
        args.get("amount", 0)
    ),
    check_fn=check_requirements
)

registry.register(
    name="aerodrome_tokens",
    toolset="dex",
    schema={
        "name": "aerodrome_tokens",
        "description": "Get list of tokens on Aerodrome DEX",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of tokens to return",
                    "default": 50
                }
            }
        }
    },
    handler=lambda args, **kw: get_token_list(args.get("limit", 50)),
    check_fn=check_requirements
)

registry.register(
    name="aerodrome_gas",
    toolset="dex",
    schema={
        "name": "aerodrome_gas",
        "description": "Get current Base network gas price",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: get_gas_price(),
    check_fn=check_requirements
)

registry.register(
    name="aerodrome_execute",
    toolset="dex",
    schema={
        "name": "aerodrome_execute",
        "description": "Execute a token swap on Aerodrome DEX on Base chain. First call aerodrome_quote to get a quote, then pass the quote_response and your private_key to execute.",
        "parameters": {
            "type": "object",
            "properties": {
                "quote_response": {
                    "type": "string",
                    "description": "Quote response JSON from aerodrome_quote"
                },
                "private_key": {
                    "type": "string",
                    "description": "Ethereum private key for signing the transaction"
                }
            },
            "required": ["quote_response"]
        }
    },
    handler=lambda args, **kw: execute_swap(
        args.get("quote_response", ""),
        args.get("private_key")
    ),
    check_fn=check_requirements
)