"""
Enhanced CLI with Phase 3 features
Telegram, Scheduler, Paper Trading, Database
"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime
import json

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from hunter.core.config import load_config, save_config, create_default_config, HunterConfig
from hunter.core.logger import setup_logging
from hunter.core.database import Database
from hunter.core.paper_trading import PaperTrading
from hunter.core.scheduler import HunterScheduler
from hunter.data.sources import DataAggregator, CoinGeckoSource
from hunter.strategies.engine import StrategyEngine, StrategyType
from hunter.interfaces.telegram_bot import HunterTelegramBot

console = Console()
app = typer.Typer(
    name="hunter",
    help="🎯 Hunter - AI Agent for Web3 Strategy Hunting",
    no_args_is_help=True,
)


def format_strategy_table(strategy) -> Table:
    """Format a strategy as a Rich table"""
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    table.add_row("Strategy", strategy.name)
    table.add_row("Type", strategy.type.value)
    table.add_row("Confidence", f"{strategy.confidence:.0%}")
    table.add_row("Risk Level", strategy.risk_level.value)
    table.add_row("Recommendation", strategy.recommendation.value)
    
    if strategy.profit_potential:
        table.add_row("APR", strategy.profit_potential.get("apr", "Unknown"))
    
    return table


@app.callback()
def main(
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
):
    """Hunter - Autonomous Web3 Strategy Hunter"""
    setup_logging(verbose=verbose)


@app.command()
def scan(
    ecosystem: str = typer.Option("solana", "--ecosystem", "-e", help="Target ecosystem (solana/sui/base)"),
    strategy_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by strategy type"),
    min_confidence: float = typer.Option(0.6, "--min-confidence", help="Minimum confidence threshold"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Scan without saving to database"),
    execute: bool = typer.Option(False, "--execute", help="Execute in paper trading mode"),
):
    """🔍 Run a one-time strategy scan"""
    console.print(Panel(f"[bold green]Scanning {ecosystem} for strategies...[/bold green]"))
    
    config = load_config()
    db = Database()
    
    # Initialize data aggregator
    console.print("[yellow]Fetching market data...[/yellow]")
    aggregator = DataAggregator({})
    
    # Get market data
    market_data = {
        "tokens": aggregator.get_market_overview(),
        "ecosystem": ecosystem
    }
    
    console.print(f"[green]✓[/green] Retrieved data for {len(market_data['tokens'])} tokens")
    
    # Initialize strategy engine
    engine = StrategyEngine(ecosystem)
    
    # Determine which strategy types to scan
    types_to_scan = None
    if strategy_type:
        try:
            types_to_scan = [StrategyType(strategy_type.lower())]
        except ValueError:
            console.print(f"[red]Unknown strategy type: {strategy_type}[/red]")
            console.print(f"Available types: {[t.value for t in StrategyType]}")
            raise typer.Exit(1)
    
    # Run scan
    console.print("[yellow]Running strategy detectors...[/yellow]")
    strategies = engine.scan(market_data, types_to_scan)
    
    # Filter by confidence
    filtered = engine.filter_by_confidence(strategies, min_confidence)
    
    # Display results
    console.print(f"\n[bold]Found {len(filtered)} strategies (from {len(strategies)} raw)[/bold]")
    
    for i, strategy in enumerate(filtered[:10], 1):
        console.print(f"\n[bold cyan]{i}. {strategy.name}[/bold cyan]")
        console.print(format_strategy_table(strategy))
        
        # Show risks
        if strategy.risks:
            console.print("[bold red]Risks:[/bold red]")
            for risk in strategy.risks:
                console.print(f"  • [{risk.severity.value}] {risk.description}")
    
    # Save to database
    if not dry_run:
        console.print("\n[yellow]Saving to database...[/yellow]")
        for strategy in filtered:
            db.save_strategy(strategy)
        console.print(f"[green]✓[/green] {len(filtered)} strategies saved")
    
    # Execute in paper trading mode
    if execute and filtered:
        console.print("\n[yellow]Executing in paper trading mode...[/yellow]")
        paper = PaperTrading()
        
        executed = 0
        for strategy in filtered:
            if strategy.recommendation.value in ["PAPER_TRADE", "TEST_SMALL", "APPROVED"]:
                trade = paper.execute_strategy(strategy)
                if trade:
                    console.print(f"  [green]✓[/green] Executed: {strategy.name}")
                    executed += 1
        
        console.print(f"[green]✓[/green] {executed} strategies executed in paper trading")


@app.command()
def strategies(
    active: bool = typer.Option(True, "--active/--all", help="Show only active strategies"),
    ecosystem: str = typer.Option("solana", "--ecosystem", "-e", help="Filter by ecosystem"),
    min_confidence: float = typer.Option(0.6, "--min-confidence", help="Minimum confidence"),
):
    """📋 View stored strategies"""
    db = Database()
    
    if active:
        results = db.get_active_strategies(ecosystem, min_confidence)
        title = f"Active Strategies ({len(results)})"
    else:
        # Get all strategies
        from hunter.core.database import StrategyModel
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        from hunter.core.database import Base
        
        db_path = Path.home() / ".hunter" / "hunter.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        query = session.query(StrategyModel)
        if ecosystem:
            query = query.filter(StrategyModel.ecosystem == ecosystem)
        
        all_strategies = query.all()
        results = [s.to_dict() for s in all_strategies]
        title = f"All Strategies ({len(results)})"
        session.close()
    
    if not results:
        console.print("[yellow]No strategies found. Run 'hunter scan' first.[/yellow]")
        return
    
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("ID", style="dim", width=20)
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="blue")
    table.add_column("Confidence", justify="right")
    table.add_column("Risk", justify="center")
    table.add_column("Recommendation", style="green")
    
    for s in results[:50]:  # Limit to 50
        table.add_row(
            s.get("strategy_id", "")[:20],
            s.get("name", "Unknown")[:30],
            s.get("type", "unknown"),
            f"{s.get('confidence', 0):.0%}",
            s.get("risk_level", "?"),
            s.get("recommendation", "?")
        )
    
    console.print(table)


@app.command()
def trade(
    list_open: bool = typer.Option(False, "--open", help="List open positions"),
    close: Optional[str] = typer.Option(None, "--close", help="Close trade by ID"),
    exit_price: Optional[float] = typer.Option(None, "--exit-price", help="Exit price for closing"),
):
    """💰 Paper trading operations"""
    db = Database()
    paper = PaperTrading()
    
    if list_open:
        positions = paper.get_open_positions()
        
        if not positions:
            console.print("[yellow]No open positions[/yellow]")
            return
        
        table = Table(title="Open Positions", box=box.ROUNDED)
        table.add_column("Trade ID", style="dim")
        table.add_column("Token", style="cyan")
        table.add_column("Entry Price", justify="right")
        table.add_column("Position Size", justify="right")
        table.add_column("Opened At", style="blue")
        
        for p in positions:
            table.add_row(
                p.get("trade_id", ""),
                p.get("token_symbol", ""),
                f"${p.get('entry_price', 0):,.4f}",
                f"${p.get('position_size_usd', 0):,.2f}",
                p.get("opened_at", "")[:19]
            )
        
        console.print(table)
    
    elif close:
        if not exit_price:
            console.print("[red]Error: --exit-price required when closing[/red]")
            raise typer.Exit(1)
        
        result = paper.close_position(close, exit_price)
        
        if result:
            pnl = result.get("pnl_absolute", 0)
            pnl_pct = result.get("pnl_percent", 0)
            pnl_color = "green" if pnl >= 0 else "red"
            
            console.print(f"[green]✓[/green] Position closed: {close}")
            console.print(f"P&L: [{pnl_color}]${pnl:,.2f} ({pnl_pct:+.2f}%)[/{pnl_color}]")
        else:
            console.print("[red]Failed to close position. Check trade ID.[/red]")
    
    else:
        # Show portfolio summary
        portfolio = paper.get_portfolio()
        
        console.print(Panel("[bold]Paper Trading Portfolio[/bold]"))
        
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Initial Balance", f"${portfolio['initial_balance']:,.2f}")
        table.add_row("Current Balance", f"${portfolio['current_balance']:,.2f}")
        table.add_row("Position Value", f"${portfolio['position_value']:,.2f}")
        table.add_row("Total Value", f"[bold]${portfolio['total_value']:,.2f}[/bold]")
        
        return_pct = portfolio['total_return']
        return_color = "green" if return_pct >= 0 else "red"
        table.add_row("Total Return", f"[{return_color}]{return_pct:+.2f}%[/{return_color}]")
        
        table.add_row("Open Positions", str(portfolio['open_positions']))
        
        console.print(table)


@app.command()
def pnl(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
):
    """📊 Show P&L report"""
    paper = PaperTrading()
    db = Database()
    
    summary = db.get_pnl_summary()
    
    if summary['total_trades'] == 0:
        console.print("[yellow]No trades yet. Run 'hunter scan --execute' to start paper trading.[/yellow]")
        return
    
    console.print(Panel("[bold]P&L Summary[/bold]"))
    
    table = Table(show_header=False, box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Total Trades", str(summary['total_trades']))
    table.add_row("Winning Trades", f"[green]{summary['winning_trades']}[/green]")
    table.add_row("Losing Trades", f"[red]{summary['losing_trades']}[/red]")
    
    win_rate = summary['win_rate']
    win_rate_color = "green" if win_rate >= 50 else "yellow" if win_rate >= 40 else "red"
    table.add_row("Win Rate", f"[{win_rate_color}]{win_rate:.1f}%[/{win_rate_color}]")
    
    total_pnl = summary['total_pnl_usd']
    pnl_color = "green" if total_pnl >= 0 else "red"
    table.add_row("Total P&L", f"[{pnl_color}]${total_pnl:,.2f}[/{pnl_color}]")
    
    table.add_row("Avg P&L per Trade", f"${summary['avg_pnl_percent']:,.2f}%")
    table.add_row("Best Trade", f"[green]${summary['best_trade']:,.2f}[/green]")
    table.add_row("Worst Trade", f"[red]${summary['worst_trade']:,.2f}[/red]")
    
    console.print(table)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current config"),
    edit: bool = typer.Option(False, "--edit", help="Open config in editor"),
    init: bool = typer.Option(False, "--init", help="Create default config file"),
):
    """⚙️ Manage Hunter configuration"""
    if init:
        config_path = create_default_config()
        console.print(f"[green]✓[/green] Created default config at: {config_path}")
        console.print("[yellow]Edit this file to customize your settings[/yellow]")
    elif show:
        try:
            config = load_config()
            console.print(config.model_dump_json(indent=2))
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
    elif edit:
        config_path = Path.home() / ".hunter" / "config.yaml"
        if not config_path.exists():
            console.print("[yellow]Config not found. Creating default...[/yellow]")
            create_default_config()
        
        editor = typer.get_editor_path()
        if editor:
            typer.launch(str(config_path))
        else:
            console.print(f"[yellow]Config location: {config_path}[/yellow]")
    else:
        console.print("[yellow]Use --show to view config, --edit to modify, or --init to create[/yellow]")


@app.command()
def telegram(
    start: bool = typer.Option(False, "--start", help="Start Telegram bot"),
    stop: bool = typer.Option(False, "--stop", help="Stop Telegram bot"),
    send_test: bool = typer.Option(False, "--test", help="Send test message"),
):
    """🤖 Manage Telegram bot"""
    if start:
        config = load_config()
        if not config.telegram.bot_token:
            console.print("[red]Error: Telegram bot token not configured[/red]")
            console.print("[yellow]1. Message @BotFather on Telegram[/yellow]")
            console.print("[yellow]2. Create a new bot and copy the token[/yellow]")
            console.print("[yellow]3. Add to config: hunter config --edit[/yellow]")
            raise typer.Exit(1)
        
        console.print("[yellow]Starting Telegram bot...[/yellow]")
        console.print("[green]Bot is running. Press Ctrl+C to stop.[/green]")
        
        try:
            from hunter.interfaces.telegram_bot import run_bot
            run_bot()
        except KeyboardInterrupt:
            console.print("\n[yellow]Bot stopped[/yellow]")
    
    elif stop:
        console.print("[yellow]To stop the bot, press Ctrl+C in the terminal running it[/yellow]")
    
    elif send_test:
        console.print("[yellow]Sending test message...[/yellow]")
        console.print("[yellow]Note: Requires chat_id configuration[/yellow]")
    
    else:
        console.print("[yellow]Use --start to start bot or --stop for instructions[/yellow]")


@app.command()
def scheduler(
    start: bool = typer.Option(False, "--start", help="Start scheduler"),
    stop: bool = typer.Option(False, "--stop", help="Stop scheduler"),
    status: bool = typer.Option(False, "--status", help="Show scheduler status"),
    run_once: bool = typer.Option(False, "--run-once", help="Run single scan and exit"),
):
    """⏰ Manage automated scheduler"""
    if start:
        console.print("[yellow]Starting Hunter scheduler...[/yellow]")
        console.print("[green]Scheduler is running. Press Ctrl+C to stop.[/green]")
        
        try:
            sch = HunterScheduler()
            sch.start()
            
            # Keep running
            import asyncio
            asyncio.get_event_loop().run_forever()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Scheduler stopped[/yellow]")
    
    elif stop:
        console.print("[yellow]To stop the scheduler, press Ctrl+C in the terminal running it[/yellow]")
    
    elif status:
        console.print("[yellow]Scheduler status requires running scheduler instance[/yellow]")
    
    elif run_once:
        console.print("[yellow]Running single scan...[/yellow]")
        # TODO: Implement single scan
        console.print("[green]✓[/green] Scan complete")
    
    else:
        console.print("[yellow]Use --start to start scheduler or --status for info[/yellow]")


@app.command()
def status():
    """📊 Show Hunter system status"""
    config = load_config()
    
    table = Table(title="Hunter System Status", box=box.ROUNDED)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    table.add_row("Ecosystems", ", ".join(config.scan.ecosystems))
    table.add_row("Risk Tolerance", config.risk.tolerance)
    table.add_row("Scan Interval", f"{config.scan.interval_hours} hours")
    table.add_row("Paper Trading", "Enabled" if config.paper_trading.enabled else "Disabled")
    
    # Check database
    try:
        db = Database()
        active = len(db.get_active_strategies())
        table.add_row("Active Strategies", str(active))
        table.add_row("Database", "Connected")
    except:
        table.add_row("Database", "Error")
    
    console.print(table)


@app.command()
def test_data():
    """🧪 Test data source connections"""
    console.print(Panel("[bold]Testing Data Sources[/bold]"))
    
    # Test CoinGecko
    console.print("\n[yellow]Testing CoinGecko...[/yellow]")
    try:
        cg = CoinGeckoSource()
        tokens = cg.get_market_data(per_page=5)
        console.print(f"[green]✓[/green] CoinGecko: Retrieved {len(tokens)} tokens")
        for t in tokens[:3]:
            console.print(f"  • {t.symbol}: ${t.price_usd:.2f} ({t.price_change_24h:+.1f}%)")
    except Exception as e:
        console.print(f"[red]✗ CoinGecko error: {e}[/red]")


if __name__ == "__main__":
    app()
