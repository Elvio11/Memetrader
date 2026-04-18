import json
import os
import requests
from tools.registry import registry

BITQUERY_API_URL = "https://graphql.bitquery.io"


def check_requirements() -> bool:
    return True


def execute_graphql(query: str, variables: dict = None) -> str:
    """Execute GraphQL query against Bitquery API"""
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(BITQUERY_API_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_token_trades(token_address: str, limit: int = 20) -> str:
    """Get recent trades for a token from DEXes
    
    Args:
        token_address: Token mint address
        limit: Max trades to return
    """
    query = """
    query ($token: String!, $limit: Int) {
      ethereum(network: solana) {
       dexTrades(
          options: {limit: $limit},
          exchangeName: {isNull: false},
          baseCurrency: {is: $token}
        ) {
          block {
            timestamp {
              time
            }
            height
          }
          transaction {
            hash
          }
          exchange {
            name
          }
          baseCurrency {
            symbol
          }
          quoteCurrency {
            symbol
          }
          tradeAmount(in: USD)
          side
        }
      }
    }
    """
    return execute_graphql(query, {"token": token_address, "limit": limit})


def get_token_liquidity(token_address: str) -> str:
    """Get token liquidity across DEXes
    
    Args:
        token_address: Token mint address
    """
    query = """
    query ($token: String!) {
      ethereum(network: solana) {
       dexTrades(
          options: {limit: 10},
          dateAfter: "2024-01-01",
          baseCurrency: {is: $token}
        ) {
          exchange {
            name
          }
          quoteCurrency {
            symbol
          }
          tradeAmount(in: USD)
          count
        }
      }
    }
    """
    return execute_graphql(query, {"token": token_address})


def get_top_tokens(limit: int = 20) -> str:
    """Get top traded tokens on Solana DEXes
    
    Args:
        limit: Number of tokens to return
    """
    query = """
    query ($limit: Int) {
      ethereum(network: solana) {
        dexTrades(
          options: {limit: $limit, desc: "count"}
          dateAfter: "2024-01-01"
        ) {
          baseCurrency {
            symbol
            address
          }
          count
          tradeAmount(in: USD)
        }
      }
    }
    """
    return execute_graphql(query, {"limit": limit})


registry.register(
    name="bitquery_token_trades",
    toolset="dex",
    schema={
        "name": "bitquery_token_trades",
        "description": "Get recent DEX trades for a token from Bitquery GraphQL API (Solana)",
        "parameters": {
            "type": "object",
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "Token mint address (e.g., Solana token address)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max trades to return",
                    "default": 20
                }
            },
            "required": ["token_address"]
        }
    },
    handler=lambda args, **kw: get_token_trades(
        args.get("token_address", ""),
        args.get("limit", 20)
    ),
    check_fn=check_requirements
)

registry.register(
    name="bitquery_token_liquidity",
    toolset="dex",
    schema={
        "name": "bitquery_token_liquidity",
        "description": "Get token liquidity across DEXes from Bitquery",
        "parameters": {
            "type": "object",
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "Token mint address"
                }
            },
            "required": ["token_address"]
        }
    },
    handler=lambda args, **kw: get_token_liquidity(args.get("token_address", "")),
    check_fn=check_requirements
)

registry.register(
    name="bitquery_top_tokens",
    toolset="dex",
    schema={
        "name": "bitquery_top_tokens",
        "description": "Get top traded tokens on Solana DEXes from Bitquery",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of tokens to return",
                    "default": 20
                }
            }
        }
    },
    handler=lambda args, **kw: get_top_tokens(args.get("limit", 20)),
    check_fn=check_requirements
)