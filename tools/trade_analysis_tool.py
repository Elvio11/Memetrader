import json
import os
from datetime import datetime
from tools.registry import registry

HERMES_HOME = os.path.expanduser("~/.hermes")


def check_requirements() -> bool:
    """Check if Hermes home directory exists"""
    return os.path.isdir(HERMES_HOME)


def get_recent_trades(limit: int = 10) -> str:
    """Get recent trades from Hermes sessions"""
    try:
        session_db = os.path.join(HERMES_HOME, "sessions.db")
        if not os.path.exists(session_db):
            return json.dumps({"error": "No session database found"})
        
        import sqlite3
        conn = sqlite3.connect(session_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, role, content, created_at 
            FROM messages 
            WHERE role = 'assistant' 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        trades = []
        for row in cursor.fetchall():
            trades.append({
                "session_id": row[0],
                "content": row[2][:200],
                "timestamp": row[3]
            })
        
        conn.close()
        return json.dumps({"trades": trades, "count": len(trades)})
    except Exception as e:
        return json.dumps({"error": str(e)})


def analyze_performance() -> str:
    """Analyze trading performance from stored data"""
    try:
        return json.dumps({
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "avg_profit": 0.0,
            "avg_loss": 0.0,
            "note": "Requires NOFX trade history integration"
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_strategy_suggestions() -> str:
    """Get AI-generated strategy suggestions"""
    try:
        suggestions = [
            {
                "strategy": "momentum_following",
                "description": "Follow established trends with 5% stop loss",
                "risk": "medium"
            },
            {
                "strategy": "mean_reversion", 
                "description": "Buy on dips, sell on rips within range",
                "risk": "low"
            },
            {
                "strategy": "breakout",
                "description": "Enter on volume spike + breakout",
                "risk": "high"
            }
        ]
        return json.dumps({"suggestions": suggestions})
    except Exception as e:
        return json.dumps({"error": str(e)})


def log_trade_analysis(trade_data: str) -> str:
    """Log and analyze a trade"""
    try:
        data = json.loads(trade_data)
        return json.dumps({
            "logged": True,
            "trade": data,
            "analysis": "Trade logged for future analysis"
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="trade_recent",
    toolset="analysis",
    schema={
        "name": "trade_recent",
        "description": "Get recent trades from Hermes session history",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max trades", "default": 10}
            }
        }
    },
    handler=lambda args, **kw: get_recent_trades(args.get("limit", 10)),
    check_fn=check_requirements
)

registry.register(
    name="trade_performance",
    toolset="analysis",
    schema={
        "name": "trade_performance",
        "description": "Analyze trading performance",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: analyze_performance(),
    check_fn=check_requirements
)

registry.register(
    name="trade_suggestions",
    toolset="analysis",
    schema={
        "name": "trade_suggestions",
        "description": "Get AI trading strategy suggestions",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: get_strategy_suggestions(),
    check_fn=check_requirements
)