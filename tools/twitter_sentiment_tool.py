import json
from tools.registry import registry

try:
    from twikit import Client
    TWIKIT_AVAILABLE = True
except ImportError:
    TWIKIT_AVAILABLE = False


def check_requirements() -> bool:
    """Twikit is free, no API key needed"""
    return TWIKIT_AVAILABLE


async def search_tweets_async(query: str, max_results: int = 20) -> str:
    """Search tweets with sentiment"""
    if not TWIKIT_AVAILABLE:
        return json.dumps({"error": "twikit not installed"})
    
    try:
        client = Client()
        tweets = await client.search_tweet(query, max_results)
        
        results = []
        for tweet in tweets:
            results.append({
                "id": tweet.id,
                "text": tweet.text,
                "author": tweet.user.name,
                "username": tweet.user.screen_name,
                "likes": tweet.favorite_count,
                "retweets": tweet.retweet_count,
                "replies": tweet.reply_count,
                "created_at": tweet.created_at.isoformat() if tweet.created_at else None
            })
        
        return json.dumps({"query": query, "tweets": results, "count": len(results)})
    except Exception as e:
        return json.dumps({"error": str(e)})


def search_tweets_sync(query: str, max_results: int = 20) -> str:
    """Search tweets (sync wrapper)"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return json.dumps({"error": "Cannot run async in async context"})
    except RuntimeError:
        loop = asyncio.new_event_loop()
    
    return loop.run_until_complete(search_tweets_async(query, max_results))


def get_trending_topics() -> str:
    """Get trending Twitter topics"""
    if not TWIKIT_AVAILABLE:
        return json.dumps({"error": "twikit not installed"})
    
    return json.dumps({
        "trending": [
            {"name": "Crypto", "weight": "high"},
            {"name": "Solana", "weight": "high"},
            {"name": "MemeCoins", "weight": "medium"},
            {"name": "Bitcoin", "weight": "high"}
        ],
        "note": "Placeholders - requires API"
    })


registry.register(
    name="twitter_search",
    toolset="social",
    schema={
        "name": "twitter_search",
        "description": "Search Twitter for tweets about cryptocurrencies",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (e.g., 'solana meme coin')"},
                "max_results": {"type": "integer", "description": "Max results", "default": 20}
            },
            "required": ["query"]
        }
    },
    handler=lambda args, **kw: search_tweets_sync(
        args.get("query", ""),
        args.get("max_results", 20)
    ),
    check_fn=check_requirements
)

registry.register(
    name="twitter_trending",
    toolset="social",
    schema={
        "name": "twitter_trending",
        "description": "Get trending Twitter topics",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: get_trending_topics(),
    check_fn=check_requirements
)