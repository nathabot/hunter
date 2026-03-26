"""
Hunter Logging System
Structured JSON logging for machine parsing
"""
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

# Create console for rich output
console = Console()

LOG_FORMAT = "%(message)s"
DATE_FORMAT = "[%X]"


def setup_logging(verbose: bool = False):
    """Setup logging with rich formatting"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory
    log_dir = Path.home() / ".hunter" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup rich handler for console
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=verbose,
    )
    rich_handler.setLevel(level)
    
    # Setup file handler
    file_handler = logging.FileHandler(log_dir / "hunter.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[rich_handler, file_handler]
    )
    
    return logging.getLogger("hunter")
