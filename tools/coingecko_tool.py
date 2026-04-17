import json
from tools.registry import registry

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


def _get_requests():
    try:
        import requests
        return requests
    except ImportError:
        return None


def check_requirements() -> bool:
    requests = _get_requests()
    if requests is None:
        return False
    try:
        response = requests.get(f"{COINGECKO_BASE_URL}/ping", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def _fetch_json(url: str, params: dict | None = None, timeout: int = 10):
    requests = _get_requests()
    if requests is None:
        raise RuntimeError("requests library is not installed")

    response = requests.get(url, params=params or {}, timeout=timeout)
    response.raise_for_status()
    return response.json()


def get_coin_price(coin_id: str, currency: str = "usd") -> str:
    try:
        data = _fetch_json(
            f"{COINGECKO_BASE_URL}/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": currency,
                "include_24hr_change": "true",
            },
        )
        if coin_id not in data:
            return json.dumps({"error": f"Coin {coin_id} not found"})

        price_data = data[coin_id]
        return json.dumps(
            {
                "coin_id": coin_id,
                "currency": currency,
                "price": price_data.get(currency, 0),
                "change_24h": price_data.get(f"{currency}_24h_change", 0),
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_trending_coins() -> str:
    try:
        data = _fetch_json(f"{COINGECKO_BASE_URL}/search/trending")
        coins = []
        for coin in data.get("coins", []):
            item = coin.get("item", {})
            coins.append(
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "symbol": item.get("symbol"),
                    "market_cap_rank": item.get("market_cap_rank"),
                }
            )
        return json.dumps({"trending_coins": coins}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="coingecko_price",
    toolset="data",
    schema={
        "name": "coingecko_price",
        "description": "Get current price and 24h change for a cryptocurrency from CoinGecko.",
        "parameters": {
            "type": "object",
            "properties": {
                "coin_id": {
                    "type": "string",
                    "description": "Coin ID (e.g. 'bitcoin', 'ethereum').",
                },
                "currency": {
                    "type": "string",
                    "description": "Target fiat or crypto currency (default: usd).",
                    "default": "usd",
                },
            },
            "required": ["coin_id"],
        },
    },
    handler=lambda args, **kw: get_coin_price(
        args.get("coin_id", ""), args.get("currency", "usd")
    ),
    check_fn=check_requirements,
)

registry.register(
    name="coingecko_trending",
    toolset="data",
    schema={
        "name": "coingecko_trending",
        "description": "Get trending cryptocurrencies from CoinGecko.",
        "parameters": {"type": "object", "properties": {}},
    },
    handler=lambda args, **kw: get_trending_coins(),
    check_fn=check_requirements,
)
