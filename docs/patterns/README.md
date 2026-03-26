# 21 Agentic Design Patterns - Implementation Guide

This document maps how Hunter implements each of the 21 Agentic Design Patterns.

## Foundation Layer (7 patterns)

### 1. Prompt Chaining
**What:** Breaking complex tasks into a sequence of simpler prompts
**Implementation:** `hunter/core/ai_agent.py` - `analyze_strategy()` method
- Step 1: Collect market data
- Step 2: Run strategy detectors
- Step 3: AI analysis with reasoning
- Step 4: Risk assessment
- Step 5: Output formatting

### 2. Routing
**What:** Directing inputs to specialized handlers
**Implementation:** `hunter/cli.py` - Typer command routing
- `/scan` → Strategy scanning
- `/chat` → AI conversation
- `/trade` → Paper trading
- `/telegram` → Bot control

### 3. Parallelization
**What:** Running multiple tasks simultaneously
**Implementation:** `hunter/strategies/engine.py` - `StrategyEngine.scan()`
- Multiple detectors run in parallel
- Data aggregation from multiple sources
- Concurrent API calls with rate limiting

### 4. Reflection
**What:** Self-critique and validation
**Implementation:** `hunter/strategies/engine.py` - `BaseStrategyDetector.calculate_confidence()`
- Self-critique factors in confidence scoring
- "What could go wrong?" analysis
- Survivorship bias detection

### 5. Tool Use
**What:** Calling external tools/APIs
**Implementation:** `hunter/data/sources.py`
- DeFiLlama API for TVL data
- CoinGecko API for price data
- Jupiter API for DEX routing
- LLM API for analysis

### 6. Planning
**What:** Breaking goals into subtasks
**Implementation:** `hunter/core/scheduler.py` - `HunterScheduler`
- Periodic scan scheduling
- Task decomposition:
  1. Fetch market data
  2. Run detectors
  3. Filter by confidence
  4. AI analysis (if enabled)
  5. Alert if high confidence

### 7. Multi-Agent
**What:** Multiple specialized agents working together
**Implementation:** `hunter/strategies/engine.py` - Multiple detectors
- `ArbitrageDetector` - Cross-DEX arbitrage
- `YieldFarmingDetector` - High APY pools
- `MomentumDetector` - Trend following
- `NFTSnipingDetector` - NFT opportunities
- `AirdropFarmingDetector` - Airdrop hunting
- Each acts as specialized sub-agent

---

## Advanced Layer (4 patterns)

### 8. Memory Management
**What:** Storing and retrieving context
**Implementation:** `hunter/core/database.py` - `ChatHistoryModel`
- Persistent chat history in SQLite
- Per-user session isolation
- Strategy memory across restarts

### 9. Learning
**What:** Improving from experience
**Implementation:** `hunter/core/paper_trading.py` - P&L tracking
- Track strategy performance
- Compare predicted vs actual results
- Adjust confidence calibration over time

### 10. MCP (Model Context Protocol)
**What:** Structured tool calling interface
**Implementation:** Planned - Not yet implemented
- Would standardize tool interfaces
- Enable dynamic tool discovery

### 11. Goal Setting
**What:** Dynamic goal decomposition
**Implementation:** `hunter/strategies/engine.py` - Strategy execution flow
- User sets target: Find profitable strategies
- System decomposes into:
  - Scan specific ecosystems
  - Filter by risk tolerance
  - Validate with paper trading
  - Report results

---

## Resilience Layer (3 patterns)

### 12. Exception Handling
**What:** Graceful error recovery
**Implementation:** Throughout codebase with try/except
- API failure fallback
- Database error handling
- Network retry logic in `hunter/data/sources.py`

### 13. Human-in-the-Loop
**What:** Human oversight and approval
**Implementation:** `hunter/interfaces/telegram_bot.py`
- Interactive Telegram commands
- Manual scan triggers
- Alert management (/alerts on/off)
- Strategy confirmation before execution

### 14. RAG (Retrieval-Augmented Generation)
**What:** Using external knowledge for LLM context
**Implementation:** `hunter/core/ai_agent.py` - `analyze_strategy()`
- Market data retrieved and fed to LLM
- Strategy context included in prompts
- Historical performance data

---

## Production Layer (7 patterns)

### 15. A2A (Agent-to-Agent)
**What:** Communication between agents
**Implementation:** Not yet implemented
- Would enable multi-agent collaboration
- Strategy sharing between instances

### 16. Resource Optimization
**What:** Efficient resource usage
**Implementation:** `hunter/data/sources.py` - Rate limiting
- API rate limiting
- Connection pooling
- Caching strategies

### 17. Reasoning
**What:** Chain-of-thought analysis
**Implementation:** `hunter/core/ai_agent.py` - LLM analysis
- AI explains reasoning for recommendations
- Confidence reasoning required
- Step-by-step analysis in prompts

### 18. Guardrails
**What:** Safety boundaries and constraints
**Implementation:** `hunter/core/config.py` - Risk configuration
- Max position size limits
- Confidence thresholds
- Risk tolerance settings (conservative/moderate/aggressive)
- Prohibited words/phrases in SOUL.md

### 19. Evaluation
**What:** Measuring performance
**Implementation:** `hunter/core/paper_trading.py` + `hunter/cli.py` - `pnl` command
- Win rate calculation
- P&L tracking
- Strategy success metrics

### 20. Prioritization
**What:** Ranking tasks by importance
**Implementation:** `hunter/strategies/engine.py` - `filter_by_confidence()`
- Strategies ranked by confidence score
- Risk-adjusted prioritization
- Time-sensitive opportunity prioritization

### 21. Discovery
**What:** Finding new strategies/opportunities
**Implementation:** Core feature of Hunter
- 8 different strategy detectors
- Automatic scanning
- New opportunity identification
- Market inefficiency detection

---

## Implementation Status Summary

| Category | Pattern | Status | Location |
|----------|---------|--------|----------|
| Foundation | Prompt Chaining | ✅ | `ai_agent.py` |
| Foundation | Routing | ✅ | `cli.py` |
| Foundation | Parallelization | ✅ | `engine.py` |
| Foundation | Reflection | ✅ | `engine.py` |
| Foundation | Tool Use | ✅ | `sources.py` |
| Foundation | Planning | ✅ | `scheduler.py` |
| Foundation | Multi-Agent | ✅ | `engine.py` |
| Advanced | Memory | ✅ | `database.py` |
| Advanced | Learning | ✅ | `paper_trading.py` |
| Advanced | MCP | 🟡 | Planned |
| Advanced | Goal Setting | ✅ | `engine.py` |
| Resilience | Exception Handling | ✅ | Throughout |
| Resilience | Human-in-Loop | ✅ | `telegram_bot.py` |
| Resilience | RAG | ✅ | `ai_agent.py` |
| Production | A2A | 🟡 | Planned |
| Production | Resource Optimization | ✅ | `sources.py` |
| Production | Reasoning | ✅ | `ai_agent.py` |
| Production | Guardrails | ✅ | `config.py` |
| Production | Evaluation | ✅ | `paper_trading.py` |
| Production | Prioritization | ✅ | `engine.py` |
| Production | Discovery | ✅ | Core feature |

**Legend:** ✅ Implemented | 🟡 Planned/Partial

---

## Total: 19/21 Implemented (90%)

The remaining 2 patterns (MCP, A2A) are architectural patterns that would require additional infrastructure and are marked for future implementation.
