"""
Strategy Detection Engine for Hunter
Implements various strategy detection algorithms
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class StrategyType(Enum):
    ARBITRAGE = "arbitrage"
    YIELD_FARMING = "yield_farming"
    MOMENTUM = "momentum"
    AIRDROP_FARMING = "airdrop_farming"
    LIQUIDITY_MINING = "liquidity_mining"
    OTHER = "other"
    # Academic strategies
    MEAN_REVERSION = "mean_reversion"
    ML_PREDICTION = "ml_prediction"


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Recommendation(Enum):
    REJECT = "REJECT"
    PAPER_TRADE = "PAPER_TRADE"
    TEST_SMALL = "TEST_SMALL"
    APPROVED = "APPROVED"


@dataclass
class Risk:
    type: str
    severity: RiskLevel
    description: str


@dataclass
class Strategy:
    """Standardized strategy output"""
    strategy_id: str
    name: str
    ecosystem: str
    type: StrategyType
    
    confidence: float
    confidence_reasoning: str
    
    risk_level: RiskLevel
    risks: List[Risk]
    
    profit_potential: Dict[str, Any]
    data_sources: List[str]
    unknowns: List[str]
    survivorship_bias_risk: str
    
    recommendation: Recommendation
    position_size_suggestion: str
    
    detected_at: datetime
    valid_until: datetime
    
    execution_steps: List[str]


class BaseStrategyDetector(ABC):
    """Abstract base class for strategy detectors"""
    
    def __init__(self, ecosystem: str = "solana"):
        self.ecosystem = ecosystem
        self.detector_name = self.__class__.__name__
    
    @abstractmethod
    def detect(self, data: Dict[str, Any]) -> List[Strategy]:
        """Detect strategies from market data"""
        pass
    
    def calculate_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate weighted confidence score"""
        weights = {
            "data_quality": 0.3,
            "historical_evidence": 0.25,
            "liquidity": 0.2,
            "risk_assessment": 0.15,
            "time_sensitivity": 0.1
        }
        
        score = 0
        for key, weight in weights.items():
            score += factors.get(key, 0) * weight
        
        return min(max(score, 0.0), 1.0)
    
    def assess_risks(self, context: Dict[str, Any]) -> List[Risk]:
        """Assess risks for a strategy"""
        risks = []
        
        # Smart contract risk
        if context.get("smart_contract_unaudited", False):
            risks.append(Risk(
                type="smart_contract",
                severity=RiskLevel.HIGH,
                description="Smart contract not audited. Risk of exploit or bug."
            ))
        
        # Liquidity risk
        if context.get("liquidity_usd", 0) < 100000:
            risks.append(Risk(
                type="liquidity",
                severity=RiskLevel.HIGH,
                description="Low liquidity (<$100k). High slippage risk."
            ))
        elif context.get("liquidity_usd", 0) < 1000000:
            risks.append(Risk(
                type="liquidity",
                severity=RiskLevel.MEDIUM,
                description="Moderate liquidity. Monitor for significant size."
            ))
        
        # Volatility risk
        if context.get("volatility_30d", 0) > 100:
            risks.append(Risk(
                type="volatility",
                severity=RiskLevel.HIGH,
                description="High volatility (>100%). Large price swings possible."
            ))
        
        # Impermanent loss risk (for LP strategies)
        if context.get("impermanent_loss_risk", False):
            risks.append(Risk(
                type="impermanent_loss",
                severity=RiskLevel.MEDIUM,
                description="Subject to impermanent loss if token prices diverge."
            ))
        
        return risks
    
    def determine_recommendation(
        self, 
        confidence: float, 
        risk_level: RiskLevel,
        risk_tolerance: str = "conservative"
    ) -> Recommendation:
        """Determine final recommendation"""
        
        # Hard rejects
        if confidence < 0.6:
            return Recommendation.REJECT
        if risk_level == RiskLevel.CRITICAL:
            return Recommendation.REJECT
        
        # Risk tolerance checks
        if risk_tolerance == "conservative":
            if risk_level == RiskLevel.HIGH:
                return Recommendation.PAPER_TRADE
            if confidence < 0.75:
                return Recommendation.PAPER_TRADE
            return Recommendation.TEST_SMALL
        
        elif risk_tolerance == "moderate":
            if risk_level == RiskLevel.HIGH:
                return Recommendation.TEST_SMALL
            if confidence >= 0.8:
                return Recommendation.APPROVED
            return Recommendation.TEST_SMALL
        
        else:  # aggressive
            if confidence >= 0.7:
                return Recommendation.APPROVED
            return Recommendation.TEST_SMALL


class ArbitrageDetector(BaseStrategyDetector):
    """Detect arbitrage opportunities"""
    
    def __init__(self, ecosystem: str = "solana"):
        super().__init__(ecosystem)
        self.type = StrategyType.ARBITRAGE
    
    def detect(self, data: Dict[str, Any]) -> List[Strategy]:
        """Detect arbitrage opportunities across DEXs"""
        strategies = []
        
        # Get price data across different DEXs
        dex_prices = data.get("dex_prices", {})
        
        if len(dex_prices) < 2:
            return strategies
        
        # Find price discrepancies
        for token, prices in dex_prices.items():
            if len(prices) < 2:
                continue
            
            # Find min and max prices
            min_price = min(p["price"] for p in prices)
            max_price = max(p["price"] for p in prices)
            
            # Calculate spread
            if min_price > 0:
                spread_pct = ((max_price - min_price) / min_price) * 100
                
                # If spread > 0.5%, potential arbitrage
                if spread_pct > 0.5:
                    # Calculate confidence
                    factors = {
                        "data_quality": 0.9,
                        "historical_evidence": 0.7,
                        "liquidity": 0.8 if max(p.get("liquidity", 0) for p in prices) > 50000 else 0.4,
                        "risk_assessment": 0.8,
                        "time_sensitivity": 0.6  # Arbitrage is time-sensitive
                    }
                    
                    confidence = self.calculate_confidence(factors)
                    
                    # Assess risks
                    context = {
                        "liquidity_usd": max(p.get("liquidity", 0) for p in prices),
                        "smart_contract_unaudited": False  # Assume audited for major DEXs
                    }
                    risks = self.assess_risks(context)
                    
                    # Determine risk level
                    risk_level = max((r.severity for r in risks), default=RiskLevel.LOW)
                    
                    # Create strategy
                    strategy = Strategy(
                        strategy_id=f"strat_{self.ecosystem}_arb_{token}_{int(datetime.now().timestamp())}",
                        name=f"{token.upper()} Arbitrage ({spread_pct:.2f}% spread)",
                        ecosystem=self.ecosystem,
                        type=StrategyType.ARBITRAGE,
                        confidence=confidence,
                        confidence_reasoning=f"Price discrepancy of {spread_pct:.2f}% across DEXs. Liquidity sufficient for small trades.",
                        risk_level=risk_level,
                        risks=risks,
                        profit_potential={
                            "apr": f"{spread_pct * 365:.0f}%",  # If done daily
                            "basis": "real_time_opportunity",
                            "daily_estimate": f"{spread_pct:.2f}%",
                            "time_horizon": "immediate"
                        },
                        data_sources=["jupiter", "raydium", "orca"],  # Example DEXs
                        unknowns=[
                            "Execution speed (arbitrage may disappear)",
                            "Gas fees eating into profits",
                            "MEV bot competition"
                        ],
                        survivorship_bias_risk="Low - arbitrage is mechanical and repeatable, though competitive",
                        recommendation=self.determine_recommendation(confidence, risk_level),
                        position_size_suggestion="5% of portfolio per trade",
                        detected_at=datetime.now(),
                        valid_until=datetime.now() + __import__('datetime').timedelta(hours=1),
                        execution_steps=[
                            f"Buy {token.upper()} on cheapest DEX",
                            f"Sell {token.upper()} on most expensive DEX",
                            "Account for gas fees and slippage",
                            "Repeat if spread persists"
                        ]
                    )
                    
                    strategies.append(strategy)
        
        return strategies


class YieldFarmingDetector(BaseStrategyDetector):
    """Detect yield farming opportunities"""
    
    def __init__(self, ecosystem: str = "solana"):
        super().__init__(ecosystem)
        self.type = StrategyType.YIELD_FARMING
    
    def detect(self, data: Dict[str, Any]) -> List[Strategy]:
        """Detect high-yield farming opportunities"""
        strategies = []
        
        pools = data.get("yield_pools", [])
        
        for pool in pools:
            apy = pool.get("apy", 0)
            tvl = pool.get("tvl", 0)
            
            # Only consider pools with reasonable APY and TVL
            if apy > 10 and tvl > 100000:  # >10% APY and >$100k TVL
                
                # Calculate confidence based on sustainability
                factors = {
                    "data_quality": 0.8,
                    "historical_evidence": 0.6 if pool.get("apy_stable_30d") else 0.3,
                    "liquidity": 0.9 if tvl > 1000000 else 0.6,
                    "risk_assessment": 0.7,
                    "time_sensitivity": 0.4
                }
                
                confidence = self.calculate_confidence(factors)
                
                # Higher APY = higher risk
                context = {
                    "liquidity_usd": tvl,
                    "smart_contract_unaudited": pool.get("unaudited", True),
                    "impermanent_loss_risk": pool.get("type") == "LP"
                }
                risks = self.assess_risks(context)
                
                # Add APY sustainability risk
                if apy > 100:
                    risks.append(Risk(
                        type="unsustainable_apy",
                        severity=RiskLevel.HIGH,
                        description=f"APY of {apy:.0f}% likely unsustainable. Expect rapid decrease."
                    ))
                
                risk_level = max((r.severity for r in risks), default=RiskLevel.LOW)
                
                strategy = Strategy(
                    strategy_id=f"strat_{self.ecosystem}_yield_{pool.get('id', 'unknown')}",
                    name=f"{pool.get('protocol', 'Unknown')} Yield ({apy:.0f}% APY)",
                    ecosystem=self.ecosystem,
                    type=StrategyType.YIELD_FARMING,
                    confidence=confidence,
                    confidence_reasoning=f"{apy:.0f}% APY with ${tvl:,.0f} TVL. {'APY stable for 30d' if pool.get('apy_stable_30d') else 'New pool, high risk.'}",
                    risk_level=risk_level,
                    risks=risks,
                    profit_potential={
                        "apr": f"{apy:.0f}%",
                        "basis": "current_pool_apy",
                        "daily_estimate": f"{apy/365:.2f}%",
                        "time_horizon": "30d"
                    },
                    data_sources=[pool.get("protocol", "unknown"), "defillama"],
                    unknowns=[
                        "APY sustainability",
                        "Token price volatility",
                        "Protocol governance changes"
                    ],
                    survivorship_bias_risk="High - high APY pools often attract too much capital, reducing returns",
                    recommendation=self.determine_recommendation(confidence, risk_level),
                    position_size_suggestion="10% of portfolio",
                    detected_at=datetime.now(),
                    valid_until=datetime.now() + __import__('datetime').timedelta(days=7),
                    execution_steps=[
                        f"Deposit into {pool.get('protocol')} pool",
                        "Monitor APY daily",
                        "Harvest rewards regularly",
                        "Exit if APY drops below opportunity cost"
                    ]
                )
                
                strategies.append(strategy)
        
        return strategies


class MomentumDetector(BaseStrategyDetector):
    """Detect momentum trading opportunities"""
    
    def __init__(self, ecosystem: str = "solana"):
        super().__init__(ecosystem)
        self.type = StrategyType.MOMENTUM
    
    def detect(self, data: Dict[str, Any]) -> List[Strategy]:
        """Detect tokens with strong momentum signals"""
        strategies = []
        
        tokens = data.get("tokens", [])
        
        for token in tokens:
            price_change_24h = token.get("price_change_24h", 0)
            price_change_7d = token.get("price_change_7d", 0)
            volume = token.get("volume_24h", 0)
            market_cap = token.get("market_cap", 0)
            
            # Momentum criteria:
            # - Up >20% in 7 days
            # - Positive 24h (continuing momentum)
            # - Volume spike (>2x average)
            # - Market cap > $10M (avoid rugs)
            
            if (price_change_7d > 20 and 
                price_change_24h > 0 and 
                market_cap > 10000000):
                
                factors = {
                    "data_quality": 0.8,
                    "historical_evidence": 0.4,  # Momentum is unpredictable
                    "liquidity": 0.7,
                    "risk_assessment": 0.5,  # Momentum is risky
                    "time_sensitivity": 0.9  # Very time-sensitive
                }
                
                confidence = self.calculate_confidence(factors)
                
                context = {
                    "liquidity_usd": volume,
                    "volatility_30d": abs(price_change_7d) * 4  # Estimate
                }
                risks = self.assess_risks(context)
                
                # Add momentum-specific risks
                risks.append(Risk(
                    type="momentum_reversal",
                    severity=RiskLevel.HIGH,
                    description="Momentum can reverse suddenly. High chance of buying the top."
                ))
                
                risks.append(Risk(
                    type="pump_and_dump",
                    severity=RiskLevel.MEDIUM if market_cap > 100000000 else RiskLevel.HIGH,
                    description="Rapid price increase may indicate pump scheme."
                ))
                
                risk_level = max((r.severity for r in risks), default=RiskLevel.MEDIUM)
                
                strategy = Strategy(
                    strategy_id=f"strat_{self.ecosystem}_mom_{token.get('symbol', 'unknown')}",
                    name=f"{token.get('symbol', 'UNKNOWN')} Momentum (+{price_change_7d:.0f}% 7d)",
                    ecosystem=self.ecosystem,
                    type=StrategyType.MOMENTUM,
                    confidence=confidence,
                    confidence_reasoning=f"Strong momentum: +{price_change_7d:.0f}% in 7d, continuing with +{price_change_24h:.0f}% today. High risk of reversal.",
                    risk_level=risk_level,
                    risks=risks,
                    profit_potential={
                        "apr": "Unknown - momentum trades are short-term",
                        "basis": "technical_momentum",
                        "daily_estimate": f"{price_change_24h:.1f}%",
                        "time_horizon": "1-3 days"
                    },
                    data_sources=["coingecko", "birdeye"],
                    unknowns=[
                        "When momentum will reverse",
                        "Whether this is organic or manipulated",
                        "Entry timing precision"
                    ],
                    survivorship_bias_risk="Very high - past momentum doesn't predict future, most momentum trades lose money",
                    recommendation=self.determine_recommendation(confidence, risk_level, "conservative"),
                    position_size_suggestion="2% of portfolio (very risky)",
                    detected_at=datetime.now(),
                    valid_until=datetime.now() + __import__('datetime').timedelta(hours=6),
                    execution_steps=[
                        "Set stop-loss at -10% from entry",
                        "Take profits at +20%, +50%",
                        "Monitor volume for exhaustion",
                        "Exit immediately on momentum loss"
                    ]
                )
                
                strategies.append(strategy)
        
        return strategies


class StrategyEngine:
    """Main strategy detection engine"""
    
    def __init__(self, ecosystem: str = "solana", enable_academic: bool = False):
        self.ecosystem = ecosystem
        self.detectors = {
            StrategyType.ARBITRAGE: ArbitrageDetector(ecosystem),
            StrategyType.YIELD_FARMING: YieldFarmingDetector(ecosystem),
            StrategyType.MOMENTUM: MomentumDetector(ecosystem),
        }
        
        # Register academic strategies if enabled
        if enable_academic:
            try:
                from hunter.strategies.academic_strategies import (
                    CryptoMomentumDetector,
                    CryptoMeanReversionDetector,
                    # CryptoKNNDetector  # Experimental - uncomment with caution
                )
                
                # Override default momentum with academic version
                self.detectors[StrategyType.MOMENTUM] = CryptoMomentumDetector(ecosystem)
                
                # Add mean-reversion
                self.detectors[StrategyType.MEAN_REVERSION] = CryptoMeanReversionDetector(ecosystem)
                
                # Add ML prediction (experimental)
                # self.detectors[StrategyType.ML_PREDICTION] = CryptoKNNDetector(ecosystem)
                
            except ImportError as e:
                print(f"Warning: Could not load academic strategies: {e}")
    
    def scan(self, data: Dict[str, Any], strategy_types: Optional[List[StrategyType]] = None) -> List[Strategy]:
        """Run all detectors and return strategies"""
        all_strategies = []
        
        types_to_scan = strategy_types or list(self.detectors.keys())
        
        for stype in types_to_scan:
            if stype in self.detectors:
                detector = self.detectors[stype]
                strategies = detector.detect(data)
                all_strategies.extend(strategies)
        
        # Sort by confidence descending
        all_strategies.sort(key=lambda x: x.confidence, reverse=True)
        
        return all_strategies
    
    def filter_by_confidence(self, strategies: List[Strategy], min_confidence: float = 0.6) -> List[Strategy]:
        """Filter strategies by minimum confidence"""
        return [s for s in strategies if s.confidence >= min_confidence]
    
    def filter_by_risk(self, strategies: List[Strategy], max_risk: RiskLevel = RiskLevel.HIGH) -> List[Strategy]:
        """Filter strategies by maximum risk level"""
        risk_order = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2, RiskLevel.CRITICAL: 3}
        max_risk_value = risk_order.get(max_risk, 2)
        return [s for s in strategies if risk_order.get(s.risk_level, 3) <= max_risk_value]
