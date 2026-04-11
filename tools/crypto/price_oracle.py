import json
import os
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


COINGECKO_API = "https://api.coingecko.com/api/v3"
BINANCE_API = "https://api.binance.com/api/v3"


_cached_prices: Dict[str, float] = {}
_cache_timestamp: float = 0
CACHE_TTL_SECONDS = 30


def _get_cache_key(chain: str, token: str) -> str:
    return f"{chain}:{token}".upper()


def _is_cache_valid() -> bool:
    return time.time() - _cache_timestamp < CACHE_TTL_SECONDS


def get_price_coingecko(coin_id: str, vs_currency: str = "usd") -> Optional[float]:
    """Get price from CoinGecko API"""
    if not REQUESTS_AVAILABLE:
        return None

    try:
        url = f"{COINGECKO_API}/simple/price"
        params = {"ids": coin_id, "vs_currencies": vs_currency}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data.get(coin_id, {}).get(vs_currency)
        if price is None:
            print(f"Warning: No price found for {coin_id}, returning 0")
            return 0.0
        return price
    except Exception as e:
        print(f"Error fetching price for {coin_id}: {e}")
        return None


def get_token_price(chain: str, token: str) -> Optional[float]:
    """Get token price with caching"""
    global _cached_prices, _cache_timestamp

    cache_key = _get_cache_key(chain, token)

    if cache_key in _cached_prices and _is_cache_valid():
        return _cached_prices[cache_key]

    # Map common tokens to CoinGecko IDs
    token_to_cg = {
        "ethereum": {
            "ETH": "ethereum",
            "WETH": "weth",
            "USDC": 1.0,  # Stablecoin - assume $1
            "USDT": 1.0,  # Stablecoin - assume $1
            "PEPE": "pepe",
            "SHIB": "shiba-inu",
            "DOGE": "dogecoin",
            "WIF": "dogwifhat",
            "BONK": "bonk",
            "SOL": "solana",
            "ARB": "arbitrum",
            "BASE": "base",
        },
        "solana": {
            "SOL": "solana",
            "USDC": 1.0,  # Stablecoin
            "USDT": 1.0,  # Stablecoin
            "BONK": "bonk",
            "WIF": "dogwifhat",
            "POPCAT": "popcat",
        },
        "base": {
            "ETH": "ethereum",
            "WETH": "weth",
            "USDC": "usd-coin",
        },
        "arbitrum": {
            "ETH": "ethereum",
            "WETH": "weth",
            "USDC": "usd-coin",
        },
    }

    cg_id = token_to_cg.get(chain, {}).get(token)
    if not cg_id:
        return None

    # Handle stablecoins (fixed price of 1.0)
    if isinstance(cg_id, (int, float)):
        return float(cg_id)

    price = get_price_coingecko(cg_id)
    if price is not None:
        _cached_prices[cache_key] = price
        _cache_timestamp = time.time()

    return price


def get_prices_batch(tokens: List[Dict[str, str]]) -> Dict[str, float]:
    """Get prices for multiple tokens at once"""
    global _cached_prices, _cache_timestamp

    result = {}
    cg_ids = []

    token_to_cg = {
        "ethereum": {
            "ETH": "ethereum",
            "WETH": "weth",
            "USDC": "usd-coin",
            "USDT": "tether",
            "PEPE": "pepe",
            "SHIB": "shiba-inu",
            "DOGE": "dogecoin",
            "WIF": "dogwifhat",
        },
        "solana": {
            "SOL": "solana",
            "USDC": "usd-coin",
            "USDT": "tether",
            "BONK": "bonk",
            "WIF": "dogwifhat",
            "POPCAT": "popcat",
        },
        "base": {"ETH": "ethereum", "WETH": "weth", "USDC": "usd-coin"},
        "arbitrum": {"ETH": "ethereum", "WETH": "weth", "USDC": "usd-coin"},
    }

    for chain, token in tokens:
        cache_key = _get_cache_key(chain, token)
        if cache_key in _cached_prices and _is_cache_valid():
            result[cache_key] = _cached_prices[cache_key]
            continue

        cg_id = token_to_cg.get(chain, {}).get(token)
        if cg_id and cg_id not in cg_ids:
            cg_ids.append(cg_id)

    if cg_ids:
        try:
            url = f"{COINGECKO_API}/simple/price"
            params = {"ids": ",".join(cg_ids), "vs_currencies": "usd"}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Map back
            for chain, token in tokens:
                cache_key = _get_cache_key(chain, token)
                cg_id = token_to_cg.get(chain, {}).get(token)
                if cg_id and cg_id in data:
                    price = data[cg_id].get("usd")
                    result[cache_key] = price
                    _cached_prices[cache_key] = price

            _cache_timestamp = time.time()
        except Exception:
            pass

    return result


def get_meme_token_price(token: str) -> Optional[float]:
    """Get price for any token by name (searches CoinGecko)"""
    if not REQUESTS_AVAILABLE:
        return None

    try:
        url = f"{COINGECKO_API}/search"
        params = {"query": token}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        coins = data.get("coins", [])
        if coins:
            cg_id = coins[0]["id"]
            return get_price_coingecko(cg_id)
    except Exception:
        return None


def get_trending_meme_tokens() -> List[Dict]:
    """Get trending meme tokens from CoinGecko"""
    if not REQUESTS_AVAILABLE:
        return []

    try:
        url = f"{COINGECKO_API}/search/trending"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        tokens = []
        for item in data.get("coins", [])[:20]:
            coin = item.get("item", {})
            tokens.append(
                {
                    "id": coin.get("id"),
                    "name": coin.get("name"),
                    "symbol": coin.get("symbol"),
                    "thumb": coin.get("thumb"),
                    "small": coin.get("small"),
                    "large": coin.get("large"),
                    "price_btc": coin.get("price_btc"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                }
            )
        return tokens
    except Exception:
        return []


def get_token_market_data(token_id: str) -> Optional[Dict]:
    """Get full market data for a token"""
    if not REQUESTS_AVAILABLE:
        return None

    try:
        url = f"{COINGECKO_API}/coins/{token_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "false",
            "developer_data": "false",
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "id": data.get("id"),
            "symbol": data.get("symbol"),
            "name": data.get("name"),
            "image": data.get("image", {}),
            "current_price": data.get("market_data", {})
            .get("current_price", {})
            .get("usd"),
            "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
            "market_cap_rank": data.get("market_data", {}).get("market_cap_rank"),
            "total_volume": data.get("market_data", {})
            .get("total_volume", {})
            .get("usd"),
            "price_change_24h": data.get("market_data", {}).get(
                "price_change_percentage_24h"
            ),
            "price_change_7d": data.get("market_data", {}).get(
                "price_change_percentage_7d"
            ),
            "price_change_30d": data.get("market_data", {}).get(
                "price_change_percentage_30d"
            ),
            "ath": data.get("market_data", {}).get("ath", {}).get("usd"),
            "atl": data.get("market_data", {}).get("atl", {}).get("usd"),
            "description": data.get("description", {}).get("en", "")[:500],
        }
    except Exception:
        return None


def search_tokens(query: str) -> List[Dict]:
    """Search for tokens on CoinGecko"""
    if not REQUESTS_AVAILABLE:
        return []

    try:
        url = f"{COINGECKO_API}/search"
        params = {"query": query}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return [
            {
                "id": coin.get("id"),
                "name": coin.get("name"),
                "symbol": coin.get("symbol"),
                "thumb": coin.get("thumb"),
                "market_cap_rank": coin.get("market_cap_rank"),
            }
            for coin in data.get("coins", [])[:15]
        ]
    except Exception:
        return []
