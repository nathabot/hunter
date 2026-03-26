# Hunter Quick Start Guide

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Git (for cloning)

### Install Hunter

```bash
# Clone the repository
git clone https://github.com/yourusername/hunter.git
cd hunter

# Install in editable mode
pip install -e .

# Verify installation
hunter --help
```

## ⚙️ Initial Configuration

### 1. Create Default Config

```bash
hunter config --init
```

This creates `~/.hunter/config.yaml` with default settings.

### 2. Edit Configuration

```bash
hunter config --edit
```

Or manually edit `~/.hunter/config.yaml`:

```yaml
scan:
  interval_hours: 4  # Scan every 4 hours
  ecosystems:
    - solana  # Start with Solana

risk:
  tolerance: conservative  # Options: conservative, moderate, aggressive
  min_confidence_threshold: 0.7

# Add your API keys (optional - can use free tier)
apis:
  defillama: free
  coingecko: free
  # birdeye: YOUR_BIRDEYE_API_KEY  # Optional paid API

telegram:
  bot_token: YOUR_TELEGRAM_BOT_TOKEN  # Optional - see below
```

## 🎯 Basic Usage

### Run Your First Scan

```bash
# Simple scan
hunter scan

# Scan with filters
hunter scan --ecosystem solana --min-confidence 0.75

# Dry run (don't save to database)
hunter scan --dry-run
```

### View Results

```bash
# View stored strategies
hunter strategies

# View with filters
hunter strategies --ecosystem solana --min-confidence 0.8
```

### Paper Trading

```bash
# Scan and execute in paper trading mode
hunter scan --execute --min-confidence 0.75

# View portfolio
hunter trade

# View open positions
hunter trade --open

# Close a position
hunter trade --close TRADE_ID --exit-price 150.0

# View P&L report
hunter pnl
```

## 🤖 Telegram Bot Setup

### 1. Create Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow prompts to name your bot
4. **Copy the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Add Token to Config

```bash
hunter config --edit
```

Add your token:
```yaml
telegram:
  bot_token: "123456789:ABCdefGHIjklMNOpqr..."
  alert_min_confidence: 0.75
```

### 3. Start the Bot

```bash
hunter telegram --start
```

The bot will run in the foreground. Press `Ctrl+C` to stop.

### Bot Commands

Once running, message your bot:
- `/start` - Welcome message
- `/scan` - Trigger manual scan
- `/status` - Show system status
- `/strategies` - View active strategies
- `/pnl` - Show paper trading P&L
- `/alerts` - Toggle alerts on/off
- `/help` - Show all commands

## ⏰ Automated Scanning

### Start Scheduler

```bash
# Start background scheduler
hunter scheduler --start
```

The scheduler will:
- Run scans every X hours (configurable)
- Send Telegram alerts for high-confidence strategies
- Generate daily reports
- Clean up expired strategies

Press `Ctrl+C` to stop.

### Schedule Options

Edit `config.yaml`:
```yaml
scan:
  interval_hours: 4  # Scan every 4 hours
  # Or use cron-style:
  # cron: "0 */4 * * *"  # Every 4 hours on the hour
```

## 📊 Understanding Strategy Output

### Example Strategy

```
Strategy: SOL-USDC Arbitrage (0.85% spread)
Type: arbitrage
Confidence: 82%
Risk Level: MEDIUM
Recommendation: PAPER_TRADE
APR: 310%

Risks:
• [MEDIUM] Slippage on large trades
• [MEDIUM] MEV bot competition

Data Sources: jupiter, raydium
Unknowns:
• Execution speed
• Transaction success rate
```

### Key Metrics

- **Confidence (0-100%)**: How likely this strategy is to work
- **Risk Level**: LOW / MEDIUM / HIGH / CRITICAL
- **Recommendation**: 
  - `REJECT` - Too risky or low confidence
  - `PAPER_TRADE` - Test with fake money first
  - `TEST_SMALL` - Try with small real amount
  - `APPROVED` - Meets all criteria

## 🎓 Example Workflows

### Workflow 1: Daily Scanning

```bash
# Morning scan
hunter scan --min-confidence 0.75

# Review results
hunter strategies

# Check P&L on existing positions
hunter pnl

# Let scheduler run for continuous monitoring
hunter scheduler --start
```

### Workflow 2: Find Yield Opportunities

```bash
# Scan specifically for yield farming
hunter scan --type yield_farming --min-confidence 0.7

# Execute best opportunities in paper trading
hunter scan --type yield_farming --execute --min-confidence 0.8

# Monitor positions daily
hunter trade --open
```

### Workflow 3: Telegram Alerts

```bash
# Setup bot (one time)
hunter config --edit
# Add bot_token

# Start bot
hunter telegram --start

# Now you get automatic alerts!
# High-confidence strategies will be sent to your Telegram
```

## ⚠️ Risk Management

### Conservative Settings (Recommended for Beginners)

```yaml
risk:
  tolerance: conservative
  min_confidence_threshold: 0.75
  max_position_size_pct: 5.0  # Max 5% per strategy
```

### Always Paper Trade First

```bash
# Test strategy before real money
hunter scan --execute --min-confidence 0.75

# Monitor for 1-2 weeks
hunter pnl

# If profitable in paper trading, consider small real position
```

### Understanding Risks

Every strategy includes:
1. **Risk Level**: Overall risk assessment
2. **Specific Risks**: Detailed risk factors
3. **Unknowns**: What we don't know
4. **Survivorship Bias**: Is this repeatable?

**Never invest more than you can afford to lose!**

## 🐛 Troubleshooting

### "No strategies found"

- Lower confidence threshold: `--min-confidence 0.6`
- Check API connections: `hunter test-data`
- Ensure market data is available

### "Database error"

```bash
# Check database exists
ls ~/.hunter/hunter.db

# Reset database (WARNING: loses all data)
rm ~/.hunter/hunter.db
hunter scan  # Will recreate
```

### "Telegram bot not responding"

1. Check bot token is correct in config
2. Ensure you've messaged the bot `/start`
3. Check bot isn't blocked
4. Restart: `hunter telegram --start`

### "Import errors"

```bash
# Reinstall
pip install -e . --force-reinstall

# Or use requirements.txt
pip install -r requirements.txt
```

## 📚 Next Steps

- Read [Architecture Guide](architecture.md) to understand how Hunter works
- Check [Strategy Guide](strategies.md) for detailed strategy explanations
- See [API Reference](api.md) for programmatic usage
- Join our community: [Telegram Group](https://t.me/hunter_community)

## 💡 Tips

1. **Start Conservative**: Use conservative risk settings initially
2. **Paper Trade Everything**: Test for weeks before real money
3. **Diversify**: Don't put all capital in one strategy
4. **Monitor Daily**: Check P&L and adjust positions
5. **Keep Learning**: Markets change, adapt your approach

---

**Remember**: Hunter helps you find opportunities, but you make the final decisions. Always DYOR (Do Your Own Research)!
