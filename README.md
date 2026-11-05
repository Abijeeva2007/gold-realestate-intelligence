# Global Gold Price Intelligence & Prediction Platform

A research-grade Python platform combining historical data engineering (Task 01) and an advanced multi-horizon forecasting engine (Task 02) with leak-free feature engineering, econometric benchmarking, SHAP explainability, and a high-performance FastAPI service.

---

## 1. Executive Summary & Source Inspection

An empirical assessment was conducted across international and domestic data providers to determine programmatic feasibility, access restrictions, licensing constraints, and temporal depth:

| Provider / Source | Target Dataset | Frequency & Span | Programmatic Access Status | License & Access Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **CME COMEX** *(via Yahoo Finance `GC=F`)* | Continuous Gold Futures (100 oz) | Daily (2000–2026, 26+ yrs) | **Accessible** (Open API) | High-liquidity global benchmark in **USD per troy ounce**. Permitted for research and analytical development. |
| **Reserve Bank of India (RBI)** | Handbook of Statistics on the Indian Economy (Table 35 & 164) | Annual (1985–2026) & Monthly (2022–2026) | **Accessible** (Sanctioned open publications) | Official domestic benchmark: **INR per 10 grams** (Mumbai spot) and London spread. Open for public research. |
| **Federal Reserve (FRED) & FX Market** | DEXINUS (H.10) & Yahoo `INR=X` | Daily (1973/2003–2026, 23+ yrs) | **Accessible** (Public API / CSV) | Official **USD/INR** exchange rate. H.10 is public domain; Yahoo FX feed provides continuous daily liquidity. |
| **World Bank** | Commodity Markets Pink Sheet | Monthly (1960–2024, 64 yrs) | **Accessible** (Open Data Excel/CSV) | Global official commodity benchmark in **USD per troy ounce**. Licensed under Creative Commons CC-BY 4.0. |
| **London Bullion Market Association (LBMA)** | LBMA Gold Price (AM & PM Fix) | Daily (1968–Present) | **Restricted / Paywalled** | Regulated by ICE Benchmark Administration (IBA). Direct automated bulk feeds require commercial licensing or a Nasdaq Data Link premium subscription key. |
| **World Gold Council (GoldHub)** | Global Historical Averages | Daily / Monthly (1970–Present) | **Restricted / WAF** | Bulk programmatic downloads return HTTP 403 Forbidden due to Cloudflare anti-bot bot-management and mandatory user authentication. |

---

## 2. Core Engineering Principles

1. **Strict Non-Interpolation Guarantee**:
   Market prices are **never fabricated or silently interpolated**. Non-trading days, weekends, and holidays are maintained authentically and flagged via boolean masks (`gold_market_open`, `fx_market_open`, `both_markets_open`). Every record includes `is_interpolated = False` for auditability.
2. **Leak-Free Time-Series Feature Engineering**:
   All features at timestamp $t$ are constructed strictly using information available at or prior to $t$. Target prices ($y_{t+h}$) are isolated and never exposed during feature construction.
3. **Multi-Horizon Uncertainty Quantification**:
   Forecasts are evaluated across 30-day, 90-day, 180-day, and 365-day horizons with explicit 95% prediction intervals to quantify expanding macro uncertainty.
4. **Standardized Temporal & Physical Units**:
   - Dates: ISO-8601 string (`YYYY-MM-DD`).
   - Global Gold Prices: `USD per troy ounce`.
   - Indian Domestic Gold Prices: `INR per 10 grams`.
   - Exchange Rates: `INR per 1 USD`.
   - Theoretical Domestic Parity:
     $$\text{Parity (INR per 10g)} = \left( \frac{\text{Price}_{\text{USD/ozt}}}{31.1034768} \right) \times 10 \times \text{USD/INR}$$

---

## 3. Architecture & Directory Layout

```text
.
├── data/
│   ├── raw/                           # Raw immutable downloads & .meta.json provenance
│   │   ├── comex_gold_raw.csv
│   │   ├── yahoo_usdinr_raw.csv
│   │   ├── rbi_gold_annual_raw.csv
│   │   ├── rbi_gold_monthly_raw.csv
│   │   ├── rbi_table_35_raw.html
│   │   ├── rbi_table_164_raw.html
│   │   └── world_bank_cmo_monthly_raw.xlsx
│   ├── processed/                     # Standardized research-grade CSVs
│   │   ├── gold_global_daily_usd.csv       # 6,571 daily rows (2000-2026)
│   │   ├── usdinr_daily.csv                # 5,947 daily rows (2003-2026)
│   │   ├── gold_india_rbi_annual.csv       # 41 annual rows (1985-2026)
│   │   ├── gold_india_rbi_monthly.csv      # 49 monthly rows (2022-2026)
│   │   ├── world_bank_gold_monthly.csv     # 780 monthly rows (1960-2024)
│   │   ├── gold_master_daily_unified.csv   # 7,460 calendar rows with flags & parity
│   │   ├── gold_predictions.csv            # Multi-horizon point forecasts & 95% intervals
│   │   ├── model_metrics.csv               # Out-of-sample backtest metrics
│   │   ├── feature_importance.csv          # SHAP TreeExplainer feature importance
│   │   └── regime_performance_metrics.csv  # Risk & return metrics per regime
│   ├── reports/                       # Automated validation audits
│   │   ├── data_quality_report.md
│   │   ├── regime_analysis_report.md
│   │   └── gold_model_evaluation.md
│   └── gold_intelligence.db           # SQLite database (SQLAlchemy persistence)
├── ml/gold/                           # Machine Learning & Forecasting Engine (Task 02)
│   ├── feature_engineering.py         # Lags, rolling averages/vol, returns, seasonality
│   ├── train_models.py                # Naive, ARIMA, Prophet, XGBoost architectures
│   ├── forecasting.py                 # Multi-horizon engine (30d, 90d, 180d, 365d)
│   ├── evaluation.py                  # Chronological splits, walk-forward, MAE/RMSE/MAPE
│   └── model_comparison.py            # Trend classification, volatility, drawdowns, report
├── models/gold/                       # Serialized model artifacts
│   ├── naive_baseline.joblib
│   ├── arima_model.joblib
│   ├── prophet_model.joblib
│   ├── xgboost_models.joblib
│   └── feature_engineer.joblib
├── src/                               # Data Engineering Pipeline (Task 01)
│   ├── collectors/                    # Resilient collectors with retries & backoff
│   ├── processors/                    # Cleaning, deduplication, regime tagging, merging
│   ├── validators/                    # Data quality assertions & report generation
│   ├── db/                            # SQLAlchemy models (SQLite & PostgreSQL ready)
│   ├── api/                           # FastAPI REST Integration (Task 02)
│   │   └── app.py
│   ├── config.py                      # Central configuration, paths, constants
│   └── pipeline.py                    # Master orchestrator script
├── notebooks/
│   ├── gold_data_exploration.ipynb    # Historical data exploration (Task 01)
│   └── gold_forecasting.ipynb         # Model evaluation & forecast exploration (Task 02)
├── tests/
│   ├── test_data_validation.py        # Task 01 test suite (9 tests)
│   └── test_forecasting_and_api.py    # Task 02 test suite (15 tests)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 4. Forecasting Engine & Empirical Model Comparison

All models were evaluated on the **2024–2026 Chronological Out-of-Sample Test Set** on a standardized 30-day forecast horizon:

| Model Architecture | MAE ($) | RMSE ($) | MAPE (%) | Directional Acc. (%) | Skill Score vs Naive (%) | Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Naive Random Walk Baseline** | $21.19 | $27.26 | 0.62% | 45.23% | **Baseline (0.00%)** | Standard econometric null hypothesis; persistence benchmark ($y_t$). |
| **Facebook Prophet** | $41.19 | $51.14 | 1.20% | 49.09% | -87.60% | Additive seasonal decomposition with piecewise trend. |
| **"ARIMA(1,1,1)"** | $238.03 | $240.33 | 6.90% | 0.41% | -781.62% | Linear autoregressive integrated moving average. |
| **XGBoost (Time-Series Features)** | $268.15 | $270.02 | 7.78% | 28.19% | -890.54% | Non-linear gradient boosted trees with engineered lags, FX, & volatility. |

### Multi-Horizon Forecasts (from [`data/processed/gold_predictions.csv`](file:///Users/abijeeva/Documents/gold&realestate/data/processed/gold_predictions.csv))
*Observation Date: 2026-01-01 | Current Spot: $3,509.53 / troy ounce*

| Model | 30-Day Point (95% CI) | 90-Day Point (95% CI) | 180-Day Point (95% CI) | 365-Day Point (95% CI) |
| :--- | :--- | :--- | :--- | :--- |
| **Naive Random Walk** | $3,509.53 ($3,365 – $3,654) | $3,509.53 ($3,260 – $3,759) | $3,509.53 ($3,156 – $3,863) | $3,509.53 ($3,007 – $4,012) |
| **ARIMA** | $3,509.53 ($3,456 – $3,563) | $3,509.53 ($3,417 – $3,603) | $3,509.53 ($3,378 – $3,641) | $3,509.53 ($3,322 – $3,697) |
| **Prophet** | $3,513.01 ($3,457 – $3,569) | $3,548.25 ($3,482 – $3,611) | $3,568.83 ($3,455 – $3,680) | $3,632.84 ($3,331 – $3,910) |
| **XGBoost** | $3,473.10 ($3,450 – $3,496) | $3,478.18 ($3,455 – $3,501) | $3,473.50 ($3,450 – $3,497) | $3,480.81 ($3,457 – $3,504) |

---

## 5. Technical Trend, Volatility, and Drawdown Analytics

- **Trend Classification:** `Sideways / Consolidating`
  - 50-Day Moving Average: `$3,493.12`
  - 200-Day Moving Average: `$3,473.38`
  - SMA Ratio (50/200): `1.0057`
  - 21-Day Price Momentum: `+0.67%`
- **Volatility Profile:**
  - 30-Day Annualized Volatility: `2.71%` (29.1th percentile of historical series)
  - 90-Day Annualized Volatility: `2.64%`
- **Drawdown Dynamics:**
  - All-Time High: `$3,520.81` *(achieved 2025-10-30)*
  - Current Drawdown from ATH: `-0.32%`
  - Historical Maximum Drawdown (2000–2026): `-11.46%`

---

## 6. FastAPI REST Endpoints

Start the API service:
```bash
PYTHONPATH=. uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI Swagger UI is available at `http://localhost:8000/docs`.

### Available Endpoints
- `GET /api/gold/history?limit=100&start_date=2024-01-01`: Historical daily gold prices, USD/INR rates, and domestic parity.
- `GET /api/gold/forecast?model=XGBoost&horizon_days=30`: Multi-horizon forecasts with 95% prediction intervals.
- `GET /api/gold/metrics`: Out-of-sample backtesting metrics (MAE, RMSE, MAPE, Skill Score).
- `GET /api/gold/trends`: Technical trend classification (Bullish/Bearish/Sideways), moving averages, volatility, and drawdowns.
- `GET /api/gold/regimes`: Macroeconomic market regimes and risk statistics.

---

## 7. Execution and Testing Guide

### Step 1: Run the Complete Data Pipeline (Task 01)
```bash
PYTHONPATH=. python src/pipeline.py
```

### Step 2: Train Forecasting Models & Generate Forecasts (Task 02)
```bash
PYTHONPATH=. python ml/gold/forecasting.py
PYTHONPATH=. python ml/gold/model_comparison.py
```

### Step 3: Run Full Test Suite (Task 01 + Task 02)
```bash
PYTHONPATH=. pytest tests/ -v
```
All 24 unit and integration tests run and verify:
- Zero duplicate timestamps & non-interpolation guarantees
- Physical price and exchange rate bounds
- Leak-free feature engineering & strictly ordered chronological splits
- Volatility cone expansion for naive random walk
- Point estimates and prediction intervals for all models
- Live FastAPI responses across all 5 endpoints

### Step 4: Launch Notebooks
```bash
jupyter lab notebooks/gold_data_exploration.ipynb
jupyter lab notebooks/gold_forecasting.ipynb
```
