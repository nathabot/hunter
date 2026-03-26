"""
Database Models for Hunter
SQLite persistence for strategies, paper trading, and session memory
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
import json

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime,
    Boolean, Text, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class StrategyStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    EXECUTED = "executed"
    REJECTED = "rejected"


class TradeStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class StrategyModel(Base):
    """Database model for detected strategies"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    ecosystem = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    
    confidence = Column(Float, nullable=False)
    confidence_reasoning = Column(Text)
    
    risk_level = Column(String, nullable=False)
    risks_json = Column(Text)  # JSON list of risks
    
    profit_potential_json = Column(Text)  # JSON dict
    data_sources_json = Column(Text)  # JSON list
    unknowns_json = Column(Text)  # JSON list
    survivorship_bias_risk = Column(Text)
    
    recommendation = Column(String, nullable=False)
    position_size_suggestion = Column(String)
    
    detected_at = Column(DateTime, default=func.now())
    valid_until = Column(DateTime)
    status = Column(SQLEnum(StrategyStatus), default=StrategyStatus.ACTIVE)
    
    execution_steps_json = Column(Text)
    
    # Relationship to trades
    trades = relationship("TradeModel", back_populates="strategy")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "strategy_id": self.strategy_id,
            "name": self.name,
            "ecosystem": self.ecosystem,
            "type": self.type,
            "confidence": self.confidence,
            "confidence_reasoning": self.confidence_reasoning,
            "risk_level": self.risk_level,
            "risks": json.loads(self.risks_json) if self.risks_json else [],
            "profit_potential": json.loads(self.profit_potential_json) if self.profit_potential_json else {},
            "data_sources": json.loads(self.data_sources_json) if self.data_sources_json else [],
            "unknowns": json.loads(self.unknowns_json) if self.unknowns_json else [],
            "survivorship_bias_risk": self.survivorship_bias_risk,
            "recommendation": self.recommendation,
            "position_size_suggestion": self.position_size_suggestion,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "status": self.status.value if self.status else None,
            "execution_steps": json.loads(self.execution_steps_json) if self.execution_steps_json else []
        }


class TradeModel(Base):
    """Database model for paper trades"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    trade_id = Column(String, unique=True, nullable=False)
    strategy_id = Column(String, ForeignKey("strategies.strategy_id"), nullable=False)
    
    # Trade details
    token_symbol = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    position_size_usd = Column(Float, nullable=False)
    
    # P&L tracking
    pnl_absolute = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    
    # Status
    status = Column(SQLEnum(TradeStatus), default=TradeStatus.OPEN)
    opened_at = Column(DateTime, default=func.now())
    closed_at = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    
    # Relationship
    strategy = relationship("StrategyModel", back_populates="trades")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "trade_id": self.trade_id,
            "strategy_id": self.strategy_id,
            "token_symbol": self.token_symbol,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "position_size_usd": self.position_size_usd,
            "pnl_absolute": self.pnl_absolute,
            "pnl_percent": self.pnl_percent,
            "status": self.status.value if self.status else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "notes": self.notes
        }


class ScanLogModel(Base):
    """Log of all scans performed"""
    __tablename__ = "scan_logs"
    
    id = Column(Integer, primary_key=True)
    scan_id = Column(String, unique=True, nullable=False)
    ecosystem = Column(String, nullable=False)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    strategies_found = Column(Integer, default=0)
    error_message = Column(Text)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "ecosystem": self.ecosystem,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "strategies_found": self.strategies_found,
            "error_message": self.error_message
        }


class MemoryModel(Base):
    """Session memory and learnings"""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(String, unique=True, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    category = Column(String, nullable=False)  # 'learning', 'market_context', 'decision'
    content = Column(Text, nullable=False)
    tags_json = Column(Text)  # JSON list
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "memory_id": self.memory_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "category": self.category,
            "content": self.content,
            "tags": json.loads(self.tags_json) if self.tags_json else [],
            "importance": self.importance
        }


class ChatHistoryModel(Base):
    """Persistent chat history for Hunter AI"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, nullable=False, index=True)  # user_id or session_id
    timestamp = Column(DateTime, default=func.now())
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    context_json = Column(Text)  # Additional context (strategy_id, etc.)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "role": self.role,
            "content": self.content,
            "context": json.loads(self.context_json) if self.context_json else {}
        }


class Database:
    """Database manager for Hunter"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            from pathlib import Path
            db_path = str(Path.home() / ".hunter" / "hunter.db")
        
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_strategy(self, strategy) -> Dict:
        """Save a strategy to database"""
        from hunter.strategies.engine import Strategy
        
        session = self.Session()
        try:
            # Convert Strategy dataclass to model
            model = StrategyModel(
                strategy_id=strategy.strategy_id,
                name=strategy.name,
                ecosystem=strategy.ecosystem,
                type=strategy.type.value,
                confidence=strategy.confidence,
                confidence_reasoning=strategy.confidence_reasoning,
                risk_level=strategy.risk_level.value,
                risks_json=json.dumps([{"type": r.type, "severity": r.severity.value, "description": r.description} for r in strategy.risks]),
                profit_potential_json=json.dumps(strategy.profit_potential),
                data_sources_json=json.dumps(strategy.data_sources),
                unknowns_json=json.dumps(strategy.unknowns),
                survivorship_bias_risk=strategy.survivorship_bias_risk,
                recommendation=strategy.recommendation.value,
                position_size_suggestion=strategy.position_size_suggestion,
                detected_at=strategy.detected_at,
                valid_until=strategy.valid_until,
                execution_steps_json=json.dumps(strategy.execution_steps)
            )
            
            session.add(model)
            session.commit()
            session.refresh(model)
            result = model.to_dict()
            return result
            
        finally:
            session.close()
    
    def get_active_strategies(self, ecosystem: str = None, min_confidence: float = 0.6) -> List[Dict]:
        """Get active strategies from database"""
        session = self.Session()
        try:
            query = session.query(StrategyModel).filter(
                StrategyModel.status == StrategyStatus.ACTIVE,
                StrategyModel.confidence >= min_confidence
            )
            
            if ecosystem:
                query = query.filter(StrategyModel.ecosystem == ecosystem)
            
            strategies = query.all()
            return [s.to_dict() for s in strategies]
            
        finally:
            session.close()
    
    def create_paper_trade(self, strategy_id: str, token_symbol: str, 
                          entry_price: float, position_size: float) -> Dict:
        """Create a paper trade"""
        import uuid
        
        session = self.Session()
        try:
            trade = TradeModel(
                trade_id=f"trade_{uuid.uuid4().hex[:8]}",
                strategy_id=strategy_id,
                token_symbol=token_symbol,
                entry_price=entry_price,
                position_size_usd=position_size,
                status=TradeStatus.OPEN
            )
            
            session.add(trade)
            session.commit()
            session.refresh(trade)
            return trade.to_dict()
            
        finally:
            session.close()
    
    def close_paper_trade(self, trade_id: str, exit_price: float, notes: str = None) -> Optional[Dict]:
        """Close a paper trade and calculate P&L"""
        session = self.Session()
        try:
            trade = session.query(TradeModel).filter_by(trade_id=trade_id).first()
            
            if not trade or trade.status != TradeStatus.OPEN:
                return None
            
            trade.exit_price = exit_price
            trade.closed_at = datetime.now()
            trade.status = TradeStatus.CLOSED
            trade.notes = notes
            
            # Calculate P&L
            if trade.entry_price > 0:
                trade.pnl_percent = ((exit_price - trade.entry_price) / trade.entry_price) * 100
                trade.pnl_absolute = (trade.pnl_percent / 100) * trade.position_size_usd
            
            session.commit()
            session.refresh(trade)
            return trade.to_dict()
            
        finally:
            session.close()
    
    def get_paper_trades(self, status: str = None) -> List[Dict]:
        """Get paper trading history"""
        session = self.Session()
        try:
            query = session.query(TradeModel)
            
            if status:
                # Convert string to TradeStatus enum by value
                query = query.filter(TradeModel.status == TradeStatus(status.lower()))
            
            trades = query.order_by(TradeModel.opened_at.desc()).all()
            return [t.to_dict() for t in trades]
            
        finally:
            session.close()
    
    def get_pnl_summary(self) -> Dict[str, Any]:
        """Get P&L summary"""
        session = self.Session()
        try:
            trades = session.query(TradeModel).all()
            
            closed_trades = [t for t in trades if t.status == TradeStatus.CLOSED]
            open_trades = [t for t in trades if t.status == TradeStatus.OPEN]
            
            total_pnl = sum(t.pnl_absolute for t in closed_trades)
            avg_pnl_percent = sum(t.pnl_percent for t in closed_trades) / len(closed_trades) if closed_trades else 0
            
            winning_trades = [t for t in closed_trades if t.pnl_absolute > 0]
            losing_trades = [t for t in closed_trades if t.pnl_absolute <= 0]
            
            return {
                "total_trades": len(trades),
                "closed_trades": len(closed_trades),
                "open_trades": len(open_trades),
                "winning_trades": len(winning_trades),
                "losing_trades": len(losing_trades),
                "win_rate": len(winning_trades) / len(closed_trades) * 100 if closed_trades else 0,
                "total_pnl_usd": total_pnl,
                "avg_pnl_percent": avg_pnl_percent,
                "best_trade": max((t.pnl_absolute for t in closed_trades), default=0),
                "worst_trade": min((t.pnl_absolute for t in closed_trades), default=0)
            }
            
        finally:
            session.close()
    
    def add_memory(self, category: str, content: str, tags: List[str] = None, importance: float = 0.5):
        """Add a memory/learning"""
        import uuid
        
        session = self.Session()
        try:
            memory = MemoryModel(
                memory_id=f"mem_{uuid.uuid4().hex[:8]}",
                category=category,
                content=content,
                tags_json=json.dumps(tags or []),
                importance=importance
            )
            
            session.add(memory)
            session.commit()
            
        finally:
            session.close()
    
    def get_memories(self, category: str = None, limit: int = 50) -> List[Dict]:
        """Get memories, ordered by importance and recency"""
        session = self.Session()
        try:
            query = session.query(MemoryModel)
            
            if category:
                query = query.filter(MemoryModel.category == category)
            
            memories = query.order_by(
                MemoryModel.importance.desc(),
                MemoryModel.timestamp.desc()
            ).limit(limit).all()
            
            return [m.to_dict() for m in memories]
            
        finally:
            session.close()
    
    def save_chat_message(self, session_id: str, role: str, content: str, context: Dict = None):
        """Save a chat message to persistent storage"""
        session = self.Session()
        try:
            chat_msg = ChatHistoryModel(
                session_id=session_id,
                role=role,
                content=content,
                context_json=json.dumps(context or {})
            )
            
            session.add(chat_msg)
            session.commit()
            
        finally:
            session.close()
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a session"""
        session = self.Session()
        try:
            messages = session.query(ChatHistoryModel).filter(
                ChatHistoryModel.session_id == session_id
            ).order_by(
                ChatHistoryModel.timestamp.asc()
            ).limit(limit).all()
            
            return [m.to_dict() for m in messages]
            
        finally:
            session.close()
    
    def clear_chat_history(self, session_id: str):
        """Clear chat history for a session"""
        session = self.Session()
        try:
            session.query(ChatHistoryModel).filter(
                ChatHistoryModel.session_id == session_id
            ).delete()
            session.commit()
            
        finally:
            session.close()
