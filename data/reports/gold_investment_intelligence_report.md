# Global Gold Investment Intelligence Engine — Technical & Quantitative Report (Task 03)

**Engine Version:** 3.0.0  
**Audit & Release Date:** November 5, 2026  
**Reference Spot Price:** \$4,073.00 / troy ounce  
**Historical Observation Span:** August 30, 2000 to November 4, 2026 (6,571 trading records, 7,460 calendar rows)  
**Historical All-Time High:** \$5,318.40 (January 29, 2026)  
**Automated Test Suite Status:** **54 / 54 PASSED**

---

## 1. Executive Summary & Architecture Overview

Task 03 advances the Global Gold Price Intelligence and Forecasting Platform from single-model time-series forecasting into an institutional-grade **Gold Investment Intelligence Engine**. 

The engine introduces five core analytical modules and a dedicated financial terminal dashboard:
1. **Market Regime Intelligence (`ml/gold/regime_intelligence.py`)**: Multi-factor classification across Bullish, Bearish, Sideways, and High Volatility regimes using SMA 50/200, 21d/63d momentum, rolling volatility, and Welles Wilder's 14-period ADX.
2. **Quantitative Risk Analytics (`ml/gold/risk_analytics.py`)**: Realized volatility across 7d, 30d, 90d, full-series; Historical Simulation Value at Risk (VaR) and Expected Shortfall (CVaR) at 95% and 99% confidence for 1-day and 10-day horizons; and 6 macroeconomic stress-testing shock scenarios.
3. **Scenario Forecasting Engine (`ml/gold/scenario_forecasting.py`)**: Three conditional macroeconomic trajectories (Bullish, Base, Bearish) spanning 30, 90, 180, and 365 trading days, grounded in policy assumptions, historical distributions, and model consensus.
4. **Uncertainty & Conformal Calibration Engine (`ml/gold/uncertainty_engine.py`)**: Multi-tier 50%, 80%, and 95% prediction intervals calibrated strictly via validation-based split-conformal prediction (2023 validation set) without test-set peeking.
5. **Macroeconomic Intelligence Collector (`src/collectors/macro_collector.py`)**: Synchronized tracking of 7 core fundamental drivers (DXY, US 10Y Yield, TIPS Real Yield, US CPI, USD/INR, ETF Holdings, Central Bank Purchases) with point-in-time publication lag documentation.
6. **Investment Intelligence API (`src/api/app.py`)**: 6 new modular REST endpoints maintaining backward compatibility with all prior endpoints.
7. **Institutional Financial Terminal Dashboard (`src/dashboard/index.html` & `/dashboard`)**: Interactive terminal interface presenting all 8 required analytical sections.

---

## 2. Module 1: Market Regime Intelligence

### Quantitative Methodology
Regimes are classified using a multi-factor voting framework that avoids reliance on any single technical indicator:
1. **Moving Average Trend Structure:** 50-day and 200-day Simple Moving Averages, cross ratio ($\text{SMA}_{50} / \text{SMA}_{200}$), and price location relative to $\text{SMA}_{50}$.
2. **Intermediate & Cyclical Momentum:** 21-day and 63-day percentage returns ($\text{ROC}$).
3. **Realized Volatility Profile:** 30-day and 90-day annualized realized standard deviations ($\times \sqrt{252}$).
4. **Trend Conviction:** Welles Wilder's 14-period Average Directional Index ($\text{ADX}_{14}$) with $+DI_{14}$ and $-DI_{14}$ directional indicators:
   $$TR = \max(H - L, |H - C_{t-1}|, |L - C_{t-1}|)$$
   $$+DM = \mathbb{I}_{\{H_t - H_{t-1} > L_{t-1} - L_t \text{ and } H_t - H_{t-1} > 0\}} (H_t - H_{t-1})$$
   $$-DM = \mathbb{I}_{\{L_{t-1} - L_t > H_t - H_{t-1} \text{ and } L_{t-1} - L_t > 0\}} (L_{t-1} - L_t)$$
   $$DX = 100 \times \frac{|+DI - -DI|}{+DI + -DI}, \quad ADX = \text{EMA}(DX, 14)$$

### Classification Rules
- **High Volatility:** Realized 30d annualized volatility $> 24.0\%$ or 90d volatility $> 22.5\%$ or 63-day drawdown $< -10.0\%$.
- **Bullish:** Trend score $\ge 60\%$ (Price $> \text{SMA}_{50} > \text{SMA}_{200}$, $\text{SMA}_{\text{ratio}} > 1.015$, $+DI > -DI$, positive momentum).
- **Bearish:** Downtrend score $\ge 60\%$ (Price $< \text{SMA}_{50} < \text{SMA}_{200}$, $\text{SMA}_{\text{ratio}} < 0.985$, $-DI > +DI$, negative momentum).
- **Sideways:** Mixed technical signals, consolidating moving averages, and weak trend conviction ($\text{ADX} < 20.0$).

### Empirical Distribution (2000–2026)
- **Bullish:** 3,415 trading days (52.0%)
- **Bearish:** 1,764 trading days (26.8%)
- **High Volatility:** 825 trading days (12.6%)
- **Sideways:** 368 trading days (5.6%)
- **Warm-up / Unclassified:** 199 trading days (3.0%)
- **Current Active Regime (Nov 4, 2026):** `High Volatility` (30d Vol: 22.41%, 63d Drawdown: -13.3%, ADX: 31.33).

---

## 3. Module 2: Quantitative Risk Analytics & Stress Testing

### Realized Volatility Profile
- **7-Day Realized Volatility:** 33.77%
- **30-Day Realized Volatility:** 22.41%
- **90-Day Realized Volatility:** 21.79%
- **Full Series Historical Volatility (2000–2026):** **17.98%**

### Drawdown Dynamics & Recovery
- **All-Time High:** \$5,318.40 (January 29, 2026)
- **Current Spot Price:** \$4,073.00
- **Current Drawdown from ATH:** **-23.42%**
- **Days Elapsed Since ATH:** 280 calendar days (198 trading days)
- **Historical Maximum Drawdown:** **-44.36%** (Peak: \$1,888.70 on August 22, 2011 $\rightarrow$ Trough: \$1,050.80 on December 17, 2015)
- **Historical Recovery Duration from Max Drawdown:** Fully recovered on July 24, 2020 (2,246 trading days / 3,259 calendar days).

### Historical Simulation VaR & Expected Shortfall (CVaR)
Calculated from 6,570 empirical daily return observations:
$$\text{VaR}_\alpha = -Q_{1-\alpha}(R), \quad \text{CVaR}_\alpha = -\mathbb{E}[R \mid R \le -\text{VaR}_\alpha]$$

| Confidence Level | Risk Horizon | VaR (%) | CVaR / Expected Shortfall (%) |
| :--- | :--- | :--- | :--- |
| **95% Confidence** | 1-Day Horizon | **1.66%** | **2.55%** |
| **99% Confidence** | 1-Day Horizon | **2.60%** | **3.91%** |
| **95% Confidence** | 10-Day Horizon | **5.25%** | **8.06%** |
| **99% Confidence** | 10-Day Horizon | **8.22%** | **12.35%** |

### Macroeconomic Stress Testing Scenarios
1. **Sharp USD Appreciation (DXY +12.0%):** Gold beta $-0.80$, projected price: **\$3,682.00** (-9.60%).
2. **Rising US Real Yields (10Y TIPS +175 bps):** Gold beta $-6.20$, projected price: **\$3,631.08** (-10.85%).
3. **Geopolitical Escalation (Safe-Haven Flight):** Gold beta $+1.25$, projected price: **\$4,529.18** (+11.20%).
4. **Inflation Surprises (CPI +2.5% overshoot):** Gold beta $+0.85$, projected price: **\$4,419.20** (+8.50%).
5. **Central Bank Demand Slowdown (Purchases Halved):** Gold beta $-0.65$, projected price: **\$3,728.83** (-8.45%).
6. **USD/INR Currency Shock (+8.0% Rupee depreciation):** Domestic Indian landed parity surges to **₹134,057 / 10g** (+7.84%).

---

## 4. Module 3: Scenario Forecasting

The engine generates three multi-horizon conditional scenarios distinct from unconditional statistical prediction intervals:

| Scenario | 30-Day Target (\$) | 90-Day Target (\$) | 180-Day Target (\$) | 365-Day Target (\$) | 365-Day Return (%) | Core Macro Thesis |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bullish** | \$4,350.00 | \$4,720.00 | \$5,180.00 | **\$5,850.00** | **+43.60%** | Accelerated de-dollarization (>1,200t/yr), US real yields $< 1.0\%$, DXY $< 97.0$. |
| **Base** | \$4,076.70 | \$4,259.34 | \$4,145.23 | **\$4,343.01** | **+6.63%** | Validated model consensus (XGBoost + Prophet), orderly disinflation, stable central bank buying (~950t/yr). |
| **Bearish** | \$3,820.00 | \$3,580.00 | \$3,390.00 | **\$3,200.00** | **-21.40%** | Higher-for-longer Fed rates, real yields $> 2.5\%$, DXY $> 108.0$, official purchases slow to 500t/yr. |

---

## 5. Module 4: Uncertainty Engine & Conformal Calibration

### Resolving the 77.7% XGBoost 30-Day Under-Coverage
- **Root Cause of Prior Under-Coverage:**
  Uncalibrated Gaussian prediction intervals assumed a fixed $1.96 \sigma$ multiplier derived from training set residuals ($\sigma_{\text{train}} = 4.65\%$). During the 2024–2026 test period, realized forward return volatility surged to $7.00\%$, and price climbed from \$2,040 to \$5,318.40. Out of 153 total breaches, 106 (69.3%) were **upper-bound breaches** ($y > \text{UB}$) caused by secular bull market drift and non-Gaussian fat tails.
- **Validation-Based Conformal Calibration:**
  Conformal scaling multipliers $\hat{q}_{1-\alpha, h}$ were calibrated strictly on the **2023 chronological validation split** ($N = 251$) without peeking at the 2024–2026 test set:
  $$\hat{q}_{1-\alpha, h} = \text{Quantile}\left(\left\{\frac{|y_i - \hat{y}_i|}{\hat{\sigma}_{h, i}}\right\}_{i=1}^{n_{\text{val}}}, \frac{\lceil (n_{\text{val}} + 1)(1 - \alpha) \rceil}{n_{\text{val}}}\right)$$
- **Calibrated Conformal Multipliers:**
  - 30-Day: $50\% \rightarrow 0.5767$, $80\% \rightarrow 1.0262$, $95\% \rightarrow 1.6114$
  - 90-Day: $50\% \rightarrow 0.4135$, $80\% \rightarrow 0.9936$, $95\% \rightarrow 1.3716$
  - 180-Day: $50\% \rightarrow 0.7374$, $80\% \rightarrow 1.0467$, $95\% \rightarrow 1.3068$
  - 365-Day: $50\% \rightarrow 0.6142$, $80\% \rightarrow 1.4383$, $95\% \rightarrow 2.0133$
- **Monotonic Expansion:** Both confidence tier widths ($50\% < 80\% < 95\%$) and horizon widths ($30d < 90d < 180d < 365d$) expand monotonically.

---

## 6. Module 5: Macroeconomic Intelligence Catalog

All 7 core macroeconomic drivers are tracked with strict point-in-time publication lag constraints:
1. **US Dollar Index (DXY):** ICE Market Close, T+0 lag, Ref: 104.38.
2. **US 10-Year Treasury Yield (TNX):** US Treasury / CBOE, T+0 lag, Ref: 4.38%.
3. **US 10-Year Real Yield (TIPS / DFII10):** St. Louis Fed FRED, T+1 lag, Ref: 1.95%.
4. **US Consumer Price Index (CPIAUCSL):** Bureau of Labor Statistics, 10–14 day release lag, Ref: 315.3 (YoY ~2.6%).
5. **USD/INR Exchange Rate (INR=X):** Reserve Bank of India, T+0 lag, Ref: 94.94.
6. **Gold ETF Holdings (GLD + IAU):** State Street / BlackRock, T+1 lag, Ref: 1,315.2 metric tonnes.
7. **Central-Bank Gold Purchases:** World Gold Council / IMF IFS, 45-day quarterly reporting lag, Ref: 1,037 tonnes annualized pace.

---

## 7. Module 6 & 7: API Endpoints & Financial Terminal Dashboard

### REST API Catalog
- `GET /api/gold/intelligence` — Unified executive intelligence payload
- `GET /api/gold/risk` — Full market risk analytics, VaR/CVaR, and 6 stress tests
- `GET /api/gold/scenarios` — Bullish/Base/Bearish multi-horizon trajectories and macro assumptions
- `GET /api/gold/uncertainty` — Conformal multi-tier prediction intervals and breach audit
- `GET /api/gold/macro` — Macroeconomic indicator catalog with point-in-time metadata
- `GET /api/gold/regime-history` — Queryable historical regimes and supporting indicators
- `GET /dashboard` — High-performance financial terminal interface
- Existing endpoints preserved: `/api/gold/history`, `/api/gold/forecast`, `/api/gold/metrics`, `/api/gold/trends`, `/api/gold/regimes`.

---

## 8. Verification & Acceptance Sign-Off

The entire automated test suite of **54 unit, integration, and regression tests** executes cleanly without error:
- Task 01 Data Pipeline Tests: 9 passed
- Task 02 Forecasting & API Tests: 15 passed
- Task 02 Validation Audit Tests: 13 passed
- Task 03 Investment Intelligence Tests: 17 passed
- **Total: 54 / 54 PASSED in 3.56s**
- **Production Dataset Integrity:** `gold_master_daily_unified.csv` verified invariant under SHA-256 (`eead2b1...`).
