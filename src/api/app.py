"""
FastAPI REST API for Global Gold Price Intelligence & Forecasting Platform.
Endpoints:
- GET /api/gold/history: Historical daily gold prices, FX rates, and domestic parity.
- GET /api/gold/forecast: Multi-horizon forecasts (30d, 90d, 180d, 365d) with 95% prediction intervals.
- GET /api/gold/metrics: Comparative model evaluation metrics (MAE, RMSE, MAPE, Skill Score).
- GET /api/gold/trends: Current technical trend (Bullish/Bearish/Sideways), moving averages, volatility, and drawdowns.
- GET /api/gold/regimes: Historical macroeconomic regimes and risk metrics.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import pandas as pd
import numpy as np
from sqlalchemy import text

from src.config import BASE_DIR, PROCESSED_DATA_DIR
from src.db.database import get_engine
from ml.gold.model_comparison import GoldModelComparisonEngine
from ml.gold.regime_intelligence import GoldRegimeEngine
from ml.gold.risk_analytics import GoldRiskEngine
from ml.gold.scenario_forecasting import GoldScenarioForecaster
from ml.gold.uncertainty_engine import GoldUncertaintyEngine
from src.collectors.macro_collector import MacroIntelligenceCollector
from src.real_estate.api.router import router as real_estate_router
import json
import os
from datetime import date

app = FastAPI(
    title="Global Market Intelligence & Real Estate Platform API",
    description="Research-Grade Gold Forecasting & Tamil Nadu Real Estate Intelligence Engine",
    version="2.0.0"
)

# Production CORS configuration
cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
allowed_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()] if cors_origins_raw != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app" if "*" not in allowed_origins else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Real Estate Intelligence Router
app.include_router(real_estate_router)

engine = get_engine()
processed_dir = Path(PROCESSED_DATA_DIR)
assets_dir = BASE_DIR / "src/dashboard/assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


@app.get("/health")
def health_check():
    """Production health check endpoint verifying database connectivity."""
    gold_status = "UNKNOWN"
    re_status = "UNKNOWN"
    try:
        with engine.connect() as conn:
            c = conn.execute(text("SELECT count(*) FROM gold_daily_prices")).scalar()
            gold_status = f"CONNECTED ({c} rows)"
    except Exception as e:
        gold_status = f"ERROR: {str(e)}"

    try:
        from src.real_estate.db.database import get_real_estate_engine
        re_engine = get_real_estate_engine()
        with re_engine.connect() as conn:
            c = conn.execute(text("SELECT count(*) FROM price_observations")).scalar()
            re_status = f"CONNECTED ({c} rows)"
    except Exception as e:
        re_status = f"ERROR: {str(e)}"

    is_healthy = "CONNECTED" in gold_status and "CONNECTED" in re_status

    return {
        "status": "HEALTHY" if is_healthy else "DEGRADED",
        "timestamp": str(date.today()),
        "version": "2.0.0",
        "databases": {
            "gold_intelligence_db": gold_status,
            "real_estate_db": re_status
        }
    }


@app.get("/")
def root():
    return {
        "platform": "Global Gold Price Intelligence Platform",
        "status": "ONLINE",
        "version": "1.0.0",
        "docs_url": "/docs",
        "available_endpoints": [
            "/dashboard",
            "/real-estate-dashboard",
            "/api/real-estate/overview",
            "/api/real-estate/districts",
            "/api/real-estate/rankings",
            "/api/real-estate/localities",
            "/api/real-estate/valuation",
            "/api/real-estate/forecasts",
            "/api/real-estate/rental-yields",
            "/api/real-estate/macro",
            "/api/real-estate/sources",
            "/api/real-estate/models",
            "/api/real-estate/data-quality",
            "/api/gold/history",
            "/api/gold/forecast",
            "/api/gold/metrics",
            "/api/gold/trends",
            "/api/gold/regimes",
            "/api/gold/intelligence",
            "/api/gold/risk",
            "/api/gold/scenarios",
            "/api/gold/uncertainty",
            "/api/gold/macro",
            "/api/gold/regime-history"
        ]
    }


@app.get("/api/gold/history")
def get_gold_history(
    limit: int = Query(default=100, ge=1, le=8000),
    start_date: Optional[str] = Query(default=None, description="Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="Format YYYY-MM-DD")
):
    """Retrieves historical daily gold prices and USD/INR exchange rates from database."""
    query = "SELECT date, close_usd_per_troy_oz, open_usd_per_troy_oz, high_usd_per_troy_oz, low_usd_per_troy_oz, volume, fx_usdinr, gold_parity_inr_per_10g, regime_name FROM gold_daily_prices WHERE gold_market_open = 1"
    params = {}

    if start_date:
        query += " AND date >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND date <= :end_date"
        params["end_date"] = end_date

    query += " ORDER BY date DESC LIMIT :limit"
    params["limit"] = limit

    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)
        raw_records = df.to_dict(orient="records")
        clean_records = [{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in raw_records]
        return {
            "status": "success",
            "total_returned": len(clean_records),
            "data": clean_records
        }
    except Exception as exc:
        # Fallback to processed CSV
        csv_path = processed_dir / "gold_master_daily_unified.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df = df[df["gold_market_open"]].sort_values("date", ascending=False)
            if start_date:
                df = df[df["date"] >= start_date]
            if end_date:
                df = df[df["date"] <= end_date]
            df = df.head(limit)
            raw_records = df.to_dict(orient="records")
            clean_records = [{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in raw_records]
            return {
                "status": "success (csv_fallback)",
                "total_returned": len(clean_records),
                "data": clean_records
            }
        raise HTTPException(status_code=500, detail=f"Database query failed: {exc}")


@app.get("/api/gold/forecast")
def get_gold_forecast(
    model: Optional[str] = Query(default=None, description="Filter by model name: 'XGBoost', 'ARIMA', 'Prophet', 'Naive Random Walk'"),
    horizon_days: Optional[int] = Query(default=None, description="Filter by horizon: 30, 90, 180, 365")
):
    """Returns multi-horizon forecasts with point estimates and 95% uncertainty intervals."""
    pred_path = processed_dir / "gold_predictions.csv"
    if not pred_path.exists():
        raise HTTPException(status_code=404, detail="Forecasts not generated yet. Please run the forecasting engine.")

    df = pd.read_csv(pred_path)
    if model:
        df = df[df["model"].str.lower().str.contains(model.lower())]
    if horizon_days:
        df = df[df["horizon_days"] == horizon_days]

    if df.empty:
        raise HTTPException(status_code=404, detail="No forecasts match the specified filter criteria.")

    forecast_date_val = str(df["forecast_origin_date"].iloc[0]) if "forecast_origin_date" in df.columns else str(df["forecast_date"].iloc[0])
    return {
        "status": "success",
        "current_price_usd": float(df["current_price_usd"].iloc[0]),
        "forecast_date": forecast_date_val,
        "forecast_origin_date": forecast_date_val,
        "total_forecasts": len(df),
        "forecasts": df.to_dict(orient="records")
    }


@app.get("/api/gold/metrics")
def get_model_metrics():
    """Returns comparative model performance metrics (MAE, RMSE, MAPE, Skill Score vs. Naive)."""
    metrics_path = processed_dir / "model_metrics.csv"
    if not metrics_path.exists():
        raise HTTPException(status_code=404, detail="Model evaluation metrics not found.")

    df = pd.read_csv(metrics_path)
    return {
        "status": "success",
        "evaluation_period": "2024-2026 Chronological Out-of-Sample Test Set",
        "benchmark_baseline": "Naive Random Walk Baseline",
        "models": df.to_dict(orient="records")
    }


@app.get("/api/gold/trends")
def get_gold_trends():
    """Returns current technical trend classification, moving averages, volatility, and drawdowns."""
    csv_path = processed_dir / "gold_master_daily_unified.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Cleaned gold data not found.")

    comparison_engine = GoldModelComparisonEngine(data_path=csv_path)
    df_raw = pd.read_csv(csv_path)
    df_gold = df_raw[df_raw["gold_market_open"]].sort_values("date").reset_index(drop=True)
    df_feat = comparison_engine.feature_engineer.build_features(df_gold, drop_na=True)
    analysis = comparison_engine.compute_market_analysis(df_feat)

    return {
        "status": "success",
        "market_analysis": analysis
    }


@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    """Serves the Institutional Gold Investment Intelligence Terminal Dashboard."""
    html_path = BASE_DIR / "src/dashboard/index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Dashboard template not found.")
    return html_path.read_text(encoding="utf-8")


@app.get("/real-estate-dashboard", response_class=HTMLResponse)
def serve_real_estate_dashboard():
    """Serves the Tamil Nadu Real Estate Market Intelligence & Prediction Dashboard."""
    re_html_path = BASE_DIR / "src/real_estate/dashboard/index.html"
    if not re_html_path.exists():
        raise HTTPException(status_code=404, detail="Real Estate Dashboard template not found.")
    return re_html_path.read_text(encoding="utf-8")


@app.get("/api/gold/regimes")
def get_gold_regimes():
    """Returns historical macroeconomic market regimes, annualized volatility, and returns."""
    regime_path = processed_dir / "regime_performance_metrics.csv"
    if not regime_path.exists():
        raise HTTPException(status_code=404, detail="Regime performance metrics not found.")

    df = pd.read_csv(regime_path)
    return {
        "status": "success",
        "total_regimes": len(df),
        "regimes": df.to_dict(orient="records")
    }


def _sanitize_data(obj: Any) -> Any:
    """Recursively replaces NaN, Inf, and non-serializable float values with None."""
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: _sanitize_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_data(v) for v in obj]
    return obj


@app.get("/api/gold/intelligence")
def get_gold_intelligence():
    """
    Unified Executive Intelligence Overview.
    Aggregates market regime, risk indicators, forecast consensus, prediction uncertainty,
    and macroeconomic driver signals.
    """
    try:
        # 1. Regime
        regime_engine = GoldRegimeEngine()
        regime_csv = processed_dir / "gold_regime_history.csv"
        if regime_csv.exists():
            df_reg = pd.read_csv(regime_csv)
            latest_reg = df_reg.iloc[-1].to_dict()
            reg_summary = {
                "latest_date": str(latest_reg["date"])[:10],
                "current_price_usd": float(latest_reg["close_usd_per_troy_oz"]),
                "current_regime": str(latest_reg["regime"]),
                "conviction_score": float(latest_reg["regime_conviction_score"]),
                "description": str(latest_reg["regime_description"]),
                "adx_14d": float(latest_reg["adx_14d"]) if pd.notna(latest_reg["adx_14d"]) else None,
                "sma_ratio": float(latest_reg["sma_ratio"]) if pd.notna(latest_reg["sma_ratio"]) else None
            }
        else:
            reg_summary = regime_engine.run_regime_intelligence()

        # 2. Risk Overview
        risk_json_path = processed_dir / "gold_risk_analytics.json"
        if risk_json_path.exists():
            with open(risk_json_path, "r", encoding="utf-8") as f:
                risk_data = json.load(f)
        else:
            risk_data = GoldRiskEngine().run_risk_analytics()

        # 3. Scenarios Overview
        scenarios_json_path = processed_dir / "gold_scenario_forecasts.json"
        if scenarios_json_path.exists():
            with open(scenarios_json_path, "r", encoding="utf-8") as f:
                scenarios_data = json.load(f)
        else:
            scenarios_data = GoldScenarioForecaster().generate_scenarios()

        # 4. Uncertainty Overview
        uncertainty_json_path = processed_dir / "gold_uncertainty_analytics.json"
        if uncertainty_json_path.exists():
            with open(uncertainty_json_path, "r", encoding="utf-8") as f:
                uncertainty_data = json.load(f)
        else:
            uncertainty_data = GoldUncertaintyEngine().run_uncertainty_pipeline()

        # 5. Macro Overview
        macro_collector = MacroIntelligenceCollector()
        macro_data = macro_collector.get_macro_overview()

        payload = {
            "status": "success",
            "observation_date": reg_summary["latest_date"],
            "current_price_usd": reg_summary["current_price_usd"],
            "all_time_high_usd": risk_data["drawdowns"]["all_time_high_usd"],
            "current_drawdown_pct": risk_data["drawdowns"]["current_drawdown_pct"],
            "regime_intelligence": {
                "regime": reg_summary["current_regime"],
                "conviction_score": reg_summary["conviction_score"],
                "description": reg_summary["description"],
                "trend_strength_adx": reg_summary["adx_14d"],
                "sma_cross_ratio": reg_summary["sma_ratio"]
            },
            "risk_profile": {
                "realized_vol_30d_pct": risk_data["volatility"]["realized_vol_30d_pct"],
                "full_series_vol_pct": risk_data["volatility"]["full_series_vol_pct"],
                "var_95pct_1d": risk_data["value_at_risk"]["metrics"]["var_95pct_1d"],
                "cvar_95pct_1d": risk_data["value_at_risk"]["metrics"]["cvar_95pct_1d"],
                "historical_max_drawdown_pct": risk_data["drawdowns"]["historical_max_drawdown_pct"]
            },
            "scenarios_consensus_365d": {
                "bullish_target_usd": scenarios_data["scenarios"]["bullish"]["horizon_projections"][-1]["target_price_usd"],
                "base_target_usd": scenarios_data["scenarios"]["base"]["horizon_projections"][-1]["target_price_usd"],
                "bearish_target_usd": scenarios_data["scenarios"]["bearish"]["horizon_projections"][-1]["target_price_usd"]
            },
            "uncertainty_intervals_30d": uncertainty_data["production_intervals"][0],
            "macro_signals_count": macro_data["total_indicators_tracked"]
        }
        return _sanitize_data(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate intelligence summary: {exc}")


@app.get("/api/gold/risk")
def get_gold_risk():
    """
    Comprehensive Gold Market Risk Analytics & Stress Testing.
    Returns realized volatilities (7d, 30d, 90d, full series), drawdown dynamics and recovery,
    Historical Simulation VaR and CVaR (95% and 99% for 1d and 10d), and 6 macroeconomic stress tests.
    """
    risk_json_path = processed_dir / "gold_risk_analytics.json"
    if risk_json_path.exists():
        with open(risk_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        engine = GoldRiskEngine()
        data = engine.run_risk_analytics()

    return {
        "status": "success",
        "risk_analytics": _sanitize_data(data)
    }


@app.get("/api/gold/scenarios")
def get_gold_scenarios():
    """
    Multi-Horizon Conditional Macroeconomic Scenario Forecasts.
    Returns Bullish, Base, and Bearish price trajectories, target ranges, macro assumptions,
    and risk factors across 30, 90, 180, and 365 trading-day horizons.
    """
    scenarios_json_path = processed_dir / "gold_scenario_forecasts.json"
    if scenarios_json_path.exists():
        with open(scenarios_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        engine = GoldScenarioForecaster()
        data = engine.generate_scenarios()

    return {
        "status": "success",
        "scenario_forecasts": _sanitize_data(data)
    }


@app.get("/api/gold/uncertainty")
def get_gold_uncertainty():
    """
    Prediction Uncertainty, Horizon-Specific Residual Calibration & Conformal Analysis.
    Returns 50%, 80%, and 95% multi-tier prediction intervals, validation-calibrated conformal multipliers,
    out-of-sample breach analysis (upper vs lower breaches), and 60-day rolling coverage.
    """
    uncertainty_json_path = processed_dir / "gold_uncertainty_analytics.json"
    if uncertainty_json_path.exists():
        with open(uncertainty_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        engine = GoldUncertaintyEngine()
        data = engine.run_uncertainty_pipeline()

    return {
        "status": "success",
        "uncertainty_engine": _sanitize_data(data)
    }


@app.get("/api/gold/macro")
def get_gold_macro():
    """
    Macroeconomic Intelligence Catalog & Point-in-Time Provenance.
    Tracks DXY, US 10Y Yield, US 10Y TIPS Real Yield, US CPI, USD/INR, Gold ETF Holdings,
    and Central Bank Purchases with documented providers, observation lags, and revision policies.
    """
    collector = MacroIntelligenceCollector()
    data = collector.get_macro_overview()
    return _sanitize_data(data)


@app.get("/api/gold/regime-history")
def get_gold_regime_history(
    limit: int = Query(default=100, ge=1, le=8000),
    regime: Optional[str] = Query(default=None, description="Filter by regime: 'Bullish', 'Bearish', 'Sideways', 'High Volatility'"),
    start_date: Optional[str] = Query(default=None, description="Format YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="Format YYYY-MM-DD")
):
    """
    Retrieves historical classified market regimes with timestamps and supporting indicator values
    (SMA50, SMA200, SMA ratio, ADX 14d, +DI, -DI, rolling 30d vol, 21d momentum).
    """
    # Try querying SQLite table
    query = "SELECT date, close_usd_per_troy_oz, regime, regime_conviction_score, sma_50d, sma_200d, sma_ratio, return_21d, return_63d, rolling_vol_30d, rolling_vol_90d, adx_14d, plus_di_14d, minus_di_14d, drawdown_63d_pct, regime_description FROM gold_regime_history WHERE 1=1"
    params = {}

    if regime:
        query += " AND regime = :regime"
        params["regime"] = regime
    if start_date:
        query += " AND date >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND date <= :end_date"
        params["end_date"] = end_date

    query += " ORDER BY date DESC LIMIT :limit"
    params["limit"] = limit

    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)
        raw_records = df.to_dict(orient="records")
        clean_records = _sanitize_data(raw_records)
        return {
            "status": "success",
            "total_returned": len(clean_records),
            "data": clean_records
        }
    except Exception as exc:
        # Fallback to CSV
        csv_path = processed_dir / "gold_regime_history.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path).sort_values("date", ascending=False)
            if regime:
                df = df[df["regime"] == regime]
            if start_date:
                df = df[df["date"] >= start_date]
            if end_date:
                df = df[df["date"] <= end_date]
            df = df.head(limit)
            clean_records = _sanitize_data(df.to_dict(orient="records"))
            return {
                "status": "success (csv_fallback)",
                "total_returned": len(clean_records),
                "data": clean_records
            }
        raise HTTPException(status_code=500, detail=f"Database and CSV lookup failed: {exc}")

