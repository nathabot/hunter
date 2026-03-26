"""
Trading Strategies from "151 Trading Strategies" (Kakushadze & Serur)
Implemented for Hunter AI Agent - Crypto Edition

Reference: SSRN 3247865
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from collections import deque

from hunter.strategies.engine import (
    BaseStrategyDetector, Strategy, StrategyType,
    RiskLevel, Risk, Recommendation
)


# ============================================================================
# SECTION 3.1: PRICE MOMENTUM (Jegadeesh & Titman, 1993)
# ============================================================================

@dataclass
class MomentumConfig:
    """Configuration for momentum strategy"""
    lookback_period: int = 12  # 12-month equivalent (in days for crypto)
    skip_period: int = 1       # 1-month skip (momentum crash protection)
    holding_period: int = 1    # Rebalance frequency
    top_percentile: float = 0.1  # Top 10%
    bottom_percentile: float = 0.1  # Bottom 10% (for short)


class CryptoMomentumDetector(BaseStrategyDetector):
    """
    Classic price momentum adapted for crypto markets.
    
    From Paper Section 3.1:
    "Rank stocks by past return R_i(t-12,t-1), go long top decile,
    short bottom decile"
    
    Crypto Adaptation:
    - Shorter lookback (12 days vs 12 months) due to crypto volatility
    - Skip period to avoid momentum crashes
    - Volatility-adjusted position sizing
    """
    
    def __init__(self, ecosystem: str = "solana", config: MomentumConfig = None):
        super().__init__(ecosystem)
        self.type = StrategyType.MOMENTUM
        self.config = config or MomentumConfig()
    
    def calculate_momentum(self, prices: List[float], volumes: List[float] = None) -> Dict[str, float]:
        """
        Calculate momentum score with volatility adjustment.
        
        Formula: Momentum = (P_t - P_{t-n}) / P_{t-n} / volatility
        
        Returns:
            momentum_score: Risk-adjusted momentum
            raw_return: Simple return over lookback period
            volatility: Annualized volatility
        """
        if len(prices) < self.config.lookback_period + self.config.skip_period:
            return {"momentum_score": 0, "raw_return": 0, "volatility": 1}
        
        # Skip recent period (momentum crash protection)
        recent_price = prices[-(self.config.skip_period + 1)]
        past_price = prices[-(self.config.lookback_period + self.config.skip_period)]
        
        # Raw return
        raw_return = (recent_price - past_price) / past_price
        
        # Calculate volatility (standard deviation of returns)
        returns = [(prices[i] - prices[i-1]) / prices[i-1] 
                   for i in range(-self.config.lookback_period, 0)]
        volatility = np.std(returns) * np.sqrt(365)  # Annualized
        
        # Volatility-adjusted momentum (Sharpe-like)
        momentum_score = raw_return / (volatility + 1e-8)  # Avoid div by zero
        
        return {
            "momentum_score": momentum_score,
            "raw_return": raw_return,
            "volatility": volatility
        }
    
    def detect(self, data: Dict[str, Any]) -> List[Strategy]:
        """
        Detect momentum opportunities across multiple tokens.
        
        Paper Logic:
        1. Calculate momentum for all assets
        2. Rank by momentum score
        3. Long top decile, short bottom decile
        """
        strategies = []
        tokens_data = data.get("tokens", [])
        
        # Calculate momentum for all tokens
        momentum_scores = []
        for token_data in tokens_data:
            symbol = token_data.get("symbol", "UNKNOWN")
            prices = token_data.get("prices", [])
            
            if len(prices) < self.config.lookback_period + 5:
                continue
            
            metrics = self.calculate_momentum(prices)
            momentum_scores.append({
                "symbol": symbol,
                **metrics,
                "current_price": prices[-1] if prices else 0
            })
        
        if not momentum_scores:
            return strategies
        
        # Rank by momentum score
        momentum_scores.sort(key=lambda x: x["momentum_score"], reverse=True)
        
        # Top performers (LONG candidates)
        top_n = max(1, int(len(momentum_scores) * self.config.top_percentile))
        top_tokens = momentum_scores[:top_n]
        
        # Bottom performers (SHORT candidates)
        bottom_n = max(1, int(len(momentum_scores) * self.config.bottom_percentile))
        bottom_tokens = momentum_scores[-bottom_n:]
        
        # Generate LONG signals for top momentum
        for token in top_tokens:
            if token["momentum_score"] <= 0:  # Only positive momentum
                continue
            
            factors = {
                "data_quality": 0.8,
                "historical_evidence": 0.7,  # Momentum well-documented
                "liquidity": 0.6,
                "risk_assessment": 0.6,
                "time_sensitivity": 0.7
            }
            
            confidence = self.calculate_confidence(factors)
            
            context = {
                "liquidity_usd": 1000000,  # Placeholder
                "volatility_annual": token["volatility"]
            }
            risks = self.assess_risks(context)
            
            # Add momentum-specific risks
            risks.append(Risk(
                type="momentum_crash",
                severity=RiskLevel.HIGH,
                description="Momentum strategies can experience sudden crashes. Skip period helps but doesn't eliminate risk."
            ))
            
            risks.append(Risk(
                type="volatility_regime_change",
                severity=RiskLevel.MEDIUM,
                description="Crypto volatility can change rapidly, invalidating momentum signals."
            ))
            
            strategy = Strategy(
                strategy_id=f"strat_{self.ecosystem}_momentum_{token['symbol']}",
                name=f"{token['symbol']} Momentum (Score: {token['momentum_score']:.2f})",
                ecosystem=self.ecosystem,
                type=StrategyType.MOMENTUM,
                confidence=confidence,
                confidence_reasoning=f"Momentum score: {token['momentum_score']:.2f}, Raw return: {token['raw_return']:.1%}, Volatility: {token['volatility']:.1%}. Ranked top {self.config.top_percentile:.0%} in universe.",
                risk_level=RiskLevel.HIGH,  # Momentum is inherently risky
                risks=risks,
                profit_potential={
                    "apr": f"{(token['momentum_score'] * 100):.0f}% (theoretical)",
                    "basis": "academic_momentum",
                    "daily_estimate": f"{token['momentum_score'] / 365:.2%}",
                    "time_horizon": f"{self.config.holding_period} day(s)"
                },
                data_sources=["coingecko", "birdeye"],
                unknowns=[
                    "Whether momentum will continue or reverse",
                    "Impact of broader market sentiment",
                    "Whale manipulation potential"
                ],
                survivorship_bias_risk="High - past momentum winners don't guarantee future performance, especially in crypto bear markets",
                recommendation=Recommendation.PAPER_TRADE,  # Momentum is risky
                position_size_suggestion="3% of portfolio (momentum is volatile)",
                detected_at=datetime.now(),
                valid_until=datetime.now() + timedelta(days=self.config.holding_period),
                execution_steps=[
                    f"Check {token['symbol']} recent price action",
                    "Verify volume supports the move",
                    f"Enter LONG at {token['current_price']}",
                    f"Set stop-loss at {token['current_price'] * 0.95:.4f} (5% below entry)",
                    f"Hold for {self.config.holding_period} day(s)",
                    "Reassess momentum after holding period"
                ]
            )
            
            strategies.append(strategy)
        
        return strategies


# ============================================================================
# SECTION 3.9: MEAN-REVERSION (Ornstein-Uhlenbeck Process)
# ============================================================================

@dataclass
class MeanReversionConfig:
    """Configuration for mean-reversion strategy"""
    lookback_period: int = 20  # Lookback for mean calculation
    entry_zscore: float = 2.0  # Enter when |z-score| > 2
    exit_zscore: float = 0.5   # Exit when |z-score| < 0.5
    max_holding_days: int = 5  # Force exit after N days


class CryptoMeanReversionDetector(BaseStrategyDetector):
    """
    Mean-reversion strategy using Ornstein-Uhlenbeck framework.
    
    From Paper Section 3.9:
    dX_t = θ(μ - X_t)dt + σdW_t
    Half-life: t_{1/2} = ln(2)/θ
    
    Crypto Adaptation:
    - Z-score based entry/exit
    - Shorter holding periods (crypto mean-reverts faster)
    - Volatility regime filtering
    """
    
    def __init__(self, ecosystem: str = "solana", config: MeanReversionConfig = None):
        super().__init__(ecosystem)
        self.type = StrategyType.MOMENTUM  # Would add MEAN_REVERSION to enum
        self.config = config or MeanReversionConfig()
    
    def calculate_zscore(self, prices: List[float]) -> Dict[str, float]:
        """
        Calculate Z-score for mean-reversion signal.
        
        Z = (Price - Mean) / StdDev
        
        High positive Z = potential SHORT (overbought)
        High negative Z = potential LONG (oversold)
        """
        if len(prices) < self.config.lookback_period:
            return {"zscore": 0, "mean": 0, "std": 1, "half_life": 999}
        
        recent_prices = prices[-self.config.lookback_period:]
        mean = np.mean(recent_prices)
        std = np.std(recent_prices)
        current = prices[-1]
        
        zscore = (current - mean) / (std + 1e-8)
        
        # Estimate half-life using OLS (simplified)
        # In practice, would do: Δy_t = α + βy_{t-1} + ε_t
        # Then θ = -ln(1+β)/Δt
        returns = np.diff(recent_prices) / recent_prices[:-1]
        if len(returns) > 1 and np.var(returns) > 0:
            # Simplified half-life estimate
            half_life = np.log(2) / (np.abs(np.mean(returns)) + 0.01)
        else:
            half_life = 999
        
        return {
            "zscore": zscore,
            "mean": mean,
            "std": std,
            "half_life": half_life,
            "current": current
        }
    
    def detect(self, data: Dict[str, Any]) -> List[Strategy]:
        """Detect mean-reversion opportunities."""
        strategies = []
        tokens_data = data.get("tokens", [])
        
        for token_data in tokens_data:
            symbol = token_data.get("symbol", "UNKNOWN")
            prices = token_data.get("prices", [])
            
            if len(prices) < self.config.lookback_period + 5:
                continue
            
            metrics = self.calculate_zscore(prices)
            zscore = metrics["zscore"]
            
            # Skip if z-score not extreme enough
            if abs(zscore) < self.config.entry_zscore:
                continue
            
            # Determine direction
            if zscore > 0:
                direction = "SHORT"  # Overbought, expect reversion down
                signal_type = "mean_reversion_short"
            else:
                direction = "LONG"   # Oversold, expect reversion up
                signal_type = "mean_reversion_long"
            
            factors = {
                "data_quality": 0.7,
                "historical_evidence": 0.6,
                "liquidity": 0.6,
                "risk_assessment": 0.5,
                "time_sensitivity": 0.8  # Mean-reversion is time-sensitive
            }
            
            confidence = self.calculate_confidence(factors)
            
            context = {
                "liquidity_usd": 1000000,
                "volatility_annual": metrics["std"] / metrics["mean"] * np.sqrt(365) if metrics["mean"] > 0 else 1
            }
            risks = self.assess_risks(context)
            
            risks.append(Risk(
                type="trend_continuation",
                severity=RiskLevel.HIGH,
                description=f"Price may continue {direction.lower()}ing rather than reverting. Z-score: {zscore:.2f}"
            ))
            
            risks.append(Risk(
                type="half_life_uncertainty",
                severity=RiskLevel.MEDIUM,
                description=f"Estimated half-life: {metrics['half_life']:.1f} periods. Mean-reversion may take longer than expected."
            ))
            
            entry_price = metrics["current"]
            target_price = metrics["mean"]  # Target is the mean
            
            strategy = Strategy(
                strategy_id=f"strat_{self.ecosystem}_mr_{symbol}",
                name=f"{symbol} Mean-Reversion ({direction}, Z={zscore:.2f})",
                ecosystem=self.ecosystem,
                type=StrategyType.MOMENTUM,  # Would be MEAN_REVERSION
                confidence=confidence,
                confidence_reasoning=f"Z-score: {zscore:.2f} (entry threshold: ±{self.config.entry_zscore}). Mean: {metrics['mean']:.4f}, Current: {entry_price:.4f}. Half-life estimate: {metrics['half_life']:.1f} periods.",
                risk_level=RiskLevel.HIGH,
                risks=risks,
                profit_potential={
                    "apr": f"{(abs(target_price - entry_price) / entry_price * 100):.1f}% per trade",
                    "basis": "mean_reversion_ou_process",
                    "daily_estimate": f"{(abs(zscore) * 0.5):.1f}% (estimate)",
                    "time_horizon": f"{min(int(metrics['half_life']), self.config.max_holding_days)} days"
                },
                data_sources=["coingecko"],
                unknowns=[
                    "Whether mean-reversion will occur",
                    "Actual half-life vs estimate",
                    "Impact of market regime change"
                ],
                survivorship_bias_risk="Medium - mean-reversion works until it doesn't (trending markets)",
                recommendation=Recommendation.PAPER_TRADE,
                position_size_suggestion="2% of portfolio (mean-reversion has high failure rate)",
                detected_at=datetime.now(),
                valid_until=datetime.now() + timedelta(days=self.config.max_holding_days),
                execution_steps=[
                    f"Verify {symbol} is not in strong trend (check higher timeframes)",
                    f"Enter {direction} at {entry_price:.4f}",
                    f"Target: {target_price:.4f} (mean)",
                    f"Stop-loss: {entry_price * 1.1 if direction == 'SHORT' else entry_price * 0.9:.4f}",
                    f"Exit if Z-score < {self.config.exit_zscore}",
                    f"Force exit after {self.config.max_holding_days} days"
                ]
            )
            
            strategies.append(strategy)
        
        return strategies


# ============================================================================
# SECTION 3.17: MACHINE LEARNING - KNN
# ============================================================================

@dataclass
class KNNConfig:
    """Configuration for KNN strategy"""
    k: int = 5                    # Number of neighbors
    lookback: int = 30            # Lookback window for features
    feature_window: int = 5       # Window for feature calculation
    min_samples: int = 100        # Minimum samples needed


class CryptoKNNDetector(BaseStrategyDetector):
    """
    k-Nearest Neighbors strategy for price prediction.
    
    From Paper Section 3.17:
    "k-nearest neighbors for predicting stock returns
    Features: technical indicators, market microstructure
    Distance metric: Euclidean or Mahalanobis"
    
    Features used:
    - Returns (various windows)
    - Volatility
    - Volume change
    - Price vs moving averages
    """
    
    def __init__(self, ecosystem: str = "solana", config: KNNConfig = None):
        super().__init__(ecosystem)
        self.type = StrategyType.OTHER  # ML strategy
        self.config = config or KNNConfig()
        self.memory = deque(maxlen=self.config.min_samples)  # Store historical patterns
    
    def calculate_features(self, prices: List[float], volumes: List[float]) -> List[float]:
        """
        Calculate feature vector for KNN.
        
        Features:
        1. 1-period return
        2. 5-period return
        3. 10-period return
        4. Volatility (std of returns)
        5. Price vs MA5 ratio
        6. Price vs MA20 ratio
        7. Volume change
        """
        if len(prices) < 20 or len(volumes) < 2:
            return []
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        features = [
            returns[-1] if len(returns) >= 1 else 0,  # 1-period return
            sum(returns[-5:]) if len(returns) >= 5 else 0,  # 5-period return
            sum(returns[-10:]) if len(returns) >= 10 else 0,  # 10-period return
            np.std(returns[-10:]) if len(returns) >= 10 else 0,  # Volatility
            prices[-1] / np.mean(prices[-5:]) - 1 if len(prices) >= 5 else 0,  # MA5 ratio
            prices[-1] / np.mean(prices[-20:]) - 1 if len(prices) >= 20 else 0,  # MA20 ratio
            (volumes[-1] - volumes[-2]) / volumes[-2] if len(volumes) >= 2 else 0  # Volume change
        ]
        
        return features
    
    def knn_predict(self, current_features: List[float], historical: List[Tuple[List[float], float]]) -> Dict[str, float]:
        """
        KNN prediction.
        
        Returns predicted return and confidence.
        """
        if len(historical) < self.config.k:
            return {"prediction": 0, "confidence": 0, "neighbors": 0}
        
        # Calculate Euclidean distances
        distances = []
        for features, outcome in historical:
            if len(features) == len(current_features):
                dist = np.sqrt(sum((a - b) ** 2 for a, b in zip(current_features, features)))
                distances.append((dist, outcome))
        
        if not distances:
            return {"prediction": 0, "confidence": 0, "neighbors": 0}
        
        # Sort by distance and take k nearest
        distances.sort(key=lambda x: x[0])
        k_nearest = distances[:self.config.k]
        
        # Weighted prediction (closer neighbors have more weight)
        weights = [1 / (d[0] + 1e-8) for d in k_nearest]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return {"prediction": 0, "confidence": 0, "neighbors": 0}
        
        weighted_prediction = sum(w * o for w, (d, o) in zip(weights, k_nearest)) / total_weight
        
        # Confidence based on agreement of neighbors
        outcomes = [o for _, o in k_nearest]
        agreement = np.std(outcomes)
        confidence = 1 / (1 + agreement)  # Lower variance = higher confidence
        
        return {
            "prediction": weighted_prediction,
            "confidence": confidence,
            "neighbors": len(k_nearest)
        }
    
    def detect(self, data: Dict[str, Any]) -> List[Strategy]:
        """Detect opportunities using KNN prediction."""
        strategies = []
        tokens_data = data.get("tokens", [])
        
        # Build historical database (in practice, load from DB)
        for token_data in tokens_data:
            symbol = token_data.get("symbol", "UNKNOWN")
            prices = token_data.get("prices", [])
            volumes = token_data.get("volumes", [])
            
            if len(prices) < self.config.lookback + 10:
                continue
            
            # Build historical patterns (sliding window)
            historical = []
            for i in range(self.config.lookback, len(prices) - 1):
                past_prices = prices[i-self.config.lookback:i]
                past_volumes = volumes[i-self.config.lookback:i] if i < len(volumes) else [1]*len(past_prices)
                features = self.calculate_features(past_prices, past_volumes)
                
                # Outcome is next-period return
                outcome = (prices[i] - prices[i-1]) / prices[i-1]
                
                if features:
                    historical.append((features, outcome))
            
            # Get current features
            current_features = self.calculate_features(prices, volumes)
            if not current_features:
                continue
            
            # Predict
            prediction = self.knn_predict(current_features, historical)
            
            # Generate signal if confidence is high enough
            if prediction["confidence"] > 0.5 and abs(prediction["prediction"]) > 0.01:
                direction = "LONG" if prediction["prediction"] > 0 else "SHORT"
                
                factors = {
                    "data_quality": 0.6,
                    "historical_evidence": 0.5,  # ML backtest required
                    "liquidity": 0.6,
                    "risk_assessment": 0.4,
                    "time_sensitivity": 0.7
                }
                
                confidence = self.calculate_confidence(factors) * prediction["confidence"]
                
                context = {"liquidity_usd": 1000000}
                risks = self.assess_risks(context)
                
                risks.append(Risk(
                    type="ml_overfitting",
                    severity=RiskLevel.HIGH,
                    description="KNN may overfit to historical patterns that don't repeat."
                ))
                
                risks.append(Risk(
                    type="feature_staleness",
                    severity=RiskLevel.MEDIUM,
                    description="Features may become stale in rapidly changing markets."
                ))
                
                strategy = Strategy(
                    strategy_id=f"strat_{self.ecosystem}_knn_{symbol}",
                    name=f"{symbol} KNN Prediction ({direction}, conf={prediction['confidence']:.2f})",
                    ecosystem=self.ecosystem,
                    type=StrategyType.OTHER,
                    confidence=confidence,
                    confidence_reasoning=f"KNN prediction: {prediction['prediction']:.2%} return expected. Confidence: {prediction['confidence']:.2f}. Based on {prediction['neighbors']} neighbors.",
                    risk_level=RiskLevel.HIGH,
                    risks=risks,
                    profit_potential={
                        "apr": f"{(prediction['prediction'] * 365 * 100):.0f}% (theoretical)",
                        "basis": "knn_machine_learning",
                        "daily_estimate": f"{prediction['prediction']:.2%}",
                        "time_horizon": "1 day"
                    },
                    data_sources=["coingecko", "on_chain"],
                    unknowns=[
                        "Model accuracy on out-of-sample data",
                        "Whether historical patterns repeat",
                        "Optimal k value for current regime"
                    ],
                    survivorship_bias_risk="Very high - ML models often fail on unseen data",
                    recommendation=Recommendation.REJECT,  # ML requires extensive backtesting first
                    position_size_suggestion="1% of portfolio (ML is experimental)",
                    detected_at=datetime.now(),
                    valid_until=datetime.now() + timedelta(hours=1),
                    execution_steps=[
                        f"Paper trade only - KNN needs extensive backtesting",
                        "Log prediction vs actual outcome",
                        "Retrain model weekly with new data",
                        "Monitor for overfitting",
                        f"Prediction: {prediction['prediction']:.2%} next-period return"
                    ]
                )
                
                strategies.append(strategy)
        
        return strategies


# ============================================================================
# STRATEGY REGISTRY - Add to hunter/strategies/advanced.py
# ============================================================================

STRATEGY_REGISTRY = {
    "crypto_momentum": CryptoMomentumDetector,
    "crypto_mean_reversion": CryptoMeanReversionDetector,
    "crypto_knn": CryptoKNNDetector
}

"""
IMPLEMENTATION NOTES:

1. Add these strategies to hunter/strategies/advanced.py
2. Register in StrategyEngine.__init__()
3. Add to config.yaml strategy_types:
   - crypto_momentum
   - crypto_mean_reversion
   - crypto_knn

4. For production use:
   - KNN requires extensive backtesting (currently marked REJECT)
   - Mean-reversion needs regime detection (trending vs ranging)
   - Momentum needs volatility scaling

5. References:
   - Momentum: Jegadeesh & Titman (1993)
   - Mean-Reversion: Ornstein-Uhlenbeck process
   - KNN: Section 3.17, 151 Trading Strategies
"""
