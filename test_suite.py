#!/usr/bin/env python3
"""
Comprehensive test suite for Hunter
Run: python test_suite.py
"""
import sys
import os
sys.path.insert(0, '/root/hunter')

from datetime import datetime

def print_header(text):
    print("\n" + "="*60)
    print(f"🧪 {text}")
    print("="*60)

def print_result(success, message):
    emoji = "✅" if success else "❌"
    print(f"{emoji} {message}")
    return success

def test_imports():
    """Test all module imports"""
    print_header("Testing Module Imports")
    
    results = []
    
    modules = [
        ("hunter.core.config", "Config"),
        ("hunter.core.logger", "Logger"),
        ("hunter.core.database", "Database"),
        ("hunter.core.paper_trading", "PaperTrading"),
        ("hunter.core.scheduler", "Scheduler"),
        ("hunter.data.sources", "Data Sources"),
        ("hunter.strategies.engine", "Strategy Engine"),
        ("hunter.interfaces.telegram_bot", "Telegram Bot"),
        ("hunter.cli", "CLI"),
    ]
    
    for module, name in modules:
        try:
            __import__(module)
            results.append(print_result(True, f"{name} ({module})"))
        except Exception as e:
            results.append(print_result(False, f"{name}: {e}"))
    
    return all(results)

def test_database():
    """Test database operations"""
    print_header("Testing Database")
    
    results = []
    
    try:
        from hunter.core.database import Database, StrategyModel
        from hunter.strategies.engine import (
            Strategy, StrategyType, RiskLevel, Risk, Recommendation
        )
        
        # Create database
        db = Database()
        results.append(print_result(True, "Database initialization"))
        
        # Test strategy save with unique ID
        import uuid
        test_strategy = Strategy(
            strategy_id=f"test_{uuid.uuid4().hex[:8]}",
            name="Test Strategy",
            ecosystem="solana",
            type=StrategyType.ARBITRAGE,
            confidence=0.8,
            confidence_reasoning="Test",
            risk_level=RiskLevel.MEDIUM,
            risks=[Risk(type="test", severity=RiskLevel.LOW, description="Test risk")],
            profit_potential={"apr": "10%"},
            data_sources=["test"],
            unknowns=["test"],
            survivorship_bias_risk="Low",
            recommendation=Recommendation.PAPER_TRADE,
            position_size_suggestion="5%",
            detected_at=datetime.now(),
            valid_until=datetime.now(),
            execution_steps=["step1"]
        )
        
        saved = db.save_strategy(test_strategy)
        results.append(print_result(True, f"Strategy saved (ID: {saved.get('id', 'N/A')})"))
        
        # Test retrieval
        active = db.get_active_strategies()
        results.append(print_result(True, f"Retrieved {len(active)} strategies"))
        
        # Test paper trade
        trade = db.create_paper_trade("test_001", "SOL", 100.0, 1000.0)
        results.append(print_result(True, f"Paper trade created (ID: {trade.get('trade_id', 'N/A')})"))
        
        # Test PnL
        pnl = db.get_pnl_summary()
        results.append(print_result(True, f"PnL summary retrieved (trades: {pnl['total_trades']})"))
        
    except Exception as e:
        results.append(print_result(False, f"Database error: {e}"))
    
    return all(results)

def test_config():
    """Test configuration system"""
    print_header("Testing Configuration")
    
    results = []
    
    try:
        from hunter.core.config import load_config, save_config, create_default_config
        
        # Create default config
        path = create_default_config()
        results.append(print_result(True, f"Default config created at {path}"))
        
        # Load config
        config = load_config()
        results.append(print_result(True, "Config loaded"))
        
        # Verify values
        assert config.scan.ecosystems == ["solana"]
        assert config.risk.tolerance in ["conservative", "moderate", "aggressive"]
        results.append(print_result(True, "Config values validated"))
        
    except Exception as e:
        results.append(print_result(False, f"Config error: {e}"))
    
    return all(results)

def test_data_sources():
    """Test data source connections"""
    print_header("Testing Data Sources")
    
    results = []
    
    try:
        from hunter.data.sources import DataAggregator, CoinGeckoSource
        
        # Initialize
        agg = DataAggregator({})
        results.append(print_result(True, "DataAggregator initialized"))
        
        # Test CoinGecko (may fail if rate limited)
        try:
            cg = CoinGeckoSource()
            tokens = cg.get_market_data(per_page=3)
            if tokens:
                results.append(print_result(True, f"CoinGecko: Retrieved {len(tokens)} tokens"))
            else:
                results.append(print_result(False, "CoinGecko: No data returned"))
        except Exception as e:
            results.append(print_result(False, f"CoinGecko error (may be rate limit): {e}"))
        
    except Exception as e:
        results.append(print_result(False, f"Data sources error: {e}"))
    
    return all(results)

def test_strategy_engine():
    """Test strategy detection engine"""
    print_header("Testing Strategy Engine")
    
    results = []
    
    try:
        from hunter.strategies.engine import StrategyEngine, StrategyType, ArbitrageDetector
        
        # Initialize
        engine = StrategyEngine("solana")
        results.append(print_result(True, f"Engine initialized with {len(engine.detectors)} detectors"))
        
        # Test detector
        arb = ArbitrageDetector("solana")
        
        # Mock data
        mock_data = {
            "dex_prices": {
                "SOL": [
                    {"price": 145.0, "dex": "jupiter", "liquidity": 1000000},
                    {"price": 146.5, "dex": "raydium", "liquidity": 500000},
                ]
            },
            "ecosystem": "solana"
        }
        
        strategies = arb.detect(mock_data)
        results.append(print_result(True, f"Arbitrage detection: Found {len(strategies)} strategies"))
        
        if strategies:
            s = strategies[0]
            results.append(print_result(
                0 <= s.confidence <= 1,
                f"Confidence score valid: {s.confidence:.0%}"
            ))
        
    except Exception as e:
        results.append(print_result(False, f"Strategy engine error: {e}"))
    
    return all(results)

def test_paper_trading():
    """Test paper trading system"""
    print_header("Testing Paper Trading")
    
    results = []
    
    try:
        from hunter.core.paper_trading import PaperTrading
        from hunter.strategies.engine import Strategy, StrategyType, RiskLevel, Risk, Recommendation
        import uuid
        
        # Initialize
        paper = PaperTrading(initial_balance=10000.0)
        portfolio = paper.get_portfolio()
        
        results.append(print_result(
            portfolio['initial_balance'] == 10000.0,
            f"Initial balance: ${portfolio['initial_balance']:,.2f}"
        ))
        
        # Create mock strategy with unique ID
        strategy = Strategy(
            strategy_id=f"paper_test_{uuid.uuid4().hex[:8]}",
            name="Test Arbitrage",
            ecosystem="solana",
            type=StrategyType.ARBITRAGE,
            confidence=0.8,
            confidence_reasoning="Test",
            risk_level=RiskLevel.MEDIUM,
            risks=[Risk(type="test", severity=RiskLevel.LOW, description="Test")],
            profit_potential={"apr": "10%"},
            data_sources=["test"],
            unknowns=["test"],
            survivorship_bias_risk="Low",
            recommendation=Recommendation.PAPER_TRADE,
            position_size_suggestion="5%",
            detected_at=datetime.now(),
            valid_until=datetime.now(),
            execution_steps=["step1"]
        )
        
        # Execute
        trade = paper.execute_strategy(strategy, "SOL")
        if trade:
            results.append(print_result(True, f"Trade executed (ID: {trade['trade_id'][:8]}...)"))
        else:
            results.append(print_result(False, "Trade execution failed"))
        
        # Check portfolio
        portfolio = paper.get_portfolio()
        results.append(print_result(
            portfolio['open_positions'] >= 0,
            f"Open positions: {portfolio['open_positions']}"
        ))
        
    except Exception as e:
        results.append(print_result(False, f"Paper trading error: {e}"))
    
    return all(results)

def test_cli():
    """Test CLI commands"""
    print_header("Testing CLI")
    
    results = []
    
    try:
        from hunter.cli import app
        from typer.testing import CliRunner
        
        runner = CliRunner()
        
        # Test help
        result = runner.invoke(app, ["--help"])
        results.append(print_result(
            result.exit_code == 0,
            "CLI --help works"
        ))
        
        # Test status
        result = runner.invoke(app, ["status"])
        results.append(print_result(
            result.exit_code == 0,
            "CLI status command works"
        ))
        
    except Exception as e:
        results.append(print_result(False, f"CLI error: {e}"))
    
    return all(results)

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🎯 HUNTER COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Data Sources", test_data_sources),
        ("Strategy Engine", test_strategy_engine),
        ("Paper Trading", test_paper_trading),
        ("CLI", test_cli),
    ]
    
    all_results = []
    for name, test_func in tests:
        try:
            result = test_func()
            all_results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            all_results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for name, result in all_results:
        emoji = "✅" if result else "❌"
        print(f"{emoji} {name}")
    
    passed = sum(1 for _, r in all_results if r)
    total = len(all_results)
    
    print("\n" + "="*60)
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\nHunter is fully operational!")
        return 0
    else:
        print(f"⚠️  {passed}/{total} TESTS PASSED")
        print("\nSome tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
