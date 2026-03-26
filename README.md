# 🎯 HUNTER

**AI Agent for Web3 Strategy Hunting**

An autonomous, open-source agent that discovers, validates, and tracks profitable strategies in Web3 ecosystems. Built with the 21 Agentic Design Patterns.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🌟 Features

- 🔍 **Autonomous Strategy Discovery** - Scans Solana (and soon SUI, BASE) for profitable opportunities
- 🧠 **21 Design Patterns** - Built using proven agentic architecture patterns
- 📊 **Data-Driven Analysis** - No hype, only on-chain data and metrics
- 💰 **Paper Trading** - Test strategies without real money
- 🔔 **Smart Alerts** - Get notified only for high-confidence opportunities
- 🛡️ **Risk-First** - Safety checks before profit calculations
- 💾 **Persistent Memory** - Learns from past strategies and performance

---

## 🏗️ Architecture

Hunter implements all **21 Agentic Design Patterns**:

| Layer | Patterns Implemented |
|-------|---------------------|
| **Foundation** | Prompt Chaining, Routing, Parallelization, Reflection, Tool Use, Planning, Multi-Agent |
| **Advanced** | Memory Management, Learning, MCP, Goal Setting |
| **Resilience** | Exception Handling, Human-in-the-Loop, RAG |
| **Production** | A2A, Resource Optimization, Reasoning, Guardrails, Evaluation, Prioritization, Discovery |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/hunter.git
cd hunter
pip install -e .
```

### 2. Configure

```bash
# Copy example config
cp config/config.example.yaml config/config.yaml

# Edit with your settings
nano config/config.yaml
```

### 3. Setup Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create new bot: `/newbot`
3. Copy the bot token
4. Paste in `config/config.yaml`

### 4. Run Hunter

```bash
# CLI mode
hunter scan --ecosystem solana

# Start Telegram bot
hunter telegram --start

# Or start scheduler (background scanning)
hunter scheduler --start
```

---

## 📊 Data Sources

### Free Tier (Default)
- ✅ **DeFiLlama** - TVL, yields, protocol metrics
- ✅ **CoinGecko** - Price data, market cap
- ✅ **Solana RPC** - On-chain data (public endpoints)

### Upgradable (Paid APIs)
- 💎 **Birdeye** - Real-time Solana token data
- 💎 **Helius** - Enhanced Solana RPC
- 💎 **Twitter API** - Social sentiment
- 💎 **Custom RPC** - Dedicated nodes

All data sources are **swappable** via config - start free, upgrade when needed.

---

## 🎛️ Configuration

```yaml
# config/config.yaml
scan:
  interval_hours: 4
  ecosystems:
    - solana  # MVP: Solana only
  strategy_types:
    - arbitrage
    - yield_farming
    - momentum
    - airdrop_farming

risk_tolerance: conservative  # conservative | moderate | aggressive

apis:
  # Free tier (default)
  defillama: free
  coingecko: free
  
  # Paid tier (optional, add your keys)
  birdeye: YOUR_API_KEY_HERE
  helius: YOUR_API_KEY_HERE

telegram:
  bot_token: YOUR_BOT_TOKEN_HERE
  alert_min_confidence: 0.75
```

---

## 🧠 Design Philosophy

### Honest I/O
- Every claim backed by data
- Confidence scores (0.0-1.0)
- Explicit "unknowns" section
- "I don't know" > speculation

### Risk-First
- Risk assessment BEFORE profit potential
- Never suggest outright scams
- Survivorship bias detection
- Backtest with drawdown periods

### Zero Hype
- No emojis in analysis
- No "moon" or "guaranteed" language
- Neutral, quantitative output

---

## 📚 Documentation

- [Setup Guide](docs/setup/README.md)
- [Architecture](docs/architecture.md)
- [21 Patterns Implementation](docs/patterns/)
- [API Reference](docs/api/)
- [Contributing](CONTRIBUTING.md)

---

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) first.

### Ways to Contribute
- 🐛 Report bugs
- 💡 Suggest features
- 📖 Improve documentation
- 🔧 Submit PRs
- 💰 Donate (see below)

---

## 💝 Support Hunter

Hunter is **100% free and open source**. If you find it valuable, consider supporting development:

### Crypto Donations

| Chain | Address |
|-------|---------|
| **Solana** | `ErHgCUxZ4wLmBhc3c82mnWRBK1maiEYrry34G7zW6FJ5` |
| **Ethereum** | `0xeA8eBd6B76B10280A65390Af5f8E345D3863fE71` |
| **Bitcoin** | `bc1q8uxgmy9vdu90fc2na09783lsd6tcuudnw6uycl` |

*Note: Replace with actual addresses before publishing*

### Other Ways
- ⭐ Star this repo
- 🐦 Share on Twitter
- 💬 Join our Telegram community
- 🧪 Beta test new features

---

## 📄 License

[MIT License](LICENSE) - Feel free to use, modify, and distribute.

---

## ⚠️ Disclaimer

**NOT FINANCIAL ADVICE**. Hunter is a research tool for discovering strategies. Always:
- Do your own research (DYOR)
- Start with paper trading
- Never invest more than you can afford to lose
- Verify all information independently

---

## 🙏 Acknowledgments

- Built with the [21 Agentic Design Patterns](https://github.com/DanieleSalatti/AgenticDesignPatterns) framework
- Inspired by the OpenClaw ecosystem
- Powered by the Solana community

---

**Built with ❤️ for the Web3 community**

*Remember: In a bull market everyone is a genius. Hunter helps you survive the bear.*
