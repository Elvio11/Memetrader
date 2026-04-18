import json
import os
from typing import Dict, Any, Optional

from tools.registry import registry
from tools.crypto.chains import (
    get_chain,
    get_supported_chains,
    get_tokens_for_chain,
    CHAIN_CONFIGS,
    SUPPORTED_TOKENS,
)
from tools.crypto.price_oracle import (
    get_token_price,
    get_meme_token_price,
    get_trending_meme_tokens,
    get_token_market_data,
    search_tokens,
    get_prices_batch,
)


def check_requirements() -> bool:
    """Check if trading tools are available"""
    return True



def get_supported_chains_tool(task_id: str = None) -> str:
    """Get list of supported blockchain networks for trading.

    Returns all chains where trading is available.
    """
    chains = get_supported_chains()
    chain_info = []

    for name in chains:
        config = get_chain(name)
        if config:
            chain_info.append(
                {
                    "name": config.name,
                    "type": config.chain_type.value,
                    "symbol": config.coin_symbol,
                    "explorer": config.explorer_url,
                }
            )

    return json.dumps({"chains": chain_info}, indent=2)


def get_tokens_tool(chain: str, task_id: str = None) -> str:
    """Get supported tokens for a specific chain.

    Returns list of tradeable tokens with their addresses and decimals.
    """
    tokens = get_tokens_for_chain(chain)
    return json.dumps({"chain": chain, "tokens": tokens}, indent=2)


def get_token_price_tool(chain: str, token: str, task_id: str = None) -> str:
    """Get current price of a token in USD.

    Fetches real-time price from CoinGecko.
    """
    price = get_token_price(chain, token)
    if price is None:
        return json.dumps(
            {"success": False, "error": f"Could not get price for {token} on {chain}"}
        )

    return json.dumps({"chain": chain, "token": token, "price_usd": price}, indent=2)


def get_trending_tokens_tool(task_id: str = None) -> str:
    """Get trending meme tokens from CoinGecko.

    Returns top trending tokens that might be good for trading.
    """
    tokens = get_trending_meme_tokens()
    return json.dumps({"trending": tokens}, indent=2)


def search_token_tool(query: str, task_id: str = None) -> str:
    """Search for a token by name or symbol.

    Useful for finding token IDs before getting prices or market data.
    """
    results = search_tokens(query)
    return json.dumps({"query": query, "results": results}, indent=2)


def get_token_market_data_tool(token_id: str, task_id: str = None) -> str:
    """Get detailed market data for a token.

    Returns price, market cap, volume, ATH/ATL, and price changes.
    """
    data = get_token_market_data(token_id)
    if not data:
        return json.dumps(
            {"success": False, "error": f"Could not get data for {token_id}"}
        )

    return json.dumps(data, indent=2)


# =============================================================================
# Tool Registration
# =============================================================================

registry.register(
    name="get_supported_chains",
    toolset="trading",
    schema={
        "name": "get_supported_chains",
        "description": "Get list of supported blockchain networks for trading. Returns all chains where you can trade.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    handler=lambda args, **kw: get_supported_chains_tool(task_id=kw.get("task_id")),
    check_fn=check_requirements,
)

registry.register(
    name="get_tokens",
    toolset="trading",
    schema={
        "name": "get_tokens",
        "description": "Get supported tokens for a specific blockchain chain.",
        "parameters": {
            "type": "object",
            "properties": {
                "chain": {
                    "type": "string",
                    "description": "Blockchain network",
                    "enum": ["ethereum", "solana", "base", "arbitrum", "sui"],
                },
            },
            "required": ["chain"],
        },
    },
    handler=lambda args, **kw: get_tokens_tool(
        chain=args.get("chain"),
        task_id=kw.get("task_id"),
    ),
    check_fn=check_requirements,
)

registry.register(
    name="get_token_price",
    toolset="trading",
    schema={
        "name": "get_token_price",
        "description": "Get current USD price of a token from CoinGecko. Real-time price data.",
        "parameters": {
            "type": "object",
            "properties": {
                "chain": {"type": "string", "description": "Blockchain network"},
                "token": {
                    "type": "string",
                    "description": "Token symbol (ETH, PEPE, etc.)",
                },
            },
            "required": ["chain", "token"],
        },
    },
    handler=lambda args, **kw: get_token_price_tool(
        chain=args.get("chain"),
        token=args.get("token"),
        task_id=kw.get("task_id"),
    ),
    check_fn=check_requirements,
)

registry.register(
    name="get_trending_tokens",
    toolset="trading",
    schema={
        "name": "get_trending_tokens",
        "description": "Get trending meme tokens from CoinGecko. Discover new opportunities.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    handler=lambda args, **kw: get_trending_tokens_tool(task_id=kw.get("task_id")),
    check_fn=check_requirements,
)

registry.register(
    name="search_token",
    toolset="trading",
    schema={
        "name": "search_token",
        "description": "Search for a token by name or symbol on CoinGecko.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Token name or symbol to search",
                },
            },
            "required": ["query"],
        },
    },
    handler=lambda args, **kw: search_token_tool(
        query=args.get("query"),
        task_id=kw.get("task_id"),
    ),
    check_fn=check_requirements,
)

registry.register(
    name="get_token_market_data",
    toolset="trading",
    schema={
        "name": "get_token_market_data",
        "description": "Get detailed market data for a token including price, market cap, volume, ATH/ATL, and price changes.",
        "parameters": {
            "type": "object",
            "properties": {
                "token_id": {
                    "type": "string",
                    "description": "CoinGecko token ID (e.g., 'pepe', 'dogecoin')",
                },
            },
            "required": ["token_id"],
        },
    },
    handler=lambda args, **kw: get_token_market_data_tool(
        token_id=args.get("token_id"),
        task_id=kw.get("task_id"),
    ),
    check_fn=check_requirements,
)
