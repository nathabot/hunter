"""
Hunter Configuration System
Pydantic-based config with YAML persistence
"""
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


DEFAULT_CONFIG_PATH = Path.home() / ".hunter" / "config.yaml"


class ScanConfig(BaseModel):
    """Scanning configuration"""
    interval_hours: int = Field(default=4, ge=1, le=24)
    ecosystems: List[str] = Field(default=["solana"])
    strategy_types: List[str] = Field(default=[
        "arbitrage",
        "yield_farming",
        "momentum",
        "airdrop_farming"
    ])


class RiskConfig(BaseModel):
    """Risk tolerance configuration"""
    tolerance: str = Field(default="conservative", pattern="^(conservative|moderate|aggressive)$")
    max_position_size_pct: float = Field(default=5.0, ge=1.0, le=50.0)
    min_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class APIConfig(BaseModel):
    """API keys configuration"""
    # Free tier APIs (no key required)
    defillama: str = Field(default="free")
    coingecko: str = Field(default="free")
    
    # Paid tier APIs (optional)
    birdeye: Optional[str] = Field(default=None)
    helius: Optional[str] = Field(default=None)
    twitter_bearer: Optional[str] = Field(default=None)


class TelegramConfig(BaseModel):
    """Telegram bot configuration"""
    bot_token: Optional[str] = Field(default=None)
    alert_min_confidence: float = Field(default=0.75, ge=0.0, le=1.0)
    alert_min_profit_apr: str = Field(default="10%")


class PaperTradingConfig(BaseModel):
    """Paper trading configuration"""
    enabled: bool = Field(default=True)
    initial_balance_usd: float = Field(default=10000.0)
    max_position_size_usd: float = Field(default=1000.0)
    track_pnl: bool = Field(default=True)


class HunterConfig(BaseModel):
    """Main Hunter configuration"""
    scan: ScanConfig = Field(default_factory=ScanConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    apis: APIConfig = Field(default_factory=APIConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    paper_trading: PaperTradingConfig = Field(default_factory=PaperTradingConfig)
    
    class Config:
        validate_assignment = True


def load_config(config_path: Optional[Path] = None) -> HunterConfig:
    """Load configuration from YAML file"""
    path = config_path or DEFAULT_CONFIG_PATH
    
    if path.exists():
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return HunterConfig(**data)
    else:
        # Return default config
        return HunterConfig()


def save_config(config: HunterConfig, config_path: Optional[Path] = None):
    """Save configuration to YAML file"""
    path = config_path or DEFAULT_CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False)


def create_default_config():
    """Create default configuration file"""
    config = HunterConfig()
    save_config(config)
    return DEFAULT_CONFIG_PATH
