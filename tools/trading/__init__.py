import json
import os
from typing import Dict, Any, Optional

from tools.registry import registry
from tools.trading.paper_engine import (
    get_paper_engine,
    reset_paper_trading,
    PaperTradingEngine,
)
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
    return True  # Paper trading doesn't require API keys


def paper_get_balance(chain: str, token: str = None, task_id: str = None) -> str:
    """Get paper wallet balance for a specific chain and token.

    Returns the current balance of your paper trading wallet.
    """
    engine = get_paper_engine()
    balance = engine.get_balance(chain, token)
    return json.dumps(balance, indent=2)


def paper_get_portfolio(task_id: str = None) -> str:
    """Get your complete paper trading portfolio.

    Shows all wallets, balances, positions, and P&L.
    """
    engine = get_paper_engine()

    # Get prices for valuation
    tokens = []
    for chain, wallet in engine.portfolio.wallets.items():
        for token in wallet.current_balance.keys():
            tokens.append({"chain": chain, "token": token})

    prices = get_prices_batch(tokens)
    engine.get_portfolio_value(prices)

    stats = engine.get_stats()
    portfolio = engine.portfolio.to_dict()

    return json.dumps(
        {
            "stats": stats,
            "wallets": portfolio["wallets"],
            "positions": portfolio["positions"],
            "recent_trades": portfolio["trades"][-10:] if portfolio["trades"] else [],
        },
        indent=2,
    )


def paper_get_stats(task_id: str = None) -> str:
    """Get paper trading statistics and performance metrics.

    Returns total trades, win rate, P&L, and returns.
    """
    engine = get_paper_engine()

    tokens = []
    for chain, wallet in engine.portfolio.wallets.items():
        for token in wallet.current_balance.keys():
            tokens.append({"chain": chain, "token": token})

    prices = get_prices_batch(tokens)
    engine.get_portfolio_value(prices)

    stats = engine.get_stats()
    return json.dumps(stats, indent=2)


def paper_execute_swap(
    chain: str,
    from_token: str,
    to_token: str,
    amount: float,
    task_id: str = None,
) -> str:
    """Execute a paper money swap on a DEX.

    Simulates a token swap without using real funds. Gets current price from oracle
    and executes at market rate.
    """
    engine = get_paper_engine()

    # Get price
    price = get_token_price(chain, from_token)
    if not price:
        return json.dumps(
            {"success": False, "error": f"Could not get price for {from_token}"}
        )

    # Calculate output (simplified - no slippage calculation in paper mode)
    amount_out = amount * price

    # For meme tokens, also get target token price
    to_price = get_token_price(chain, to_token)
    if to_price and to_price > 0:
        amount_out = (amount * price) / to_price

    # Execute paper trade
    result = engine.execute_trade(
        chain=chain,
        pair=f"{from_token}/{to_token}",
        side="buy",
        amount_in=amount,
        token_in=from_token,
        amount_out=amount_out,
        token_out=to_token,
        price=price,
        price_usd=price * amount,
        fee=0.001 * amount,  # Simulated 0.1% fee
        fee_usd=0.001 * amount * price,
    )

    return json.dumps(result, indent=2)


def paper_reset(task_id: str = None) -> str:
    """Reset paper trading - clears all positions and resets balances to initial capital.

    WARNING: This will delete all trading history and reset your paper portfolio.
    """
    result = reset_paper_trading()
    return json.dumps(result, indent=2)


def paper_get_trade_history(limit: int = 20, task_id: str = None) -> str:
    """Get paper trading history.

    Returns recent trades with details on prices, amounts, and P&L.
    """
    engine = get_paper_engine()
    trades = engine.get_trade_history(limit=limit)
    return json.dumps({"trades": trades}, indent=2)


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
    name="paper_get_balance",
    toolset="trading",
    schema={
        "name": "paper_get_balance",
        "description": "Get paper wallet balance for a specific chain and token. Use this to check your current paper trading balance.",
        "parameters": {
            "type": "object",
            "properties": {
                "chain": {
                    "type": "string",
                    "description": "Blockchain network (ethereum, solana, base, arbitrum)",
                    "enum": ["ethereum", "solana", "base", "arbitrum"],
                },
                "token": {
                    "type": "string",
                    "description": "Token symbol (ETH, USDC, SOL, etc.)",
                },
            },
            "required": ["chain"],
        },
    },
    handler=lambda args, **kw: paper_get_balance(
        chain=args.get("chain"),
        token=args.get("token"),
        task_id=kw.get("task_id"),
    ),
    check_fn=check_requirements,
)

registry.register(
    name="paper_get_portfolio",
    toolset="trading",
    schema={
        "name": "paper_get_portfolio",
        "description": "Get your complete paper trading portfolio. Shows all wallets, balances, positions, and P&L summary.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    handler=lambda args, **kw: paper_get_portfolio(task_id=kw.get("task_id")),
    check_fn=check_requirements,
)

registry.register(
    name="paper_get_stats",
    toolset="trading",
    schema={
        "name": "paper_get_stats",
        "description": "Get paper trading statistics including total trades, win rate, P&L, and returns.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    handler=lambda args, **kw: paper_get_stats(task_id=kw.get("task_id")),
    check_fn=check_requirements,
)

registry.register(
    name="paper_execute_swap",
    toolset="trading",
    schema={
        "name": "paper_execute_swap",
        "description": "Execute a paper money swap - simulate a token trade without real funds. Gets current market price and executes at that rate.",
        "parameters": {
            "type": "object",
            "properties": {
                "chain": {
                    "type": "string",
                    "description": "Blockchain network",
                    "enum": ["ethereum", "solana", "base", "arbitrum"],
                },
                "from_token": {"type": "string", "description": "Token to sell"},
                "to_token": {"type": "string", "description": "Token to buy"},
                "amount": {
                    "type": "number",
                    "description": "Amount of from_token to swap",
                },
            },
            "required": ["chain", "from_token", "to_token", "amount"],
        },
    },
    handler=lambda args, **kw: paper_execute_swap(
        chain=args.get("chain"),
        from_token=args.get("from_token"),
        to_token=args.get("to_token"),
        amount=args.get("amount"),
        task_id=kw.get("task_id"),
    ),
    check_fn=check_requirements,
)

registry.register(
    name="paper_reset",
    toolset="trading",
    schema={
        "name": "paper_reset",
        "description": "Reset paper trading - clears all positions and resets balances to initial capital ($10,000). Use when you want to start fresh.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    handler=lambda args, **kw: paper_reset(task_id=kw.get("task_id")),
    check_fn=check_requirements,
)

registry.register(
    name="paper_get_trade_history",
    toolset="trading",
    schema={
        "name": "paper_get_trade_history",
        "description": "Get your paper trading history - shows recent trades with prices and amounts.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of recent trades to return",
                    "default": 20,
                },
            },
        },
    },
    handler=lambda args, **kw: paper_get_trade_history(
        limit=args.get("limit", 20),
        task_id=kw.get("task_id"),
    ),
    check_fn=check_requirements,
)

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
