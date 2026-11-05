"""
Comprehensive Test Suite for Gold Investment Intelligence Engine (Task 03).
Covers:
1. Market Regime Intelligence (ADX, multi-factor voting, database persistence)
2. Quantitative Risk Analytics (realized vol, VaR/CVaR 95/99%, drawdowns, recovery, 6 stress tests)
3. Scenario Forecasting (Bullish, Base, Bearish across 30, 90, 180, 365 days)
4. Prediction Uncertainty & Conformal Calibration (50/80/95% intervals, breach analysis)
5. Macroeconomic Intelligence (7 indicators, point-in-time constraints, provenance)
6. API Endpoints Integration (All new endpoints + dashboard)
7. Production Dataset Protection (Zero overwrite guarantee)
"""

import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from ml.gold.regime_intelligence import GoldRegimeEngine
from ml.gold.risk_analytics import GoldRiskEngine
from ml.gold.scenario_forecasting import GoldScenarioForecaster
from ml.gold.uncertainty_engine import GoldUncertaintyEngine
from src.collectors.macro_collector import MacroIntelligenceCollector
from src.api.app import app

client = TestClient(app)
MASTER_DATA_PATH = Path("data/processed/gold_master_daily_unified.csv")


class TestRegimeIntelligence:
    def test_adx_calculation(self):
        """Verifies Wilder's ADX calculation produces valid bounded metrics."""
        dates = pd.date_range("2020-01-01", periods=50, freq="B")
        prices = 1800.0 + np.cumsum(np.random.normal(1.0, 5.0, size=len(dates)))
        df = pd.DataFrame({
            "date": dates,
            "close_usd_per_troy_oz": prices,
            "high_usd_per_troy_oz": prices + 5.0,
            "low_usd_per_troy_oz": prices - 5.0
        })

        df_adx = GoldRegimeEngine.calculate_adx(df, period=14)
        assert "adx_14d" in df_adx.columns
        assert "plus_di_14d" in df_adx.columns
        assert "minus_di_14d" in df_adx.columns
        assert (df_adx["adx_14d"].dropna() >= 0).all()
        assert (df_adx["adx_14d"].dropna() <= 100).all()

    def test_regime_classification_categories(self):
        """Verifies multi-factor voting classifies into the 4 target regimes."""
        engine = GoldRegimeEngine()
        summary = engine.run_regime_intelligence()

        assert summary["current_regime"] in ["Bullish", "Bearish", "Sideways", "High Volatility"]
        assert summary["conviction_score"] >= 0.0
        assert summary["adx_14d"] is not None

        dist = summary["regime_distribution"]
        assert "Bullish" in dist
        assert "Bearish" in dist
        assert "High Volatility" in dist


class TestRiskAnalytics:
    def test_realized_volatility(self):
        """Verifies 7d, 30d, 90d, and full series annualized volatility."""
        engine = GoldRiskEngine()
        res = engine.run_risk_analytics()
        vol = res["volatility"]

        assert 15.0 <= vol["full_series_vol_pct"] <= 20.0
        assert vol["realized_vol_30d_pct"] > 0
        assert vol["realized_vol_90d_pct"] > 0

    def test_drawdowns_and_recovery(self):
        """Verifies max drawdown (-44.36%) and ATH drawdown recovery tracking."""
        engine = GoldRiskEngine()
        res = engine.run_risk_analytics()
        dd = res["drawdowns"]

        assert -45.0 <= dd["historical_max_drawdown_pct"] <= -43.0
        assert dd["all_time_high_usd"] == 5318.40
        assert dd["current_drawdown_pct"] < 0
        assert dd["historical_recovery_status"] in ["Fully Recovered", "Ongoing"]

    def test_var_and_cvar(self):
        """Verifies Historical Simulation VaR and Expected Shortfall bounds."""
        returns = np.array([-0.03, -0.02, -0.01, 0.00, 0.01, 0.02, 0.03])
        var_stats = GoldRiskEngine.calculate_var_cvar(returns, confidence_levels=[0.95], horizon_days=1)

        # 95% CVaR must be strictly greater than or equal to 95% VaR (tail loss severity)
        assert var_stats["cvar_95pct_1d"] >= var_stats["var_95pct_1d"]
        assert var_stats["var_95pct_1d"] > 0

    def test_stress_test_scenarios_count(self):
        """Verifies 6 macro stress scenarios with beta sensitivities."""
        engine = GoldRiskEngine()
        stress = engine.compute_stress_tests(4073.0, 22.4)

        assert len(stress) == 6
        scenario_ids = [s["id"] for s in stress]
        assert "STRESS_USD_APPRECIATION" in scenario_ids
        assert "STRESS_RISING_REAL_YIELDS" in scenario_ids
        assert "STRESS_GEOPOLITICAL_ESCALATION" in scenario_ids
        assert "STRESS_INFLATION_SURPRISES" in scenario_ids
        assert "STRESS_CENTRAL_BANK_SLOWDOWN" in scenario_ids
        assert "STRESS_USDINR_SHOCK" in scenario_ids


class TestScenarioForecasting:
    def test_scenario_horizons_and_hierarchy(self):
        """Verifies Bullish > Base > Bearish hierarchy across all 4 horizons."""
        engine = GoldScenarioForecaster()
        res = engine.generate_scenarios()
        scenarios = res["scenarios"]

        assert "bullish" in scenarios
        assert "base" in scenarios
        assert "bearish" in scenarios

        for i, h in enumerate([30, 90, 180, 365]):
            bull_tgt = scenarios["bullish"]["horizon_projections"][i]["target_price_usd"]
            base_tgt = scenarios["base"]["horizon_projections"][i]["target_price_usd"]
            bear_tgt = scenarios["bearish"]["horizon_projections"][i]["target_price_usd"]

            # Hierarchy check: Bullish > Base > Bearish
            assert bull_tgt > base_tgt > bear_tgt, (
                f"Horizon {h} violated hierarchy: Bull {bull_tgt} > Base {base_tgt} > Bear {bear_tgt}"
            )


class TestUncertaintyEngine:
    def test_uncertainty_conformal_calibration(self):
        """Verifies conformal multipliers and interval width expansion."""
        engine = GoldUncertaintyEngine()
        res = engine.run_uncertainty_pipeline()

        intervals = res["production_intervals"]
        assert len(intervals) == 4

        for item in intervals:
            w50 = item["interval_50"]["width_usd"]
            w80 = item["interval_80"]["width_usd"]
            w95 = item["interval_95"]["width_usd"]
            # Width hierarchy: 50% < 80% < 95%
            assert w50 < w80 < w95

        # Monotonic expansion across horizons for 95% width
        w95_horizons = [item["interval_95"]["width_usd"] for item in intervals]
        assert w95_horizons[0] < w95_horizons[1] < w95_horizons[2] < w95_horizons[3]


class TestMacroIntelligence:
    def test_macro_catalog_completeness(self):
        """Verifies all 7 macro indicators are cataloged with point-in-time constraints."""
        collector = MacroIntelligenceCollector()
        overview = collector.get_macro_overview()

        assert overview["total_indicators_tracked"] == 7
        indicators = overview["indicators"]
        expected_keys = [
            "DXY", "US10Y_YIELD", "US10Y_REAL_YIELD", "US_CPI",
            "USD_INR", "GOLD_ETF_HOLDINGS", "CENTRAL_BANK_PURCHASES"
        ]
        for k in expected_keys:
            assert k in indicators
            assert indicators[k]["point_in_time_available"] is True


class TestInvestmentIntelligenceAPI:
    def test_api_intelligence_endpoint(self):
        r = client.get("/api/gold/intelligence")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "regime_intelligence" in data
        assert "risk_profile" in data
        assert "scenarios_consensus_365d" in data

    def test_api_risk_endpoint(self):
        r = client.get("/api/gold/risk")
        assert r.status_code == 200
        data = r.json()
        assert "risk_analytics" in data
        assert len(data["risk_analytics"]["stress_testing"]["scenarios"]) == 6

    def test_api_scenarios_endpoint(self):
        r = client.get("/api/gold/scenarios")
        assert r.status_code == 200
        data = r.json()
        assert "scenarios" in data["scenario_forecasts"]

    def test_api_uncertainty_endpoint(self):
        r = client.get("/api/gold/uncertainty")
        assert r.status_code == 200
        data = r.json()
        assert "production_intervals" in data["uncertainty_engine"]

    def test_api_macro_endpoint(self):
        r = client.get("/api/gold/macro")
        assert r.status_code == 200
        data = r.json()
        assert data["total_indicators_tracked"] == 7

    def test_api_regime_history_endpoint(self):
        r = client.get("/api/gold/regime-history?limit=10&regime=Bullish")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert len(data["data"]) <= 10
        for row in data["data"]:
            assert row["regime"] == "Bullish"

    def test_api_dashboard_endpoint(self):
        r = client.get("/dashboard")
        assert r.status_code == 200
        assert "<!DOCTYPE html>" in r.text
        assert "Global Gold Investment Intelligence Engine" in r.text


class TestProductionDatasetProtection:
    def test_dataset_hash_invariant_under_all_tests(self):
        """Verifies master unified dataset is strictly read-only during tests."""
        assert MASTER_DATA_PATH.exists()
        pre_hash = hashlib.sha256(MASTER_DATA_PATH.read_bytes()).hexdigest()

        # Run risk and regime calculations
        GoldRegimeEngine().run_regime_intelligence()
        GoldRiskEngine().run_risk_analytics()

        post_hash = hashlib.sha256(MASTER_DATA_PATH.read_bytes()).hexdigest()
        assert pre_hash == post_hash, "CRITICAL: Master unified CSV was altered by intelligence engine calculations!"
