import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

from hermes_constants import get_hermes_home


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PositionSide(Enum):
    LONG = "long"
    SHORT = "short"


@dataclass
class PaperWallet:
    chain: str
    address: str
    private_key: str  # Only stored for paper trading simulation
    initial_balance: Dict[str, float] = field(default_factory=dict)
    current_balance: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.current_balance and self.initial_balance:
            self.current_balance = self.initial_balance.copy()

    def to_dict(self):
        return {
            "chain": self.chain,
            "address": self.address,
            "initial_balance": self.initial_balance,
            "current_balance": self.current_balance,
        }


@dataclass
class Trade:
    id: str
    chain: str
    pair: str  # e.g., "PEPE/ETH"
    side: str  # "buy" or "sell"
    order_type: str  # "market" or "limit"
    amount_in: float
    token_in: str
    amount_out: float
    token_out: str
    price: float
    price_usd: float
    timestamp: str
    tx_hash: str = ""
    status: str = "filled"
    fee: float = 0.0
    fee_usd: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class Position:
    id: str
    chain: str
    pair: str
    side: str
    entry_price: float
    current_price: float
    size: float
    token: str
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    open_timestamp: str = ""
    close_timestamp: str = ""
    status: str = "open"

    def to_dict(self):
        return asdict(self)


@dataclass
class PaperPortfolio:
    wallets: Dict[str, PaperWallet] = field(default_factory=dict)
    trades: List[Trade] = field(default_factory=list)
    positions: List[Position] = field(default_factory=list)
    total_value_usd: float = 0.0
    total_pnl_usd: float = 0.0
    realized_pnl_usd: float = 0.0

    def to_dict(self):
        return {
            "wallets": {k: v.to_dict() for k, v in self.wallets.items()},
            "trades": [t.to_dict() for t in self.trades],
            "positions": [p.to_dict() for p in self.positions],
            "total_value_usd": self.total_value_usd,
            "total_pnl_usd": self.total_pnl_usd,
            "realized_pnl_usd": self.realized_pnl_usd,
        }


class PaperTradingEngine:
    """Paper money trading engine - simulates trades without real funds"""

    def __init__(self, initial_capital: float = 10000.0, base_currency: str = "USD"):
        self.id = str(uuid.uuid4())
        self.initial_capital = initial_capital
        self.base_currency = base_currency
        self.portfolio = PaperPortfolio()
        self._initialize_wallets()

    def _initialize_wallets(self):
        """Create paper wallets for each supported chain with initial capital"""
        default_balances = {
            "ethereum": {"ETH": 5.0, "USDC": 10000.0},
            "solana": {"SOL": 10.0, "USDC": 10000.0},
            "base": {"ETH": 5.0, "USDC": 10000.0},
        }

        for chain, balances in default_balances.items():
            wallet = PaperWallet(
                chain=chain,
                address=f"0x{''.join([format(i, '02x') for i in range(20)])}",  # Mock address
                private_key="0x" + "".join([format(i, "02x") for i in range(32)]),
                initial_balance=balances,
                current_balance=balances.copy(),
            )
            self.portfolio.wallets[chain] = wallet

    def execute_trade(
        self,
        chain: str,
        pair: str,
        side: str,
        amount_in: float,
        token_in: str,
        amount_out: float,
        token_out: str,
        price: float,
        price_usd: float,
        fee: float = 0.0,
        fee_usd: float = 0.0,
    ) -> Dict:
        """Execute a paper trade - update balances without real transactions"""

        wallet = self.portfolio.wallets.get(chain)
        if not wallet:
            return {"success": False, "error": f"No wallet for chain: {chain}"}

        # Check balance
        if token_in in wallet.current_balance:
            if wallet.current_balance[token_in] < amount_in:
                return {"success": False, "error": f"Insufficient {token_in} balance"}

        # Execute the trade
        wallet.current_balance[token_in] = (
            wallet.current_balance.get(token_in, 0) - amount_in
        )
        wallet.current_balance[token_out] = (
            wallet.current_balance.get(token_out, 0) + amount_out
        )

        # Deduct fees
        if token_in in wallet.current_balance:
            wallet.current_balance[token_in] -= fee

        # Record trade
        trade = Trade(
            id=str(uuid.uuid4())[:8],
            chain=chain,
            pair=pair,
            side=side,
            order_type="market",
            amount_in=amount_in,
            token_in=token_in,
            amount_out=amount_out,
            token_out=token_out,
            price=price,
            price_usd=price_usd,
            timestamp=datetime.now().isoformat(),
            tx_hash=f"0xpaper{uuid.uuid4().hex[:8]}",
            status="filled",
            fee=fee,
            fee_usd=fee_usd,
        )
        self.portfolio.trades.append(trade)

        return {
            "success": True,
            "trade": trade.to_dict(),
            "new_balance": wallet.current_balance,
        }

    def get_balance(self, chain: str, token: str = None) -> Dict:
        """Get wallet balance"""
        wallet = self.portfolio.wallets.get(chain)
        if not wallet:
            return {}

        if token:
            return {"token": token, "balance": wallet.current_balance.get(token, 0.0)}

        return {"chain": chain, "balance": wallet.current_balance}

    def get_portfolio_value(self, prices: Dict[str, float]) -> float:
        """Calculate total portfolio value in USD"""
        total = 0.0

        for chain, wallet in self.portfolio.wallets.items():
            for token, balance in wallet.current_balance.items():
                if balance > 0:
                    # Get price in USD
                    price_key = f"{chain}:{token}".upper()
                    if price_key in prices:
                        total += balance * prices[price_key]
                    elif token == "USDC" or token == "USDT":
                        total += balance  # Stablecoin = $1
                    elif token in ["ETH", "SOL", "SUI"]:
                        # Fallback - use chain native price
                        if f"{chain}:NATIVE" in prices:
                            total += balance * prices[f"{chain}:NATIVE"]

        self.portfolio.total_value_usd = total
        return total

    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        return [p.to_dict() for p in self.portfolio.positions if p.status == "open"]

    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Get recent trades"""
        trades = sorted(self.portfolio.trades, key=lambda x: x.timestamp, reverse=True)
        return [t.to_dict() for t in trades[:limit]]

    def get_stats(self) -> Dict:
        """Get trading statistics"""
        total_trades = len(self.portfolio.trades)
        if total_trades == 0:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl_usd": self.portfolio.total_value_usd - self.initial_capital,
                "initial_capital": self.initial_capital,
                "current_value": self.portfolio.total_value_usd,
                "total_return_pct": (
                    (self.portfolio.total_value_usd - self.initial_capital)
                    / self.initial_capital
                )
                * 100
                if self.initial_capital > 0
                else 0,
            }

        # Calculate PnL from trades
        buy_trades = [t for t in self.portfolio.trades if t.side == "buy"]
        sell_trades = [t for t in self.portfolio.trades if t.side == "sell"]

        total_volume = sum(t.amount_in * t.price_usd for t in self.portfolio.trades)

        return {
            "total_trades": total_trades,
            "buy_trades": len(buy_trades),
            "sell_trades": len(sell_trades),
            "total_volume_usd": total_volume,
            "initial_capital": self.initial_capital,
            "current_value": self.portfolio.total_value_usd,
            "total_pnl_usd": self.portfolio.total_value_usd - self.initial_capital,
            "total_return_pct": (
                (self.portfolio.total_value_usd - self.initial_capital)
                / self.initial_capital
            )
            * 100,
        }

    def reset(self):
        """Reset paper trading to initial state"""
        self.portfolio = PaperPortfolio()
        self._initialize_wallets()

    def save_state(self, path: Path = None):
        """Save paper trading state"""
        if path is None:
            path = get_hermes_home() / "paper_trading.json"

        data = {
            "id": self.id,
            "initial_capital": self.initial_capital,
            "base_currency": self.base_currency,
            "portfolio": self.portfolio.to_dict(),
            "saved_at": datetime.now().isoformat(),
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        return str(path)

    def load_state(self, path: Path = None) -> bool:
        """Load paper trading state"""
        if path is None:
            path = get_hermes_home() / "paper_trading.json"

        if not path.exists():
            return False

        try:
            with open(path, "r") as f:
                data = json.load(f)

            self.id = data.get("id", str(uuid.uuid4()))
            self.initial_capital = data.get("initial_capital", 10000.0)
            self.base_currency = data.get("base_currency", "USD")

            # Reconstruct portfolio
            pf = data.get("portfolio", {})
            self.portfolio.wallets = {
                k: PaperWallet(**v) for k, v in pf.get("wallets", {}).items()
            }
            self.portfolio.trades = [Trade(**t) for t in pf.get("trades", [])]
            self.portfolio.positions = [Position(**p) for p in pf.get("positions", [])]

            return True
        except Exception:
            return False


# Global paper trading engine instance
_paper_engine: Optional[PaperTradingEngine] = None


def get_paper_engine() -> PaperTradingEngine:
    """Get or create the global paper trading engine"""
    global _paper_engine
    if _paper_engine is None:
        _paper_engine = PaperTradingEngine()
    return _paper_engine


def reset_paper_trading():
    """Reset paper trading state"""
    global _paper_engine
    _paper_engine = PaperTradingEngine()
    return {"success": True, "message": "Paper trading reset to initial state"}
