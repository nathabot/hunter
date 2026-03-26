"""
Paper Trading Module for Hunter
Simulates trades without real money
"""
from datetime import datetime
from typing import List, Dict, Optional
import uuid

from hunter.core.database import Database
from hunter.strategies.engine import Strategy, Recommendation


class PaperTrading:
    """Paper trading simulator"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.db = Database()
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}  # token -> position info
    
    def execute_strategy(self, strategy: Strategy, token_symbol: str = None) -> Optional[Dict]:
        """
        Execute a strategy in paper trading mode
        
        Only executes if recommendation is not REJECT
        """
        if strategy.recommendation == Recommendation.REJECT:
            return None
        
        # Determine position size
        position_pct = self._parse_position_size(strategy.position_size_suggestion)
        position_size = self.balance * position_pct
        
        # Don't exceed max position size from config
        max_position = 1000.0  # TODO: Get from config
        position_size = min(position_size, max_position)
        
        # Get entry price (would come from market data in real implementation)
        entry_price = 100.0  # Placeholder
        
        # Create paper trade
        trade = self.db.create_paper_trade(
            strategy_id=strategy.strategy_id,
            token_symbol=token_symbol or strategy.name.split()[0],
            entry_price=entry_price,
            position_size=position_size
        )
        
        # Deduct from balance
        self.balance -= position_size
        
        return trade
    
    def close_position(self, trade_id: str, exit_price: float, notes: str = None) -> Optional[Dict]:
        """Close a paper trading position"""
        trade = self.db.close_paper_trade(trade_id, exit_price, notes)
        
        if trade:
            # Return funds to balance (plus/minus P&L)
            self.balance += trade['position_size_usd'] + trade.get('pnl_absolute', 0)
            return trade
        
        return None
    
    def get_portfolio(self) -> Dict:
        """Get current portfolio state"""
        open_trades = self.db.get_paper_trades(status="open")
        closed_trades = self.db.get_paper_trades(status="closed")
        pnl_summary = self.db.get_pnl_summary()
        
        # Calculate total value
        position_value = sum(t["position_size_usd"] for t in open_trades)
        total_value = self.balance + position_value
        
        return {
            "initial_balance": self.initial_balance,
            "current_balance": self.balance,
            "position_value": position_value,
            "total_value": total_value,
            "total_return": ((total_value - self.initial_balance) / self.initial_balance) * 100,
            "open_positions": len(open_trades),
            "closed_trades": len(closed_trades),
            "win_rate": pnl_summary.get("win_rate", 0),
            "total_pnl": pnl_summary.get("total_pnl_usd", 0)
        }
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        return self.db.get_paper_trades(status="open")
    
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Get trade history"""
        return self.db.get_paper_trades()[:limit]
    
    def generate_report(self, days: int = 7) -> Dict:
        """Generate performance report"""
        pnl_summary = self.db.get_pnl_summary()
        portfolio = self.get_portfolio()
        
        return {
            "period_days": days,
            "portfolio": portfolio,
            "pnl_summary": pnl_summary,
            "report_generated_at": datetime.now().isoformat()
        }
    
    def _parse_position_size(self, suggestion: str) -> float:
        """Parse position size suggestion (e.g., '5% of portfolio')"""
        try:
            # Extract number before %
            pct_str = suggestion.split('%')[0].strip()
            pct = float(pct_str) / 100
            return min(pct, 0.5)  # Max 50% per position
        except:
            return 0.05  # Default 5%
