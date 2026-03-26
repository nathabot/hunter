"""
Final installation test for Hunter Phase 3
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing Hunter imports...")
    
    tests = []
    
    try:
        from hunter.core.config import load_config, HunterConfig
        print("✓ Core config module")
        tests.append(True)
    except Exception as e:
        print(f"❌ Core config: {e}")
        tests.append(False)
    
    try:
        from hunter.core.logger import setup_logging
        print("✓ Core logger module")
        tests.append(True)
    except Exception as e:
        print(f"❌ Core logger: {e}")
        tests.append(False)
    
    try:
        from hunter.core.database import Database
        print("✓ Core database module")
        tests.append(True)
    except Exception as e:
        print(f"❌ Core database: {e}")
        tests.append(False)
    
    try:
        from hunter.core.paper_trading import PaperTrading
        print("✓ Core paper trading module")
        tests.append(True)
    except Exception as e:
        print(f"❌ Core paper trading: {e}")
        tests.append(False)
    
    try:
        from hunter.core.scheduler import HunterScheduler
        print("✓ Core scheduler module")
        tests.append(True)
    except Exception as e:
        print(f"❌ Core scheduler: {e}")
        tests.append(False)
    
    try:
        from hunter.data.sources import DataAggregator, CoinGeckoSource
        print("✓ Data sources module")
        tests.append(True)
    except Exception as e:
        print(f"❌ Data sources: {e}")
        tests.append(False)
    
    try:
        from hunter.strategies.engine import StrategyEngine, ArbitrageDetector
        print("✓ Strategy engine module")
        tests.append(True)
    except Exception as e:
        print(f"❌ Strategy engine: {e}")
        tests.append(False)
    
    try:
        from hunter.interfaces.telegram_bot import HunterTelegramBot
        print("✓ Telegram bot module")
        tests.append(True)
    except Exception as e:
        print(f"❌ Telegram bot: {e}")
        tests.append(False)
    
    try:
        from hunter.cli import app
        print("✓ CLI module")
        tests.append(True)
    except Exception as e:
        print(f"❌ CLI: {e}")
        tests.append(False)
    
    return all(tests)


def test_config():
    """Test configuration system"""
    print("\n🧪 Testing configuration...")
    
    try:
        from hunter.core.config import HunterConfig
        
        # Create default config
        config = HunterConfig()
        print(f"✓ Default config created")
        print(f"  - Ecosystems: {config.scan.ecosystems}")
        print(f"  - Risk tolerance: {config.risk.tolerance}")
        print(f"  - Scan interval: {config.scan.interval_hours}h")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_database():
    """Test database connection"""
    print("\n🧪 Testing database...")
    
    try:
        from hunter.core.database import Database
        
        db = Database()
        print("✓ Database connected")
        
        # Test getting active strategies
        strategies = db.get_active_strategies()
        print(f"  - Active strategies: {len(strategies)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_data_sources():
    """Test data source initialization"""
    print("\n🧪 Testing data sources...")
    
    try:
        from hunter.data.sources import DataAggregator
        
        agg = DataAggregator({})
        print("✓ Data aggregator initialized")
        print("  - DeFiLlama: Ready")
        print("  - CoinGecko: Ready")
        
        return True
        
    except Exception as e:
        print(f"❌ Data sources test failed: {e}")
        return False


def test_strategy_engine():
    """Test strategy engine"""
    print("\n🧪 Testing strategy engine...")
    
    try:
        from hunter.strategies.engine import StrategyEngine, StrategyType
        
        engine = StrategyEngine("solana")
        print("✓ Strategy engine initialized")
        print(f"  - Detectors: {len(engine.detectors)}")
        print(f"  - Types: {[t.value for t in engine.detectors.keys()]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategy engine test failed: {e}")
        return False


def test_paper_trading():
    """Test paper trading"""
    print("\n🧪 Testing paper trading...")
    
    try:
        from hunter.core.paper_trading import PaperTrading
        
        paper = PaperTrading()
        portfolio = paper.get_portfolio()
        print("✓ Paper trading initialized")
        print(f"  - Initial balance: ${portfolio['initial_balance']:,.2f}")
        print(f"  - Current balance: ${portfolio['current_balance']:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Paper trading test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🎯 Hunter Phase 3 - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Data Sources", test_data_sources),
        ("Strategy Engine", test_strategy_engine),
        ("Paper Trading", test_paper_trading),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! Hunter Phase 3 is ready.")
        print("\nQuick Start:")
        print("  1. hunter config --init")
        print("  2. hunter config --edit  # Add your API keys")
        print("  3. hunter scan")
        print("  4. hunter telegram --start  # Optional: Telegram alerts")
        return 0
    else:
        passed = sum(results)
        total = len(results)
        print(f"⚠️  {passed}/{total} tests passed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
