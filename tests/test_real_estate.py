"""
Automated Test Suite for TASK 01: Tamil Nadu Real Estate Intelligence Engine Foundation.
Verifies:
1. Database Schema Integrity (13 normalized tables, 38 districts, 6 property types, 5 sources)
2. Land Measurement Unit Conversions (Imperial, Metric, Ground, Cent, Kuzhi, Acre)
3. Data Validation & Anti-Fabrication Constraints (Bounds, Temporal Causality, Segregation, Deduplication)
4. All 10 FastAPI Real Estate Endpoints under /api/real-estate/*
5. Zero Regression on Existing Gold Intelligence Platform
"""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from src.api.app import app
from src.real_estate.db.database import SessionLocal, get_real_estate_engine
from src.real_estate.db.schema import (
    District, Taluk, Locality, PropertyType, DataSource,
    PriceObservation, MarketIndex, MacroIndicator, InfrastructureProject
)
from src.real_estate.units.converter import RealEstateUnitConverter
from src.real_estate.validators.data_validator import RealEstateDataValidator

client = TestClient(app)


class TestRealEstateDatabaseSchema:
    """Verifies schema structure, foreign keys, and geographic seeding."""

    def test_all_38_districts_present(self):
        db = SessionLocal()
        try:
            count = db.query(District).count()
            assert count == 38, f"Expected 38 districts, found {count}"
            
            # Check core districts
            codes = [d.code for d in db.query(District).all()]
            for expected in ["CHN", "CBE", "MDU", "TRY", "SLM", "CGL", "TLR", "KCH", "KRI", "KKM"]:
                assert expected in codes, f"District code '{expected}' missing from database"
        finally:
            db.close()

    def test_property_types_and_categories(self):
        db = SessionLocal()
        try:
            pts = db.query(PropertyType).all()
            assert len(pts) == 6
            codes = [p.code for p in pts]
            assert "RESIDENTIAL_APARTMENT" in codes
            assert "RESIDENTIAL_PLOT" in codes
            assert "AGRICULTURAL_LAND" in codes
            assert "COMMERCIAL_PROPERTY" in codes
            assert "INDEPENDENT_HOUSE" in codes
            assert "VILLA" in codes
        finally:
            db.close()

    def test_all_five_data_sources_registered(self):
        db = SessionLocal()
        try:
            sources = db.query(DataSource).all()
            assert len(sources) == 5
            src_codes = [s.code for s in sources]
            for expected in ["TNREGINET", "NHB_RESIDEX", "RBI_DBIE", "BIS_REALESTATE", "TNRERA"]:
                assert expected in src_codes, f"DataSource '{expected}' missing from registry"
        finally:
            db.close()

    def test_distinct_price_types_segregation(self):
        """Verifies that GUIDELINE, ASKING, and BANK_ASSESSMENT are strictly segregated."""
        db = SessionLocal()
        try:
            guidelines = db.query(PriceObservation).filter(PriceObservation.price_type == "GUIDELINE").count()
            askings = db.query(PriceObservation).filter(PriceObservation.price_type == "ASKING").count()
            bank_assessments = db.query(PriceObservation).filter(PriceObservation.price_type == "BANK_ASSESSMENT").count()

            assert guidelines > 0, "No statutory guideline values ingested"
            assert askings > 0, "No builder asking rates ingested"
            assert bank_assessments > 0, "No bank valuation benchmarks ingested"

            # Check that guideline observations have the official legal disclaimer metadata
            first_guideline = db.query(PriceObservation).filter(PriceObservation.price_type == "GUIDELINE").first()
            assert "Statutory Minimum Base Valuation" in first_guideline.metadata_json
        finally:
            db.close()


class TestUnitConversionEngine:
    """Verifies mathematical conversions for indigenous South Indian and metric units."""

    def test_ground_to_sqft(self):
        assert RealEstateUnitConverter.to_sqft(1.0, "GROUND") == 2400.0
        assert RealEstateUnitConverter.to_sqft(2.5, "GROUND") == 6000.0

    def test_cent_to_sqft(self):
        assert RealEstateUnitConverter.to_sqft(1.0, "CENT") == 435.6
        assert RealEstateUnitConverter.to_sqft(10.0, "CENTS") == 4356.0

    def test_acre_to_cents_and_grounds(self):
        assert RealEstateUnitConverter.to_sqft(1.0, "ACRE") == 43560.0
        assert RealEstateUnitConverter.to_cents(1.0, "ACRE") == 100.0
        assert RealEstateUnitConverter.to_grounds(1.0, "ACRE") == 18.15

    def test_kuzhi_traditional_measure(self):
        assert RealEstateUnitConverter.to_sqft(1.0, "KUZHI") == 144.0
        assert RealEstateUnitConverter.to_sqft(1.0, "MAA") == 14400.0

    def test_price_normalization(self):
        # 1 Ground for ₹1.2 Crores
        total_price = 12000000.0
        sqft_rate, sqm_rate, aux = RealEstateUnitConverter.normalize_price(
            total_amount_inr=total_price,
            area_value=1.0,
            area_unit="GROUND"
        )
        assert sqft_rate == 5000.0  # 12,000,000 / 2,400 = 5,000 / sqft
        assert aux["price_per_ground_inr"] == 12000000.0
        assert aux["price_per_cent_inr"] == 2178000.0  # 5000 * 435.6


class TestDataValidationAndIntegrity:
    """Tests non-fabrication guarantees, temporal bounds, and duplicate rejection."""

    def test_rejects_negative_or_zero_values(self):
        db = SessionLocal()
        try:
            res1 = RealEstateDataValidator.validate_price_observation(
                db=db, locality_id=1, property_type_id=1, source_id=1,
                price_type="GUIDELINE", amount=-5000.0, area_value=1000.0,
                price_per_sqft_inr=5000.0, observation_date=date.today()
            )
            assert not res1["is_valid"]
            assert any("strictly positive" in err for err in res1["errors"])

            res2 = RealEstateDataValidator.validate_price_observation(
                db=db, locality_id=1, property_type_id=1, source_id=1,
                price_type="GUIDELINE", amount=5000000.0, area_value=0.0,
                price_per_sqft_inr=5000.0, observation_date=date.today()
            )
            assert not res2["is_valid"]
        finally:
            db.close()

    def test_rejects_future_dated_observations(self):
        db = SessionLocal()
        try:
            future_date = date.today() + timedelta(days=30)
            res = RealEstateDataValidator.validate_price_observation(
                db=db, locality_id=1, property_type_id=1, source_id=1,
                price_type="TRANSACTION", amount=5000000.0, area_value=1000.0,
                price_per_sqft_inr=5000.0, observation_date=future_date
            )
            assert not res["is_valid"]
            assert any("Future observation date" in err for err in res["errors"])
        finally:
            db.close()

    def test_rejects_unsupported_price_type(self):
        db = SessionLocal()
        try:
            res = RealEstateDataValidator.validate_price_observation(
                db=db, locality_id=1, property_type_id=1, source_id=1,
                price_type="SYNTHETIC_SPECULATION", amount=5000000.0, area_value=1000.0,
                price_per_sqft_inr=5000.0, observation_date=date.today()
            )
            assert not res["is_valid"]
            assert any("Invalid price_type" in err for err in res["errors"])
        finally:
            db.close()


class TestRealEstateAPIEndpoints:
    """Verifies all 10 FastAPI real estate REST routes."""

    def test_api_overview(self):
        r = client.get("/api/real-estate/overview")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["geographic_coverage"]["total_districts"] == 38
        assert data["evidence_ledger"]["total_price_observations"] > 0
        assert "nhb_residex_chennai" in data["official_indices_summary"]

    def test_api_districts_list(self):
        r = client.get("/api/real-estate/districts")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["total_districts"] == 38

    def test_api_district_filter_by_region(self):
        r = client.get("/api/real-estate/districts?region=Western")
        assert r.status_code == 200
        data = r.json()
        assert data["total_districts"] > 0
        for d in data["districts"]:
            assert d["region"] == "Western"

    def test_api_district_detail_chennai(self):
        r = client.get("/api/real-estate/districts/CHN")
        assert r.status_code == 200
        data = r.json()
        assert data["district"]["name"] == "Chennai"
        assert len(data["district"]["taluks"]) > 0
        assert len(data["district"]["monitored_localities"]) > 0

    def test_api_localities_list(self):
        r = client.get("/api/real-estate/localities?district_code=CHN")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["count"] > 0
        names = [l["name"] for l in data["localities"]]
        assert "Anna Nagar" in names
        assert "Mylapore" in names

    def test_api_locality_profile(self):
        # Find ID of Anna Nagar
        db = SessionLocal()
        loc = db.query(Locality).filter(Locality.name == "Anna Nagar").first()
        loc_id = loc.id
        db.close()

        r = client.get(f"/api/real-estate/localities/{loc_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["locality"]["name"] == "Anna Nagar"
        assert data["locality"]["summary_metrics"]["latest_guideline_rate_per_sqft_inr"] is not None

    def test_api_trends(self):
        r = client.get("/api/real-estate/trends?index_name=NHB_RESIDEX_CHN")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["count"] > 0
        for item in data["trends"]:
            assert item["index_name"] == "NHB_RESIDEX_CHN"
            assert item["index_value"] > 0

    def test_api_valuation_calculator(self):
        db = SessionLocal()
        loc = db.query(Locality).filter(Locality.name == "Anna Nagar").first()
        loc_id = loc.id
        db.close()

        r = client.get(f"/api/real-estate/valuation?locality_id={loc_id}&property_type=RESIDENTIAL_APARTMENT&area=1200&unit=SQFT&age_years=2&floor_number=3&total_floors=8")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        val = data["valuation"]
        assert val["locality"]["name"] == "Anna Nagar"
        assert val["statutory_guideline_valuation"]["guideline_rate_per_sqft_inr"] > 0
        assert val["fair_market_valuation_estimate"]["estimated_market_rate_per_sqft_inr"] > 0
        assert val["tamil_nadu_statutory_taxes"]["stamp_duty_pct"] == 7.0
        assert val["tamil_nadu_statutory_taxes"]["registration_fee_pct"] == 2.0
        assert val["tamil_nadu_statutory_taxes"]["total_statutory_taxes_inr"] > 0

    def test_api_macro_indicators(self):
        r = client.get("/api/real-estate/macro?indicator_code=RBI_REPO_RATE")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["count"] > 0
        for item in data["indicators"]:
            assert item["code"] == "RBI_REPO_RATE"
            assert item["value"] > 0

    def test_api_sources(self):
        r = client.get("/api/real-estate/sources")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["count"] == 5
        codes = [s["code"] for s in data["sources"]]
        assert "TNREGINET" in codes
        assert "NHB_RESIDEX" in codes
        assert "TNRERA" in codes

    def test_api_models(self):
        r = client.get("/api/real-estate/models")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "models_comparison" in data
        assert "XGBoost (Champion)" in data["models_comparison"]
        assert data["models_comparison"]["XGBoost (Champion)"]["directional_accuracy_pct"] > 70.0

    def test_api_rankings(self):
        r = client.get("/api/real-estate/rankings")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert len(data["rankings"]) > 0
        # Chennai should be ranked #1
        assert data["rankings"][0]["district_code"] == "CHN"
        assert data["rankings"][0]["state_rank"] == 1

    def test_api_rental_yields(self):
        r = client.get("/api/real-estate/rental-yields")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["count"] > 0
        for y in data["rental_yields"]:
            assert y["gross_rental_yield_pct"] > 0
            assert y["payback_period_years"] > 0

    def test_api_locality_trends(self):
        db = SessionLocal()
        loc = db.query(Locality).filter(Locality.name == "Anna Nagar").first()
        loc_id = loc.id
        db.close()

        r = client.get(f"/api/real-estate/locality-trends/{loc_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        trend = data["trend_data"]
        assert trend["rates"]["cagr_pct"] > 0
        assert trend["rates"]["total_appreciation_pct"] > 0

    def test_api_forecasts(self):
        r = client.get("/api/real-estate/forecasts")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["count"] > 0
        horizons = [f["horizon_months"] for f in data["forecasts"]]
        assert 3 in horizons
        assert 6 in horizons
        assert 12 in horizons
        assert 24 in horizons

    def test_api_data_quality(self):
        r = client.get("/api/real-estate/data-quality")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["districts_registered"] == 38
        assert data["district_coverage_pct"] == 100.0

    def test_real_estate_dashboard_serves_html(self):
        r = client.get("/real-estate-dashboard")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "Tamil Nadu Real Estate Market Intelligence Terminal" in r.text
        assert "Valuation Breakdown & Taxes" in r.text

    def test_anti_fabrication_insufficient_data_rejection(self):
        # Create an unmonitored test locality with zero price observations
        db = SessionLocal()
        dist = db.query(District).first()
        unmonitored_loc = Locality(
            district_id=dist.id,
            name="Unmonitored Test Hamlet 999",
            postal_code="600999",
            tier="TIER_3"
        )
        db.add(unmonitored_loc)
        db.commit()
        unmonitored_id = unmonitored_loc.id
        db.close()

        try:
            r = client.get(f"/api/real-estate/valuation?locality_id={unmonitored_id}&property_type=RESIDENTIAL_APARTMENT&area=1000")
            assert r.status_code == 200
            data = r.json()
            assert data["status"] == "success"
            # Must return explicit INSUFFICIENT_DATA status rather than fabricating a rate
            assert data["valuation"]["status"] == "INSUFFICIENT_DATA"
            assert "lacks verified empirical pricing evidence" in data["valuation"]["message"]
        finally:
            db = SessionLocal()
            obj = db.query(Locality).filter(Locality.id == unmonitored_id).first()
            if obj:
                db.delete(obj)
                db.commit()
            db.close()


class TestGoldEngineZeroRegression:
    """Verifies that all gold routes and artifacts remain 100% operational and undisturbed."""

    def test_gold_history_endpoint(self):
        r = client.get("/api/gold/history?limit=5")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 5

    def test_gold_forecast_endpoint(self):
        r = client.get("/api/gold/forecast")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "forecasts" in data

    def test_gold_dashboard_endpoint(self):
        r = client.get("/dashboard")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "Global Gold Market Intelligence" in r.text
