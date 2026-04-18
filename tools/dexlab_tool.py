import json
import requests
from tools.registry import registry

DEXLAB_API_URL = "https://api.dexlab.space/v1"


def check_requirements() -> bool:
    try:
        response = requests.get(f"{DEXLAB_API_URL}/tokens?limit=1", timeout=5)
        return response.status_code in (200, 429)
    except:
        return False


def get_token_data(token_address: str) -> str:
    """Get detailed token data from DexLab
    
    Args:
        token_address: Solana token mint address
    
    Returns:
        JSON with token metadata, price, liquidity
    """
    try:
        url = f"{DEXLAB_API_URL}/tokens/{token_address}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"error": str(e)})


def search_tokens(query: str, limit: int = 10) -> str:
    """Search for tokens on DexLab
    
    Args:
        query: Token symbol or name to search
        limit: Number of results
    
    Returns:
        JSON with token list
    """
    try:
        url = f"{DEXLAB_API_URL}/tokens"
        params = {"search": query, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return json.dumps({"tokens": data.get("data", []), "count": len(data.get("data", []))})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_market_pairs(base_token: str = None) -> str:
    """Get market pairs for a token
    
    Args:
        base_token: Optional token address to filter pairs
    
    Returns:
        JSON with trading pairs
    """
    try:
        url = f"{DEXLAB_API_URL}/pairs"
        params = {}
        if base_token:
            params["base_token"] = base_token
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return json.dumps({"pairs": data.get("data", [])})
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="dexlab_token_data",
    toolset="dex",
    schema={
        "name": "dexlab_token_data",
        "description": "Get detailed token data from DexLab API including metadata, price, and liquidity for Solana tokens",
        "parameters": {
            "type": "object",
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "Solana token mint address"
                }
            },
            "required": ["token_address"]
        }
    },
    handler=lambda args, **kw: get_token_data(args.get("token_address", "")),
    check_fn=check_requirements
)

registry.register(
    name="dexlab_search_tokens",
    toolset="dex",
    schema={
        "name": "dexlab_search_tokens",
        "description": "Search for tokens on DexLab by symbol or name",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Token symbol or name to search"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    },
    handler=lambda args, **kw: search_tokens(
        args.get("query", ""),
        args.get("limit", 10)
    ),
    check_fn=check_requirements
)

registry.register(
    name="dexlab_market_pairs",
    toolset="dex",
    schema={
        "name": "dexlab_market_pairs",
        "description": "Get trading market pairs from DexLab",
        "parameters": {
            "type": "object",
            "properties": {
                "base_token": {
                    "type": "string",
                    "description": "Optional token address to filter pairs"
                }
            }
        }
    },
    handler=lambda args, **kw: get_market_pairs(args.get("base_token")),
    check_fn=check_requirements
)