"""
test_dashboard_terminal.py — Acceptance and Integration Tests for TASK 04:
Gold Market Intelligence & Prediction Dashboard
"""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


class TestDashboardTerminalDelivery:
    """Verifies that the institutional terminal interface meets all Task 04 specifications."""

    def test_dashboard_endpoint_serves_html(self):
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        html = response.text
        assert "<!DOCTYPE html>" in html

    def test_dashboard_terminal_branding_and_sidebar(self):
        response = client.get("/dashboard")
        html = response.text

        # Sidebar navigation structure
        assert "sidebar" in html
        assert "Gold Intelligence" in html
        assert "Global Gold Investment Intelligence Engine" in html

        # Top navigation structure
        assert "topnav" in html
        assert "COMEX SPOT" in html
        assert "INR/10g" in html
        assert "REFRESH" in html

    def test_all_nine_dashboard_sections_present(self):
        response = client.get("/dashboard")
        html = response.text

        # Section A: Market Overview
        assert 'id="overview"' in html
        assert "Section A: Global Market Overview" in html
        assert "Global Spot Gold" in html
        assert "Indian Benchmark" in html

        # Section B: Gold Price Analysis
        assert 'id="analysis"' in html
        assert "Section B: Historical Price & Parity Analysis" in html
        assert "rangeFilterGroup" in html
        assert "btnSma50" in html
        assert "btnSma200" in html

        # Section C: Multi-Horizon Forecasting Engine
        assert 'id="forecasting"' in html
        assert "Section C: Multi-Horizon Forecasting Engine" in html
        assert "forecastHorizonFilter" in html
        assert "XGBoost (Champion)" in html

        # Section D: Market Regime Intelligence
        assert 'id="regimes"' in html
        assert "Section D: Market Regime Intelligence" in html
        assert "Trend Strength (ADX 14d)" in html
        assert "Historical Regime Distribution" in html

        # Section E: Risk Analytics
        assert 'id="risk"' in html
        assert "Section E: Risk Analytics & Stress Testing" in html
        assert "1-Day VaR (95%)" in html
        assert "Institutional Macro Shock Stress Tests" in html

        # Section F: Scenario Forecasting
        assert 'id="scenarios"' in html
        assert "Section F: Scenario Forecasting Engine" in html
        assert "EXPLICIT CONDITIONAL DISCLAIMER" in html
        assert "Bullish Thesis" in html
        assert "Base Consensus" in html
        assert "Bearish Thesis" in html

        # Section G: Prediction Uncertainty
        assert 'id="uncertainty"' in html
        assert "Section G: Conformal Prediction Uncertainty" in html
        assert "Out-of-Sample Calibration Audit" in html

        # Section H: Macroeconomic Drivers
        assert 'id="macro"' in html
        assert "Section H: Macroeconomic Drivers & Lineage" in html
        assert "US Dollar Index (DXY)" in html
        assert "Central Bank Net Purchases" in html

        # Section I: Model Performance
        assert 'id="performance"' in html
        assert "Section I: Model Performance & Walk-Forward Benchmark" in html
        assert "Master Benchmark Scorecard" in html


class TestBackendAPIEndpointsIntegrity:
    """Verifies that all 11 FastAPI endpoints return valid schemas and HTTP 200 without breakage."""

    def test_api_gold_history(self):
        r = client.get("/api/gold/history?limit=10")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 10
        row = data["data"][0]
        assert "close_usd_per_troy_oz" in row
        assert "gold_parity_inr_per_10g" in row
        assert "fx_usdinr" in row

    def test_api_gold_forecast(self):
        r = client.get("/api/gold/forecast")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "forecasts" in data
        assert len(data["forecasts"]) > 0

    def test_api_gold_metrics(self):
        r = client.get("/api/gold/metrics")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "models" in data
        assert len(data["models"]) > 0

    def test_api_gold_trends(self):
        r = client.get("/api/gold/trends")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "market_analysis" in data
        assert "current_regime" in data["market_analysis"]

    def test_api_gold_regimes(self):
        r = client.get("/api/gold/regimes")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "regimes" in data

    def test_api_gold_intelligence(self):
        r = client.get("/api/gold/intelligence")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["current_price_usd"] == 4073.00
        assert data["observation_date"] == "2026-11-04"
        assert "regime_intelligence" in data
        assert "risk_profile" in data
        assert "scenarios_consensus_365d" in data
        assert "uncertainty_intervals_30d" in data

    def test_api_gold_risk(self):
        r = client.get("/api/gold/risk")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "risk_analytics" in data
        assert "volatility" in data["risk_analytics"]
        assert "drawdowns" in data["risk_analytics"]
        assert "value_at_risk" in data["risk_analytics"]
        assert "stress_testing" in data["risk_analytics"]

    def test_api_gold_scenarios(self):
        r = client.get("/api/gold/scenarios")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "scenario_forecasts" in data
        scenarios = data["scenario_forecasts"]["scenarios"]
        assert "bullish" in scenarios
        assert "base" in scenarios
        assert "bearish" in scenarios

    def test_api_gold_uncertainty(self):
        r = client.get("/api/gold/uncertainty")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "uncertainty_engine" in data
        assert "production_intervals" in data["uncertainty_engine"]
        assert "test_uncertainty_audit" in data["uncertainty_engine"]

    def test_api_gold_macro(self):
        r = client.get("/api/gold/macro")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["total_indicators_tracked"] == 7
        assert "indicators" in data
        for k in ["DXY", "US10Y_YIELD", "US10Y_REAL_YIELD", "US_CPI", "USD_INR", "GOLD_ETF_HOLDINGS", "CENTRAL_BANK_PURCHASES"]:
            assert k in data["indicators"]

    def test_api_gold_regime_history(self):
        r = client.get("/api/gold/regime-history?limit=5")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 5
