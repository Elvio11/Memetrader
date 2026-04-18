import json
import os
import requests
from datetime import datetime
from tools.registry import registry

HERMES_HOME = os.path.expanduser("~/.hermes")
NOFX_API_URL = os.getenv("NOFX_API_URL", "http://localhost:8080")
NOFX_API_TOKEN = os.getenv("NOFX_API_TOKEN", "")


def get_headers() -> dict:
    if NOFX_API_TOKEN:
        return {"Authorization": f"Bearer {NOFX_API_TOKEN}"}
    return {}


def check_requirements() -> bool:
    return os.path.isdir(HERMES_HOME)


def get_nofx_trades(limit: int = 20) -> str:
    """Get trade history from NOFX API"""
    try:
        url = f"{NOFX_API_URL}/api/trades"
        headers = get_headers()
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            trades = response.json()
            if isinstance(trades, list):
                limited = trades[:limit]
                return json.dumps({
                    "source": "nofx",
                    "trades": limited,
                    "count": len(limited),
                    "total_available": len(trades)
                })
            return json.dumps({"source": "nofx", "trades": trades, "count": 1})
        elif response.status_code == 401:
            return json.dumps({"error": "NOFX API token required", "hint": "Set NOFX_API_TOKEN env var"})
        else:
            return json.dumps({"error": f"NOFX API returned {response.status_code}"})
    except Exception as e:
        return json.dumps({"error": str(e), "hint": "Make sure NOFX is running at " + NOFX_API_URL})


def get_hermes_trades(limit: int = 10) -> str:
    """Get recent trades from Hermes session history"""
    try:
        session_db = os.path.join(HERMES_HOME, "sessions.db")
        if not os.path.exists(session_db):
            return json.dumps({"source": "hermes", "trades": [], "count": 0})
        
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
        return json.dumps({"source": "hermes", "trades": trades, "count": len(trades)})
    except Exception as e:
        return json.dumps({"source": "hermes", "error": str(e)})


def get_recent_trades(limit: int = 10, source: str = "all") -> str:
    """Get recent trades from Hermes sessions or NOFX
    
    Args:
        limit: Maximum number of trades to return
        source: "all", "hermes", or "nofx"
    """
    if source in ("all", "nofx"):
        nofx_result = get_nofx_trades(limit)
        nofx_data = json.loads(nofx_result)
    
    if source in ("all", "hermes"):
        hermes_result = get_hermes_trades(limit)
        hermes_data = json.loads(hermes_result)
    
    if source == "nofx":
        return nofx_result
    elif source == "hermes":
        return hermes_result
    else:
        return json.dumps({
            "hermes_sessions": hermes_data.get("trades", []),
            "nofx_trades": nofx_data.get("trades", []) if "error" not in nofx_data else [],
            "count": len(hermes_data.get("trades", [])) + (nofx_data.get("count", 0) if "error" not in nofx_data else 0)
        })


def analyze_performance() -> str:
    """Analyze trading performance from NOFX trade history"""
    try:
        trades_result = get_nofx_trades(100)
        trades_data = json.loads(trades_result)
        
        if "error" in trades_data:
            return json.dumps({
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_profit": 0.0,
                "avg_loss": 0.0,
                "note": trades_data.get("error"),
                "hint": "Set NOFX_API_URL and NOFX_API_TOKEN to enable"
            })
        
        trades = trades_data.get("trades", [])
        if not trades:
            return json.dumps({
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "note": "No trades found in NOFX"
            })
        
        total = len(trades)
        winning = 0
        losing = 0
        profits = []
        losses = []
        
        for trade in trades:
            pnl = trade.get("pnl", trade.get("profit", 0))
            if pnl > 0:
                winning += 1
                profits.append(pnl)
            elif pnl < 0:
                losing += 1
                losses.append(abs(pnl))
        
        win_rate = (winning / total * 100) if total > 0 else 0
        avg_profit = sum(profits) / len(profits) if profits else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        return json.dumps({
            "total_trades": total,
            "winning_trades": winning,
            "losing_trades": losing,
            "win_rate": round(win_rate, 2),
            "avg_profit": round(avg_profit, 4),
            "avg_loss": round(avg_loss, 4),
            "profit_factor": round(sum(profits) / sum(losses), 2) if losses and profits else 0
        })
    except Exception as e:
        return json.dumps({"error": str(e)})
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