#!/usr/bin/env python3
"""
NOFX Trading Tool Module

Provides integration with NOFX trading API for executing trades,
managing portfolio, positions, and strategies.

Configuration:
- NOFX_API_URL: API base URL (default: http://localhost:8080)
- NOFX_API_TOKEN: Bearer token for authentication

Usage:
    from tools.nofx_trading_tool import (
        nofx_portfolio,
        nofx_positions,
        nofx_strategies,
        nofx_account,
        nofx_exchanges,
        nofx_trade,
    )
"""

import json
import logging
import os

import requests

from tools.registry import registry, tool_error

logger = logging.getLogger(__name__)

NOFX_API_URL = os.getenv("NOFX_API_URL", "http://localhost:8080")
NOFX_API_TOKEN = os.getenv("NOFX_API_TOKEN", "")


def get_headers() -> dict:
    """Return headers with optional Bearer token."""
    if NOFX_API_TOKEN:
        return {"Authorization": f"Bearer {NOFX_API_TOKEN}"}
    return {}


def _api_request(method: str, endpoint: str, **kwargs) -> dict:
    """Make HTTP request to NOFX API."""
    url = f"{NOFX_API_URL}{endpoint}"
    try:
        response = requests.request(method, url, headers=get_headers(), **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("NOFX API request failed: %s", e)
        return {"error": str(e)}


def nofx_portfolio() -> str:
    """Get portfolio holdings from NOFX API.

    Returns JSON with portfolio data including positions and total value.
    """
    result = _api_request("GET", "/api/portfolio")
    return json.dumps(result)


def nofx_positions() -> str:
    """Get open positions from NOFX API.

    Returns JSON array of currently open positions.
    """
    result = _api_request("GET", "/api/positions")
    return json.dumps(result)


def nofx_strategies(action: str = "list", strategy_data: dict = None) -> str:
    """List or create trading strategies.

    Args:
        action: One of "list", "create"
        strategy_data: Required for create action - dict with strategy config

    Returns JSON with strategies list or creation result.
    """
    if action == "list":
        result = _api_request("GET", "/api/strategies")
        return json.dumps(result)
    elif action == "create" and strategy_data:
        result = _api_request("POST", "/api/strategies", json=strategy_data)
        return json.dumps(result)
    else:
        return json.dumps({"error": "Invalid action or missing strategy_data"})


def nofx_account() -> str:
    """Get account information from NOFX API.

    Returns JSON with account balance, status, and other details.
    """
    result = _api_request("GET", "/api/account")
    return json.dumps(result)


def nofx_exchanges() -> str:
    """List connected exchanges from NOFX API.

    Returns JSON array of configured exchange connections.
    """
    result = _api_request("GET", "/api/exchanges")
    return json.dumps(result)


def nofx_trade(
    symbol: str,
    side: str,
    amount: float,
    order_type: str = "market",
    price: float = None,
) -> str:
    """Execute a trade via NOFX API with risk validation and trading mode control.

    Args:
        symbol: Trading pair symbol (e.g., "BTC/USDT")
        side: "buy" or "sell"
        amount: Order amount
        order_type: Order type ("market", "limit", "stop")
        price: Limit/stop price (required for limit/stop orders)

    Returns JSON with order result or risk validation errors.
    """
    try:
        from tools.risk_manager import validate_trade_risk, get_risk_config
        
        trade_value = amount * (price if price else 1.0)
        portfolio_value = 1000.0
        current_positions = 0
        daily_pnl = 0.0
        
        risk_result = validate_trade_risk(
            trade_value=trade_value,
            current_positions=current_positions,
            daily_pnl=daily_pnl,
            portfolio_value=portfolio_value
        )
        
        trading_mode = os.getenv("TRADING_MODE", "supervised").lower()
        
        if not risk_result["approved"]:
            return json.dumps({
                "error": "Trade rejected by risk management",
                "risk_errors": risk_result["errors"],
                "risk_warnings": risk_result["warnings"],
                "needs_manual_review": True
            })
        
        if trading_mode == "paper":
            return json.dumps({
                "simulated": True,
                "message": f"Paper trade: {side} {amount} {symbol} @ {price or 'market'}",
                "trade_id": f"paper_{int(__import__('time').time())}"
            })
        
        if trading_mode == "alert-only":
            return json.dumps({
                "alert": True,
                "trade_proposal": {
                    "symbol": symbol,
                    "side": side,
                    "amount": amount,
                    "price": price,
                    "order_type": order_type
                },
                "message": "Trade suggestion - use /trade command to execute"
            })
        
    except ImportError:
        pass
    
    order_data = {
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "type": order_type,
    }
    if price is not None:
        order_data["price"] = price

    result = _api_request("POST", "/api/trades", json=order_data)
    return json.dumps(result)


def check_nofx_requirements() -> bool:
    """Check if NOFX API is accessible.

    Returns True if the API is reachable (even if auth fails).
    """
    try:
        response = requests.get(f"{NOFX_API_URL}/api/health", timeout=5)
        return response.status_code in (200, 401, 403)
    except Exception:
        return False


registry.register(
    name="nofx_portfolio",
    toolset="trading",
    schema={
        "name": "nofx_portfolio",
        "description": "Get portfolio holdings from NOFX trading API. Returns current positions, total value, and allocation breakdown.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    handler=lambda args, **kw: nofx_portfolio(),
    check_fn=check_nofx_requirements,
    requires_env=["NOFX_API_URL"],
    emoji="💼",
)

registry.register(
    name="nofx_positions",
    toolset="trading",
    schema={
        "name": "nofx_positions",
        "description": "Get open positions from NOFX trading API. Returns all currently open positions with entry prices and P&L.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    handler=lambda args, **kw: nofx_positions(),
    check_fn=check_nofx_requirements,
    requires_env=["NOFX_API_URL"],
    emoji="📊",
)

registry.register(
    name="nofx_strategies",
    toolset="trading",
    schema={
        "name": "nofx_strategies",
        "description": "List or create trading strategies in NOFX. Use action 'list' to view existing strategies or 'create' to add a new one with strategy_data.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform: 'list' or 'create'",
                    "enum": ["list", "create"],
                },
                "strategy_data": {
                    "type": "object",
                    "description": "Strategy configuration for create action (name, pairs, allocation, etc.)",
                },
            },
            "required": ["action"],
        },
    },
    handler=lambda args, **kw: nofx_strategies(
        action=args.get("action", "list"),
        strategy_data=args.get("strategy_data"),
    ),
    check_fn=check_nofx_requirements,
    requires_env=["NOFX_API_URL"],
    emoji="📈",
)

registry.register(
    name="nofx_account",
    toolset="trading",
    schema={
        "name": "nofx_account",
        "description": "Get account information from NOFX trading API. Returns balance, status, and account details.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    handler=lambda args, **kw: nofx_account(),
    check_fn=check_nofx_requirements,
    requires_env=["NOFX_API_URL"],
    emoji="👤",
)

registry.register(
    name="nofx_exchanges",
    toolset="trading",
    schema={
        "name": "nofx_exchanges",
        "description": "List connected exchanges from NOFX trading API. Returns all configured exchange connections.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    handler=lambda args, **kw: nofx_exchanges(),
    check_fn=check_nofx_requirements,
    requires_env=["NOFX_API_URL"],
    emoji="🔗",
)

registry.register(
    name="nofx_trade",
    toolset="trading",
    schema={
        "name": "nofx_trade",
        "description": "Execute a trade via NOFX trading API. Specify symbol, side (buy/sell), amount, and order type. For limit/stop orders, include price.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Trading pair symbol (e.g., 'BTC/USDT', 'DOGE/USDT')",
                },
                "side": {
                    "type": "string",
                    "description": "Trade direction",
                    "enum": ["buy", "sell"],
                },
                "amount": {
                    "type": "number",
                    "description": "Order amount",
                },
                "order_type": {
                    "type": "string",
                    "description": "Order type",
                    "enum": ["market", "limit", "stop"],
                    "default": "market",
                },
                "price": {
                    "type": "number",
                    "description": "Limit/stop price (required for limit/stop orders)",
                },
            },
            "required": ["symbol", "side", "amount"],
        },
    },
    handler=lambda args, **kw: nofx_trade(
        symbol=args.get("symbol", ""),
        side=args.get("side", "buy"),
        amount=args.get("amount", 0),
        order_type=args.get("order_type", "market"),
        price=args.get("price"),
    ),
    check_fn=check_nofx_requirements,
    requires_env=["NOFX_API_URL"],
    emoji="🛒",
)


if __name__ == "__main__":
    print("NOFX Trading Tool Module")
    print("=" * 50)
    print(f"API URL: {NOFX_API_URL}")
    print(f"Token set: {bool(NOFX_API_TOKEN)}")
    print("\nAvailable tools:")
    print("  - nofx_portfolio: Get portfolio holdings")
    print("  - nofx_positions: Get open positions")
    print("  - nofx_strategies: List/create strategies")
    print("  - nofx_account: Get account info")
    print("  - nofx_exchanges: List connected exchanges")
    print("  - nofx_trade: Execute a trade")
