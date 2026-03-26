"""
Data Sources Module for Hunter
Integrates with DeFiLlama, CoinGecko, and Solana RPC
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import time
from datetime import datetime, timedelta

import requests
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class TokenData:
    """Standardized token data structure"""
    symbol: str
    name: str
    price_usd: float
    market_cap: float
    volume_24h: float
    price_change_24h: float
    price_change_7d: float
    liquidity_usd: float
    timestamp: datetime
    source: str


@dataclass
class ProtocolData:
    """DeFi protocol data"""
    name: str
    tvl: float
    chain: str
    category: str
    apy: Optional[float]
    timestamp: datetime


@dataclass
class PoolData:
    """Liquidity pool data"""
    pool_id: str
    token_a: str
    token_b: str
    tvl: float
    volume_24h: float
    apy: float
    fee_apr: float
    impermanent_loss_24h: float
    dex: str
    timestamp: datetime


class BaseDataSource(ABC):
    """Abstract base class for data sources"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # seconds
    
    def _rate_limit(self):
        """Simple rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    @abstractmethod
    def get_token_data(self, symbol: str) -> Optional[TokenData]:
        pass
    
    @abstractmethod
    def get_top_pools(self, chain: str, limit: int = 10) -> List[PoolData]:
        pass
    
    @abstractmethod
    def get_protocol_tvl(self, protocol: str) -> Optional[ProtocolData]:
        pass


class DeFiLlamaSource(BaseDataSource):
    """DeFiLlama API integration - Free tier"""
    
    BASE_URL = "https://api.llama.fi"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_protocol_tvl(self, protocol: str) -> Optional[ProtocolData]:
        """Get TVL data for a protocol"""
        self._rate_limit()
        
        try:
            response = self.session.get(f"{self.BASE_URL}/protocol/{protocol}")
            response.raise_for_status()
            data = response.json()
            
            return ProtocolData(
                name=data.get("name", protocol),
                tvl=data.get("tvl", 0),
                chain=data.get("chain", "unknown"),
                category=data.get("category", "unknown"),
                apy=None,  # DeFiLlama doesn't provide APY directly
                timestamp=datetime.now()
            )
        except Exception as e:
            print(f"DeFiLlama error: {e}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_chain_tvl(self, chain: str) -> float:
        """Get total TVL for a chain"""
        self._rate_limit()
        
        try:
            response = self.session.get(f"{self.BASE_URL}/charts/{chain}")
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return data[-1].get("totalLiquidityUSD", 0)
            return 0
        except Exception as e:
            print(f"DeFiLlama chain error: {e}")
            return 0
    
    def get_token_data(self, symbol: str) -> Optional[TokenData]:
        """DeFiLlama doesn't have token price data"""
        return None
    
    def get_top_pools(self, chain: str, limit: int = 10) -> List[PoolData]:
        """DeFiLlama doesn't have pool-level data"""
        return []


class CoinGeckoSource(BaseDataSource):
    """CoinGecko API integration - Free tier"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.rate_limit_delay = 1.2  # CoinGecko has stricter rate limits
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_token_data(self, symbol: str) -> Optional[TokenData]:
        """Get token data from CoinGecko"""
        self._rate_limit()
        
        try:
            # First, search for coin ID
            search_response = self.session.get(
                f"{self.BASE_URL}/search",
                params={"query": symbol}
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            
            coins = search_data.get("coins", [])
            if not coins:
                return None
            
            # Get the first match
            coin_id = coins[0].get("id")
            
            # Get detailed data
            self._rate_limit()
            response = self.session.get(
                f"{self.BASE_URL}/coins/{coin_id}",
                params={
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "true",
                    "community_data": "false",
                    "developer_data": "false"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            market_data = data.get("market_data", {})
            
            return TokenData(
                symbol=symbol.upper(),
                name=data.get("name", symbol),
                price_usd=market_data.get("current_price", {}).get("usd", 0),
                market_cap=market_data.get("market_cap", {}).get("usd", 0),
                volume_24h=market_data.get("total_volume", {}).get("usd", 0),
                price_change_24h=market_data.get("price_change_percentage_24h", 0),
                price_change_7d=market_data.get("price_change_percentage_7d", 0),
                liquidity_usd=0,  # Not available in free tier
                timestamp=datetime.now(),
                source="coingecko"
            )
        except Exception as e:
            print(f"CoinGecko error: {e}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_market_data(self, vs_currency: str = "usd", per_page: int = 100) -> List[TokenData]:
        """Get top tokens by market cap"""
        self._rate_limit()
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/coins/markets",
                params={
                    "vs_currency": vs_currency,
                    "order": "market_cap_desc",
                    "per_page": per_page,
                    "page": 1,
                    "sparkline": "false"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            tokens = []
            for item in data:
                tokens.append(TokenData(
                    symbol=item.get("symbol", "").upper(),
                    name=item.get("name", ""),
                    price_usd=item.get("current_price", 0),
                    market_cap=item.get("market_cap", 0),
                    volume_24h=item.get("total_volume", 0),
                    price_change_24h=item.get("price_change_percentage_24h", 0),
                    price_change_7d=item.get("price_change_percentage_7d_in_currency", 0),
                    liquidity_usd=0,
                    timestamp=datetime.now(),
                    source="coingecko"
                ))
            return tokens
        except Exception as e:
            print(f"CoinGecko market error: {e}")
            return []
    
    def get_top_pools(self, chain: str, limit: int = 10) -> List[PoolData]:
        """CoinGecko free tier doesn't have pool data"""
        return []
    
    def get_protocol_tvl(self, protocol: str) -> Optional[ProtocolData]:
        """CoinGecko doesn't have protocol TVL"""
        return None


class DataAggregator:
    """Aggregates data from multiple sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.sources = {}
        
        # Initialize DeFiLlama (always available - free)
        self.sources["defillama"] = DeFiLlamaSource()
        
        # Initialize CoinGecko (always available - free)
        self.sources["coingecko"] = CoinGeckoSource()
    
    def get_token_data(self, symbol: str) -> Optional[TokenData]:
        """Get token data from best available source"""
        # Try CoinGecko first
        data = self.sources["coingecko"].get_token_data(symbol)
        if data:
            return data
        
        return None
    
    def get_solana_ecosystem_data(self) -> Dict[str, Any]:
        """Get comprehensive Solana ecosystem data"""
        defillama = self.sources["defillama"]
        
        return {
            "chain_tvl": defillama.get_chain_tvl("solana"),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_market_overview(self) -> List[TokenData]:
        """Get top tokens overview"""
        return self.sources["coingecko"].get_market_data(per_page=50)
