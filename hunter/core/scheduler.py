"""
Scheduler for Hunter
Automated periodic scans and maintenance
"""
import asyncio
import logging
from datetime import datetime
from typing import Callable, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from hunter.core.config import load_config
from hunter.core.database import Database
from hunter.data.sources import DataAggregator
from hunter.strategies.engine import StrategyEngine
from hunter.interfaces.telegram_bot import HunterTelegramBot

logger = logging.getLogger(__name__)


class HunterScheduler:
    """Scheduler for automated Hunter operations"""
    
    def __init__(self):
        self.config = load_config()
        self.scheduler = AsyncIOScheduler()
        self.db = Database()
        self.data_aggregator = DataAggregator({})
        self.strategy_engine = StrategyEngine("solana")
        self.telegram_bot: Optional[HunterTelegramBot] = None
        
        # Setup job listeners
        self.scheduler.add_listener(
            self._on_job_executed,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )
    
    def setup_telegram(self, bot_token: str):
        """Setup Telegram bot for alerts"""
        self.telegram_bot = HunterTelegramBot(bot_token)
    
    def start(self):
        """Start the scheduler"""
        logger.info("Starting Hunter scheduler...")
        
        # Schedule strategy scan
        self.scheduler.add_job(
            self._run_scan,
            trigger=IntervalTrigger(hours=self.config.scan.interval_hours),
            id="strategy_scan",
            name="Strategy Detection Scan",
            replace_existing=True
        )
        
        # Schedule cleanup of expired strategies
        self.scheduler.add_job(
            self._cleanup_expired,
            trigger=IntervalTrigger(hours=24),
            id="cleanup_expired",
            name="Cleanup Expired Strategies",
            replace_existing=True
        )
        
        # Schedule daily report
        self.scheduler.add_job(
            self._send_daily_report,
            trigger="cron",  # Daily at 9 AM
            hour=9,
            minute=0,
            id="daily_report",
            name="Daily Performance Report",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started. Next scan in {self.config.scan.interval_hours} hours")
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping Hunter scheduler...")
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def _run_scan(self):
        """Execute strategy scan"""
        logger.info("Running scheduled strategy scan...")
        
        scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Get market data
            market_data = {
                "tokens": self.data_aggregator.get_market_overview(),
                "ecosystem": "solana"
            }
            
            # Run strategy detection
            strategies = self.strategy_engine.scan(market_data)
            
            # Filter by confidence
            filtered = self.strategy_engine.filter_by_confidence(
                strategies, 
                self.config.risk.min_confidence_threshold
            )
            
            logger.info(f"Scan complete. Found {len(filtered)} strategies ({len(strategies)} raw)")
            
            # Save to database
            for strategy in filtered:
                self.db.save_strategy(strategy)
                
                # Send alert if high confidence
                if (strategy.confidence >= self.config.telegram.alert_min_confidence and
                    self.telegram_bot):
                    # TODO: Get chat_id from config or database
                    # For now, skip alert until we have proper chat_id management
                    pass
            
            # Log scan completion
            self._log_scan(scan_id, "solana", len(filtered), None)
            
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            self._log_scan(scan_id, "solana", 0, str(e))
    
    def _cleanup_expired(self):
        """Clean up expired strategies"""
        logger.info("Cleaning up expired strategies...")
        # TODO: Implement cleanup logic
        # Mark strategies as expired when valid_until < now
        pass
    
    async def _send_daily_report(self):
        """Send daily performance report"""
        logger.info("Sending daily report...")
        
        if not self.telegram_bot:
            return
        
        # Get P&L summary
        pnl = self.db.get_pnl_summary()
        
        report_text = f"""
📊 *Daily Report - {datetime.now().strftime('%Y-%m-%d')}*

*Paper Trading Performance:*
Total P&L: ${pnl.get('total_pnl_usd', 0):,.2f}
Win Rate: {pnl.get('win_rate', 0):.1f}%
Total Trades: {pnl.get('total_trades', 0)}

*Strategy Discovery:*
Active Strategies: {len(self.db.get_active_strategies())}

*24h Activity:*
Scan completed: {datetime.now().strftime('%H:%M')}
        """
        
        # TODO: Send to configured chat_id
        logger.info("Daily report generated (Telegram sending not implemented)")
    
    def _log_scan(self, scan_id: str, ecosystem: str, strategies_found: int, error: Optional[str]):
        """Log scan to database"""
        # TODO: Implement scan logging
        pass
    
    def _on_job_executed(self, event):
        """Handle job execution events"""
        if event.exception:
            logger.error(f"Job {event.job_id} failed: {event.exception}")
        else:
            logger.debug(f"Job {event.job_id} executed successfully")
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        jobs = self.scheduler.get_jobs()
        
        return {
            "running": self.scheduler.running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                }
                for job in jobs
            ]
        }
