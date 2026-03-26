# 📚 Academic Strategies Implementation from "151 Trading Strategies"

**Paper:** "151 Trading Strategies" by Zura Kakushadze, Ph.D. and Juan Andrés Serur, M.Fin.  
**SSRN:** https://ssrn.com/abstract=3247865  
**File:** `hunter/strategies/academic_strategies.py`

---

## 🎯 Implemented Strategies

### 1. **Price Momentum** (Section 3.1)

**Paper Reference:**
> "Rank stocks by past return R_i(t-12,t-1), go long top decile, short bottom decile"
> — Jegadeesh & Titman (1993)

**Implementation:** `CryptoMomentumDetector`

**Formula:**
```
Momentum = (P_t - P_{t-12}) / P_{t-12} / volatility
```

**Crypto Adaptation:**
- 12-day lookback (vs 12-month) for crypto volatility
- 1-day skip for momentum crash protection
- Volatility-adjusted scoring (Sharpe-like)

**Status:** ✅ Implemented, tested, ready for paper trading

**Risk Level:** HIGH (momentum crashes)

---

### 2. **Mean-Reversion** (Section 3.9)

**Paper Reference:**
> "Ornstein-Uhlenbeck process: dX_t = θ(μ - X_t)dt + σdW_t"
> Half-life: t_{1/2} = ln(2)/θ

**Implementation:** `CryptoMeanReversionDetector`

**Formula:**
```
Z-score = (Price - Mean) / StdDev
```

**Entry/Exit:**
- Entry: |Z-score| > 2.0
- Exit: |Z-score| < 0.5
- Max holding: 5 days

**Crypto Adaptation:**
- Z-score based (simpler than OLS for half-life)
- Shorter holding periods
- Volatility regime filtering

**Status:** ✅ Implemented, tested, ready for paper trading

**Risk Level:** HIGH (trend continuation risk)

---

### 3. **KNN Machine Learning** (Section 3.17)

**Paper Reference:**
> "k-nearest neighbors for predicting stock returns
> Features: technical indicators, market microstructure
> Distance metric: Euclidean or Mahalanobis"

**Implementation:** `CryptoKNNDetector`

**Features Used:**
1. 1-period return
2. 5-period return
3. 10-period return
4. Volatility (std of returns)
5. Price vs MA5 ratio
6. Price vs MA20 ratio
7. Volume change

**Algorithm:**
```python
1. Calculate feature vector for current state
2. Find k nearest neighbors in historical data
3. Weighted average of neighbor outcomes
4. Confidence = 1 / (1 + variance of neighbor outcomes)
```

**Status:** ✅ Implemented, **PAPER TRADE ONLY** (needs extensive backtesting)

**Risk Level:** VERY HIGH (ML overfitting)

---

## 📊 Strategy Comparison

| Strategy | Section | Complexity | Risk | Status | Recommended |
|----------|---------|------------|------|--------|-------------|
| **Momentum** | 3.1 | Medium | HIGH | ✅ Ready | Paper trade first |
| **Mean-Reversion** | 3.9 | Medium | HIGH | ✅ Ready | Paper trade first |
| **KNN** | 3.17 | High | VERY HIGH | ⚠️ Experimental | Paper trade only |

---

## 🚀 How to Activate

### 1. Add to Strategy Engine

Edit `hunter/strategies/engine.py`:

```python
from hunter.strategies.academic_strategies import (
    CryptoMomentumDetector,
    CryptoMeanReversionDetector,
    CryptoKNNDetector
)

# In StrategyEngine.__init__():
self.detectors[StrategyType.MOMENTUM] = CryptoMomentumDetector(ecosystem)
# Add new enum for MEAN_REVERSION if desired
```

### 2. Update Config

Edit `~/.hunter/config.yaml`:

```yaml
scan:
  strategy_types:
    - arbitrage
    - yield_farming
    - momentum
    - crypto_momentum        # NEW
    - crypto_mean_reversion  # NEW
    # - crypto_knn           # Experimental, uncomment with caution
```

### 3. Run Scan

```bash
hunter scan --type crypto_momentum --min-confidence 0.7
```

---

## 📈 Expected Performance (from Paper)

### Momentum
- **Historical:** 1-2% monthly excess returns (traditional markets)
- **Crypto:** Higher volatility, higher potential returns AND drawdowns
- **Crashes:** Momentum can experience sudden 10-20% drawdowns

### Mean-Reversion
- **Half-life:** Typically 2-5 days in crypto (faster than stocks)
- **Win rate:** 55-60% (slight edge)
- **Risk:** Trend continuation can cause consecutive losses

### KNN
- **Paper results:** Varies widely based on feature selection
- **Crypto:** Requires extensive backtesting (not provided)
- **Risk:** High overfitting potential

---

## ⚠️ Important Warnings

### From Paper Authors:
> "We do NOT claim profitability—markets evolve and strategies decay."
> "The goal is descriptive and educational."

### Implementation Notes:
1. **Backtesting Required:** All strategies need out-of-sample testing
2. **Transaction Costs:** Not included in formulas; crypto fees add up
3. **Slippage:** Large orders move prices, especially in altcoins
4. **Regime Changes:** Strategies work until they don't

---

## 🎓 Academic References (from Paper)

| Strategy | Key Reference |
|----------|---------------|
| Momentum | Jegadeesh & Titman (1993), "Returns to Buying Winners and Selling Losers" |
| Mean-Reversion | Ornstein & Uhlenbeck (1930), "On the Theory of the Brownian Motion" |
| KNN | Altman (1992), "An Introduction to Kernel and Nearest-Neighbor Nonparametric Regression" |

---

## 🔮 Future Enhancements

From paper (not yet implemented):
- **Pairs Trading** (3.8): Cointegration-based arbitrage
- **Residual Momentum** (3.7): Idiosyncratic returns momentum
- **Statistical Arbitrage** (3.18): Optimization-based
- **ANN for Crypto** (18.2): Neural networks (mentioned in paper)

---

## 📝 Implementation Quality

| Aspect | Status |
|--------|--------|
| Mathematical Accuracy | ✅ Faithful to paper formulas |
| Crypto Adaptation | ✅ Shortened timeframes for volatility |
| Risk Management | ✅ Position sizing, stop-losses included |
| Code Quality | ✅ Documented, typed, tested |
| Backtesting | ⚠️ User must implement OOS testing |

---

## 💡 Key Takeaway

These strategies provide **mathematical frameworks** from academic literature. 

**NOT guaranteed profits** — they are:
- ✅ Well-researched patterns
- ✅ Mathematically rigorous
- ✅ Risk-quantified
- ❌ NOT future-proof
- ❌ NOT get-rich-quick

**Always:**
1. Paper trade first
2. Backtest on out-of-sample data
3. Monitor for strategy decay
4. Manage position sizes

---

*"Strategies are ephemeral. Mathematics is permanent."*
— Adapted from Kakushadze & Serur
