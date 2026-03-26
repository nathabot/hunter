"""
Telegram Bot Integration for Hunter
Provides real-time alerts and interactive commands
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)

from hunter.core.config import load_config
from hunter.strategies.engine import Strategy, Recommendation

logger = logging.getLogger(__name__)

# Conversation states
CONFIGURING, SCANNING = range(2)


class HunterTelegramBot:
    """Telegram bot for Hunter alerts and interaction"""
    
    def __init__(self, token: Optional[str] = None):
        self.config = load_config()
        self.token = token or self.config.telegram.bot_token
        self.application: Optional[Application] = None
        
        if not self.token:
            raise ValueError("Telegram bot token not configured. Run: hunter config --edit")
    
    async def start(self):
        """Start the bot"""
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("scan", self.cmd_scan))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("config", self.cmd_config))
        self.application.add_handler(CommandHandler("alerts", self.cmd_alerts))
        self.application.add_handler(CommandHandler("pnl", self.cmd_pnl))
        self.application.add_handler(CommandHandler("strategies", self.cmd_strategies))
        
        # Callback handlers for buttons
        self.application.add_handler(CallbackQueryHandler(self.on_callback))
        
        logger.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
    
    async def stop(self):
        """Stop the bot"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """
🎯 *Welcome to Hunter Bot*

Your autonomous Web3 strategy hunter.

*Available Commands:*
/scan - Run strategy scan
/status - System status
/strategies - View active strategies
/pnl - Paper trading P&L
/alerts - Manage alerts
/config - View configuration
/help - Show this help

*Auto-Alerts:*
You'll receive notifications when high-confidence strategies are detected.
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Scan Now", callback_data="scan")],
            [InlineKeyboardButton("📊 Status", callback_data="status")],
            [InlineKeyboardButton("💰 P&L", callback_data="pnl")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
*Hunter Bot Commands*

*Strategy Hunting:*
/scan [ecosystem] - Run manual scan
/strategies - List active strategies

*Monitoring:*
/status - System status
/pnl - Paper trading performance
/alerts on|off - Toggle alerts

*Configuration:*
/config - View current config
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def cmd_scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan command"""
        await update.message.reply_text("🔍 Running strategy scan...")
        
        # TODO: Integrate with actual scan
        # For now, mock response
        await asyncio.sleep(2)
        
        await update.message.reply_text(
            "✅ Scan complete!\n\n"
            "Found 3 strategies:\n"
            "• SOL Arbitrage (82% confidence)\n"
            "• Marinade Yield (75% confidence)\n"
            "• RAY Momentum (65% confidence)"
        )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        config = load_config()
        
        status_text = f"""
📊 *Hunter Status*

*Ecosystem:* {', '.join(config.scan.ecosystems)}
*Risk Level:* {config.risk.tolerance}
*Scan Interval:* {config.scan.interval_hours}h

*Paper Trading:* {'✅ Active' if config.paper_trading.enabled else '❌ Disabled'}
*Balance:* ${config.paper_trading.initial_balance_usd:,.0f}

*Last Scan:* Never
*Strategies Found:* 0
*Active Positions:* 0
        """
        
        await update.message.reply_text(status_text, parse_mode="Markdown")
    
    async def cmd_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /config command"""
        config = load_config()
        
        config_text = f"""
⚙️ *Configuration*

*Ecosystems:* {', '.join(config.scan.ecosystems)}
*Strategy Types:* {', '.join(config.scan.strategy_types[:3])}...
*Risk Tolerance:* {config.risk.tolerance}
*Min Confidence:* {config.risk.min_confidence_threshold}

To edit config, use CLI:
`hunter config --edit`
        """
        
        await update.message.reply_text(config_text, parse_mode="Markdown")
    
    async def cmd_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        args = context.args
        
        if args and args[0].lower() in ['on', 'off']:
            status = args[0].lower()
            await update.message.reply_text(
                f"🔔 Alerts turned *{status.upper()}*\n\n"
                f"You'll receive notifications for strategies with confidence ≥ {self.config.telegram.alert_min_confidence}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "🔔 *Alert Settings*\n\n"
                f"Status: ✅ Enabled\n"
                f"Min Confidence: {self.config.telegram.alert_min_confidence}\n"
                f"Min Profit: {self.config.telegram.alert_min_profit_apr}\n\n"
                "Use `/alerts on` or `/alerts off` to toggle",
                parse_mode="Markdown"
            )
    
    async def cmd_pnl(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pnl command"""
        pnl_text = """
💰 *Paper Trading P&L*

*Total Balance:* $10,000.00
*Total P&L:* $0.00 (0.00%)
*Open Positions:* 0

*Recent Trades:*
No trades yet.

Start scanning to discover strategies!
        """
        await update.message.reply_text(pnl_text, parse_mode="Markdown")
    
    async def cmd_strategies(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /strategies command"""
        strategies_text = """
📋 *Active Strategies*

No active strategies found.

Run `/scan` to discover opportunities.
        """
        await update.message.reply_text(strategies_text, parse_mode="Markdown")
    
    async def on_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "scan":
            await self.cmd_scan(update, context)
        elif query.data == "status":
            await self.cmd_status(update, context)
        elif query.data == "pnl":
            await self.cmd_pnl(update, context)
    
    async def send_strategy_alert(self, chat_id: int, strategy: Strategy):
        """Send strategy alert to user"""
        if not self.application:
            return
        
        # Format recommendation emoji
        rec_emoji = {
            Recommendation.REJECT: "❌",
            Recommendation.PAPER_TRADE: "🧪",
            Recommendation.TEST_SMALL: "⚠️",
            Recommendation.APPROVED: "✅"
        }.get(strategy.recommendation, "❓")
        
        alert_text = f"""
🎯 *New Strategy Detected*

*{strategy.name}*

📊 *Confidence:* {strategy.confidence:.0%}
⚠️ *Risk Level:* {strategy.risk_level.value}
💰 *Profit Potential:* {strategy.profit_potential.get('apr', 'Unknown')}

{rec_emoji} *Recommendation:* {strategy.recommendation.value}

*Risks:*
{chr(10).join(f"• [{r.severity.value}] {r.description[:50]}..." if len(r.description) > 50 else f"• [{r.severity.value}] {r.description}" for r in strategy.risks[:3])}

Use `/strategies` to view details.
        """
        
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=alert_text,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")


def run_bot():
    """Run the bot (entry point)"""
    bot = HunterTelegramBot()
    asyncio.run(bot.start())


if __name__ == "__main__":
    run_bot()
