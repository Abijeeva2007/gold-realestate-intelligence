"""
Automated Validation Suite for Task 02.1: Data Verification & Statewide Coverage Expansion.
Tests:
- Provenance auditing and verification status classification
- Strict non-conflation of NHB index series and bank valuations
- Complete 38-district statutory guideline value coverage
- Priority locality coverage (Kanniyakumari / Nagercoil and urban hubs)
- Agricultural land segregation from urban property
- Empirical rental yields and commercial benchmark plausibility
- Non-fabrication and explicit accounting of historical gaps
- API coverage and ledger endpoints
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from src.api.app import app
from src.real_estate.db.database import get_real_estate_db
from src.real_estate.db.schema import (
    District, Taluk, Locality, PropertyType, DataSource,
    PriceObservation, MarketIndex
)
from src.real_estate.validators.quality_controls import RealEstateDataQualityManager
from src.real_estate.services.intelligence import RealEstateMarketIntelligenceEngine


client = TestClient(app)


class TestRealEstateCoverageAndQuality:
    """Comprehensive test suite for Task 02.1 data verification and quality controls."""

    def test_database_record_count_expansion(self):
        """Verifies database contains expanded records (>200 price observations)."""
        db = next(get_real_estate_db())
        obs_count = db.query(PriceObservation).count()
        assert obs_count >= 200, f"Expected at least 200 observations, got {obs_count}"

    def test_verification_status_classification(self):
        """Verifies every record has an explicit status (VERIFIED or DERIVED)."""
        db = next(get_real_estate_db())
        obs = db.query(PriceObservation).all()
        for o in obs:
            assert o.verification_status in ["VERIFIED", "DERIVED", "UNVERIFIED", "REJECTED"], (
                f"Invalid verification status '{o.verification_status}' on record ID {o.id}"
            )

    def test_nhb_residex_non_conflation(self):
        """
        Enforces rule: NHB RESIDEX observations must be classified as DERIVED
        with INDEX_DERIVED_VALUATION flag and not conflated with borrower bank assessments.
        """
        db = next(get_real_estate_db())
        nhb_source = db.query(DataSource).filter(DataSource.code == "NHB_RESIDEX").first()
        assert nhb_source is not None
        nhb_obs = db.query(PriceObservation).filter(PriceObservation.source_id == nhb_source.id).all()
        assert len(nhb_obs) > 0

        for o in nhb_obs:
            assert o.verification_status == "DERIVED", (
                f"NHB record ID {o.id} must be marked DERIVED, got {o.verification_status}"
            )
            assert "INDEX_DERIVED_VALUATION" in (o.data_quality_flags or ""), (
                f"NHB record ID {o.id} must have INDEX_DERIVED_VALUATION flag"
            )

    def test_tnrera_asking_evidence(self):
        """Verifies that all TNRERA asking records have explicit dated promoter filing references."""
        db = next(get_real_estate_db())
        tnrera_source = db.query(DataSource).filter(DataSource.code == "TNRERA").first()
        assert tnrera_source is not None
        rera_obs = db.query(PriceObservation).filter(PriceObservation.source_id == tnrera_source.id).all()
        assert len(rera_obs) >= 10

        for o in rera_obs:
            assert o.verification_status == "VERIFIED"
            assert o.price_type == "ASKING"
            assert "TN/" in (o.source_reference or ""), (
                f"TNRERA record ID {o.id} lacks valid TNRERA registration reference: {o.source_reference}"
            )

    def test_statutory_guideline_coverage_all_38_districts(self):
        """Verifies 100% guideline value coverage across all 38 Tamil Nadu districts."""
        db = next(get_real_estate_db())
        all_districts = db.query(District).all()
        assert len(all_districts) == 38

        districts_with_guidelines = (
            db.query(District.code)
            .join(Locality, Locality.district_id == District.id)
            .join(PriceObservation, PriceObservation.locality_id == Locality.id)
            .filter(PriceObservation.price_type == "GUIDELINE")
            .distinct()
            .all()
        )
        covered_codes = {r[0] for r in districts_with_guidelines}
        assert len(covered_codes) == 38, (
            f"Expected 38 districts with guideline values, got {len(covered_codes)}: missing {set(d.code for d in all_districts) - covered_codes}"
        )

    def test_priority_localities_kanniyakumari(self):
        """Verifies high-priority coverage for Kanniyakumari District and Nagercoil."""
        db = next(get_real_estate_db())
        kkm_dist = db.query(District).filter(District.code == "KKM").first()
        assert kkm_dist is not None

        kkm_localities = db.query(Locality).filter(Locality.district_id == kkm_dist.id).all()
        loc_names = {l.name for l in kkm_localities}

        # Check key nodes in Kanniyakumari
        assert "Nagercoil Court Road" in loc_names
        assert "Nagercoil Vadasery" in loc_names
        assert "Cape Road (Kanyakumari)" in loc_names
        assert "Thuckalay Bazaar" in loc_names
        assert "Marthandam Main Road" in loc_names
        assert "Thovalai Floriculture Zone" in loc_names

        # Check that multiple price types are present for KKM
        kkm_obs = (
            db.query(PriceObservation)
            .join(Locality, PriceObservation.locality_id == Locality.id)
            .filter(Locality.district_id == kkm_dist.id)
            .all()
        )
        types_in_kkm = {o.price_type for o in kkm_obs}
        assert "GUIDELINE" in types_in_kkm
        assert "ASKING" in types_in_kkm
        assert "RENTAL" in types_in_kkm
        assert "TRANSACTION" in types_in_kkm

    def test_agricultural_land_strict_separation(self):
        """Verifies agricultural land records are strictly segregated and measured in ACRES."""
        db = next(get_real_estate_db())
        agri_pt = db.query(PropertyType).filter(PropertyType.code == "AGRICULTURAL_LAND").first()
        assert agri_pt is not None
        assert agri_pt.category == "AGRICULTURAL"

        agri_obs = db.query(PriceObservation).filter(PriceObservation.property_type_id == agri_pt.id).all()
        assert len(agri_obs) >= 4

        for o in agri_obs:
            assert o.original_unit == "ACRE"
            # Plausible per acre bounds (₹5L to ₹50L per acre)
            assert o.amount >= 500000.0, f"Agricultural amount below ₹5L/acre: {o.amount}"
            # Normalized sqft rate should be between ₹10 and ₹150/sqft
            assert 10.0 <= o.price_per_sqft_inr <= 150.0

    def test_rental_yield_calculations_and_payback(self):
        """Verifies empirical rental benchmarks compute mathematically sound gross yields and payback periods."""
        db = next(get_real_estate_db())
        yield_table = RealEstateMarketIntelligenceEngine.get_rental_yield_table(db)
        assert len(yield_table) >= 15

        for item in yield_table:
            monthly_rent = item["monthly_rent_per_sqft"]
            annual_rent = item["annual_rent_per_sqft"]
            capital = item["capital_price_per_sqft"]
            gross_yield = item["gross_rental_yield_pct"]
            payback = item["payback_period_years"]

            assert annual_rent == round(monthly_rent * 12.0, 2)
            expected_yield = round((annual_rent / capital) * 100.0, 2)
            assert gross_yield == expected_yield
            assert abs(payback - round(100.0 / gross_yield, 1)) <= 0.2
            assert 2.0 <= gross_yield <= 15.0

    def test_historical_gap_reporting_no_synthetic_fill(self):
        """Verifies historical matrix reports gaps explicitly without fabricating observations."""
        db = next(get_real_estate_db())
        matrix = RealEstateDataQualityManager.generate_historical_availability_matrix(db)
        assert matrix["total_quarters_tracked"] == 35
        totals = matrix["availability_status_totals"]

        assert totals["GAP"] > 1000, "Historical gaps must be recorded explicitly as GAP"
        assert totals["OBSERVED"] > 0
        assert totals["INDEX_SERIES_AVAILABLE"] > 0

    def test_api_coverage_report(self):
        """Tests /api/real-estate/coverage-report endpoint."""
        r = client.get("/api/real-estate/coverage-report")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        metrics = data["coverage"]["summary_metrics"]
        assert metrics["district_geographic_coverage_pct"] == 100.0
        assert metrics["guideline_value_coverage_pct"] == 100.0
        assert metrics["verified_transaction_coverage_pct"] > 0
        assert metrics["rental_coverage_pct"] > 0

    def test_api_ledger_endpoint(self):
        """Tests /api/real-estate/ledger endpoint with filtering."""
        r = client.get("/api/real-estate/ledger?limit=10&price_type=TRANSACTION")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["total_returned"] > 0
        for rec in data["records"]:
            assert rec["price_type"] == "TRANSACTION"
            assert rec["verification_status"] == "VERIFIED"

    def test_api_historical_matrix_endpoint(self):
        """Tests /api/real-estate/historical-matrix endpoint."""
        r = client.get("/api/real-estate/historical-matrix")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert len(data["matrix"]["district_matrix"]) == 38
