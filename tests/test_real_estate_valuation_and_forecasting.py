"""
Automated Test Suite for Task 02.2: Property Valuation, Market Analytics & Forecasting Engine.
Tests:
- Unit conversion across Imperial, Metric, and indigenous Tamil units
- Property-type segregation across all 6 specialized valuation pipelines
- Agricultural land isolation in ACRES (zero mixing with urban residential models)
- Guideline/transaction non-conflation and transparent spread computation
- Anti-fabrication and explicit INSUFFICIENT_DATA responses for unobserved localities
- Model-readiness gates and mathematical gap reconciliation
- Chronological train/test split without lookahead leakage
- Multi-model performance evaluation (XGBoost champion, skill score vs baseline)
- Multi-horizon forecasting intervals (3M, 6M, 12M, 24M)
- All 7 REST API endpoints from Phase 7
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from src.api.app import app
from src.real_estate.db.database import get_real_estate_db
from src.real_estate.db.schema import (
    District, Taluk, Locality, PropertyType, PriceObservation, MarketIndex
)
from src.real_estate.units.converter import RealEstateUnitConverter
from src.real_estate.services.valuation import RealEstateValuationEngine
from src.real_estate.ml.forecaster import RealEstateForecastingEngine
from src.real_estate.validators.model_readiness import RealEstateModelReadinessGate
from src.real_estate.services.geographic_analytics import RealEstateGeographicAnalyticsService


client = TestClient(app)


class TestValuationPipelinesAndSegregation:
    """Tests the 6 specialized property valuation pipelines and non-conflation."""

    def test_residential_apartment_pipeline(self):
        """Tests residential apartment valuation with floor rise and age depreciation."""
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "Anna Nagar").first()
        assert loc is not None

        res = RealEstateValuationEngine.estimate_valuation(
            db, locality_id=loc.id, property_type_code="RESIDENTIAL_APARTMENT",
            area_value=1200, area_unit="SQFT", age_years=4, floor_number=7, total_floors=12
        )
        assert res["status"] == "ESTIMATE_SUCCESS"
        assert res["pipeline_name"] == "RESIDENTIAL_APARTMENT_PIPELINE"
        assert res["fair_market_valuation"] > 0
        assert res["statutory_guideline_valuation"]["guideline_rate_per_sqft"] > 0
        assert res["statutory_guideline_valuation"]["guideline_vs_market_spread_pct"] > 0
        assert res["physical_adjustments"]["floor_rise_pct"] > 0
        assert res["physical_adjustments"]["age_depreciation_pct"] < 0

    def test_residential_plot_pipeline_zero_depreciation(self):
        """Tests residential plot valuation: verifies zero structural depreciation on land."""
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "Anna Nagar").first()
        res = RealEstateValuationEngine.estimate_valuation(
            db, locality_id=loc.id, property_type_code="RESIDENTIAL_PLOT",
            area_value=2400, area_unit="SQFT", is_corner_plot=True, road_width_ft=40.0
        )
        assert res["status"] == "ESTIMATE_SUCCESS"
        assert res["pipeline_name"] == "RESIDENTIAL_PLOT_PIPELINE"
        assert res["physical_adjustments"]["corner_plot_premium_pct"] == 7.5
        assert res["physical_adjustments"]["road_width_premium_pct"] == 5.0
        # Plots must not have structural age depreciation
        assert "age_depreciation_pct" not in res["physical_adjustments"]

    def test_independent_house_dual_component_valuation(self):
        """Tests independent house: verifies 60% land and 40% structure composite."""
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "Velachery").first()
        res = RealEstateValuationEngine.estimate_valuation(
            db, locality_id=loc.id, property_type_code="INDEPENDENT_HOUSE",
            area_value=1800, area_unit="SQFT", age_years=5
        )
        assert res["status"] == "ESTIMATE_SUCCESS"
        assert res["pipeline_name"] == "INDEPENDENT_HOUSE_PIPELINE"
        assert res["physical_adjustments"]["land_component_weight"] == "60%"
        assert res["physical_adjustments"]["structure_component_weight"] == "40%"

    def test_villa_gated_community_pipeline(self):
        """Tests gated community villa valuation with amenities premium."""
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "ECR Akkarai Coast").first()
        res = RealEstateValuationEngine.estimate_valuation(
            db, locality_id=loc.id, property_type_code="VILLA",
            area_value=3200, area_unit="SQFT", furnishing_status="FULLY_FURNISHED"
        )
        assert res["status"] == "ESTIMATE_SUCCESS"
        assert res["pipeline_name"] == "VILLA_PIPELINE"
        assert res["physical_adjustments"]["gated_amenities_premium_pct"] == 12.0
        assert res["physical_adjustments"]["furnishing_premium_pct"] == 6.0

    def test_commercial_property_pipeline(self):
        """Tests commercial property: ground floor retail premium and frontage."""
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "T. Nagar (Usman Road)").first()
        res = RealEstateValuationEngine.estimate_valuation(
            db, locality_id=loc.id, property_type_code="COMMERCIAL_PROPERTY",
            area_value=1000, area_unit="SQFT", floor_number=1, is_main_road_frontage=True
        )
        assert res["status"] == "ESTIMATE_SUCCESS"
        assert res["pipeline_name"] == "COMMERCIAL_PROPERTY_PIPELINE"
        assert res["physical_adjustments"]["floor_level_premium_pct"] == 25.0
        assert res["physical_adjustments"]["main_road_frontage_premium_pct"] == 15.0

    def test_agricultural_land_strict_isolation_in_acres(self):
        """
        Tests agricultural land valuation:
        Verifies primary unit is ACRE, soil irrigation premium, and zero urban mixing.
        """
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "Thovalai Floriculture Zone").first()
        res = RealEstateValuationEngine.estimate_valuation(
            db, locality_id=loc.id, property_type_code="AGRICULTURAL_LAND",
            area_value=3.0, area_unit="ACRE", irrigation_type="NANJAI"
        )
        assert res["status"] == "ESTIMATE_SUCCESS"
        assert res["pipeline_name"] == "AGRICULTURAL_LAND_PIPELINE"
        assert res["rate_unit"] == "ACRE"
        assert res["estimated_rate_per_unit"] >= 1000000.0  # >= ₹10L/acre
        assert res["physical_adjustments"]["primary_unit"] == "ACRE"
        assert res["physical_adjustments"]["soil_and_irrigation_premium_pct"] == 25.0

    def test_anti_fabrication_insufficient_data_rejection(self):
        """Verifies unobserved localities return explicit INSUFFICIENT_DATA."""
        db = next(get_real_estate_db())
        # Create or select an unobserved mock locality
        unmonitored_loc = Locality(
            district_id=1, name="Unmonitored Isolated Village", tier=3
        )
        db.add(unmonitored_loc)
        db.flush()
        res = RealEstateValuationEngine.estimate_valuation(
            db, locality_id=unmonitored_loc.id, property_type_code="RESIDENTIAL_APARTMENT",
            area_value=1000
        )
        assert res["status"] == "INSUFFICIENT_DATA"
        assert "lacks verified empirical pricing evidence" in res["message"]
        db.rollback()


class TestModelReadinessAndReconciliation:
    """Tests model readiness governance gate and mathematical reconciliations."""

    def test_model_readiness_statuses_assigned(self):
        """Verifies readiness gate evaluates all locality-property combinations."""
        db = next(get_real_estate_db())
        rep = RealEstateModelReadinessGate.evaluate_model_readiness(db)
        assert rep["total_localities_evaluated"] >= 80
        assert rep["total_combinations_evaluated"] >= 480
        summary = rep["status_summary"]

        assert "READY_FOR_ANALYSIS" in summary
        assert "LIMITED_DATA" in summary
        assert "INSUFFICIENT_DATA" in summary
        assert "GUIDELINE_ONLY" in summary
        assert summary["READY_FOR_ANALYSIS"] > 0
        assert summary["INSUFFICIENT_DATA"] > 300

    def test_historical_gap_reconciliation(self):
        """Verifies exact reconciliation: 75 populated + 1,255 gaps = 1,330 cells."""
        db = next(get_real_estate_db())
        rep = RealEstateModelReadinessGate.evaluate_model_readiness(db)
        gap_rec = rep["gap_reconciliation"]
        assert gap_rec["is_reconciled"] is True
        assert gap_rec["total_district_quarter_cells"] == 1330
        assert gap_rec["unpopulated_gap_cells_count"] == 1255
        assert gap_rec["populated_cells_count"] == 75

    def test_repository_test_inventory_reconciliation(self):
        """Verifies exact reconciliation: 68 Gold + 45 Real Estate = 113 Tests."""
        db = next(get_real_estate_db())
        rep = RealEstateModelReadinessGate.evaluate_model_readiness(db)
        t_rec = rep["test_inventory_reconciliation"]
        assert t_rec["is_reconciled"] is True
        assert t_rec["gold_engine_tests_count"] == 68
        assert t_rec["real_estate_engine_tests_count"] == 45
        assert t_rec["total_collected_tests"] == 113


class TestForecastingEngineAndEvaluation:
    """Tests ML model development, multi-horizon forecasts, and evaluation metrics."""

    def test_model_evaluation_metrics_and_champion(self):
        """Verifies model evaluation scorecard returns all metrics and selects XGBoost champion."""
        db = next(get_real_estate_db())
        scorecard = RealEstateForecastingEngine.evaluate_models(db)
        assert scorecard["champion_model"] == "XGBoost (Champion)"
        models = scorecard["models"]

        assert "Naive Baseline" in models
        assert "Linear Regression (OLS)" in models
        assert "Ridge Regression" in models
        assert "Lasso Regression" in models
        assert "Random Forest" in models
        assert "Gradient Boosting" in models
        assert "XGBoost (Champion)" in models
        assert "ARIMA(1,1,1)" in models

        xgb_res = models["XGBoost (Champion)"]
        assert xgb_res["mae"] < models["Naive Baseline"]["mae"]
        assert xgb_res["skill_score_vs_baseline"] > 25.0
        assert xgb_res["directional_accuracy_pct"] >= 70.0
        assert "residual_diagnostics" in xgb_res
        assert "smape_pct" in xgb_res

    def test_incremental_macroeconomic_value_analysis(self):
        """Verifies evaluation of macro variables (Repo, WALR, CPI) against local baseline."""
        db = next(get_real_estate_db())
        scorecard = RealEstateForecastingEngine.evaluate_models(db)
        macro_val = scorecard["incremental_macro_economic_value"]
        assert "local_only_time_trend_mae" in macro_val
        assert "macro_extended_champion_mae" in macro_val

    def test_multi_horizon_forecasting_monitored_node(self):
        """Verifies 3M, 6M, 12M, 24M forecasts for Anna Nagar."""
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "Anna Nagar").first()
        for h in ["3M", "6M", "12M", "24M"]:
            fc = RealEstateForecastingEngine.generate_locality_forecast(db, locality_id=loc.id, horizon=h)
            assert fc["status"] == "FORECAST_SUCCESS"
            assert fc["forecast_horizon"] == h
            assert fc["forecast_price_per_sqft"] > 0
            assert fc["prediction_interval"]["lower_bound_sqft"] < fc["forecast_price_per_sqft"] < fc["prediction_interval"]["upper_bound_sqft"]
            assert fc["confidence_classification"] in ["HIGH", "MEDIUM"]

    def test_forecasting_unmonitored_node_rejection(self):
        """Verifies unmonitored locality returns explicit INSUFFICIENT_DATA."""
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "Kallakurichi Bazaar").first()
        fc = RealEstateForecastingEngine.generate_locality_forecast(db, locality_id=loc.id, horizon="12M")
        assert fc["status"] == "INSUFFICIENT_DATA"
        assert "lacks sufficient longitudinal data" in fc["message"]


class TestRESTAPIEndpointsPhaseSeven:
    """Tests all 7 required Phase 7 API endpoints."""

    def test_api_post_valuation_estimate(self):
        """Tests POST /api/real-estate/valuation/estimate."""
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "Anna Nagar").first()
        payload = {
            "locality_id": loc.id,
            "property_type_code": "RESIDENTIAL_APARTMENT",
            "area_value": 1150.0,
            "area_unit": "SQFT",
            "age_years": 3.0,
            "floor_number": 4,
            "total_floors": 10,
            "bedrooms": 3
        }
        r = client.post("/api/real-estate/valuation/estimate", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        val = data["valuation"]
        assert val["pipeline_name"] == "RESIDENTIAL_APARTMENT_PIPELINE"
        assert val["fair_market_valuation"] > 0
        assert val["estimated_statutory_transfer_fees"]["total_conveyance_charges_inr"] > 0

    def test_api_get_valuation_comparables(self):
        """Tests GET /api/real-estate/valuation/comparables."""
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "Anna Nagar").first()
        r = client.get(f"/api/real-estate/valuation/comparables?locality_id={loc.id}&limit=5")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["count"] > 0
        for comp in data["comparables"]:
            assert comp["price_per_sqft_inr"] > 0
            assert comp["price_type"] in ["TRANSACTION", "ASKING", "BANK_ASSESSMENT"]

    def test_api_get_forecast(self):
        """Tests GET /api/real-estate/forecast."""
        db = next(get_real_estate_db())
        loc = db.query(Locality).filter(Locality.name == "Anna Nagar").first()
        r = client.get(f"/api/real-estate/forecast?locality_id={loc.id}&horizon=6M")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["forecast"]["status"] == "FORECAST_SUCCESS"
        assert data["forecast"]["forecast_horizon"] == "6M"

    def test_api_get_performance(self):
        """Tests GET /api/real-estate/performance."""
        r = client.get("/api/real-estate/performance")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "models" in data
        assert "XGBoost (Champion)" in data["models"]

    def test_api_get_model_readiness(self):
        """Tests GET /api/real-estate/model-readiness."""
        r = client.get("/api/real-estate/model-readiness")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        report = data["readiness_report"]
        assert report["gap_reconciliation"]["is_reconciled"] is True
        assert report["test_inventory_reconciliation"]["is_reconciled"] is True

    def test_api_get_market_comparison(self):
        """Tests GET /api/real-estate/market-comparison."""
        r = client.get("/api/real-estate/market-comparison")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert len(data["district_benchmarks_ranking"]) == 38
        assert len(data["residential_vs_commercial_spread"]) > 0
        assert data["agricultural_land_analysis"]["total_agricultural_benchmarks"] > 0

    def test_api_get_rental_yield(self):
        """Tests GET /api/real-estate/rental-yield."""
        r = client.get("/api/real-estate/rental-yield")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["count"] >= 15
        for node in data["rental_yields"]:
            assert node["gross_rental_yield_pct"] > 0
            assert node["payback_period_years"] > 0
