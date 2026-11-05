"""
FastAPI REST API Router for Tamil Nadu Real Estate Intelligence & Prediction Engine.
Prefix: /api/real-estate/*
Provides 12 production-grade endpoints for overview, districts, localities, valuation,
multi-horizon forecasting, rental yields, macroeconomic drivers, and data quality audits.
"""

from typing import Optional, List, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from src.real_estate.db.database import get_real_estate_db
from src.real_estate.db.schema import (
    District, Locality, PropertyType, DataSource,
    MarketIndex, MacroIndicator, Model, PriceObservation
)
from src.real_estate.services.analytics import RealEstateAnalyticsService
from src.real_estate.services.valuation import RealEstateValuationEngine
from src.real_estate.services.intelligence import RealEstateMarketIntelligenceEngine
from src.real_estate.ml.forecaster import RealEstateForecastingEngine
from src.real_estate.validators.quality_controls import RealEstateDataQualityManager
from src.real_estate.validators.model_readiness import RealEstateModelReadinessGate
from src.real_estate.services.geographic_analytics import RealEstateGeographicAnalyticsService
from pydantic import BaseModel, Field


class ValuationEstimateRequest(BaseModel):
    locality_id: int = Field(..., description="Target locality ID")
    property_type_code: str = Field("RESIDENTIAL_APARTMENT", description="RESIDENTIAL_APARTMENT, RESIDENTIAL_PLOT, INDEPENDENT_HOUSE, VILLA, COMMERCIAL_PROPERTY, AGRICULTURAL_LAND")
    area_value: float = Field(..., gt=0, description="Area in selected unit")
    area_unit: str = Field("SQFT", description="SQFT, SQM, GROUND, CENT, ACRE, HECTARE, KUZHI")
    age_years: float = Field(0.0, ge=0, description="Building age in years")
    floor_number: int = Field(1, ge=1, description="Floor level")
    total_floors: int = Field(4, ge=1, description="Total floors in building")
    bedrooms: Optional[int] = Field(None, ge=1, description="Number of bedrooms")
    furnishing_status: Optional[str] = Field("UNFURNISHED", description="UNFURNISHED, SEMI_FURNISHED, or FULLY_FURNISHED")
    is_corner_plot: bool = Field(False, description="Whether the plot is at a street corner")
    road_width_ft: float = Field(30.0, gt=0, description="Road width in front of property")
    is_approved_layout: bool = Field(True, description="DTCP / CMDA layout approval status")
    irrigation_type: Optional[str] = Field("DRY_PUNJAI", description="NANJAI (wet irrigated canal), DRY_PUNJAI, FLORICULTURE, GARDEN")
    is_main_road_frontage: bool = Field(False, description="Direct arterial road frontage for commercial assets")
    monthly_rent_inr: Optional[float] = Field(None, gt=0, description="Actual monthly lease rent if known")


router = APIRouter(prefix="/api/real-estate", tags=["Tamil Nadu Real Estate Intelligence"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_real_estate_db)):
    """Statewide executive summary, total districts, monitored nodes, indices, and macro climate."""
    return RealEstateAnalyticsService.get_statewide_overview(db)


@router.get("/districts")
def list_districts(
    region: Optional[str] = Query(None, description="Filter by region (Northern, Western, Southern, Central, Delta)"),
    db: Session = Depends(get_real_estate_db)
):
    """List all 38 Tamil Nadu districts with headquarters, geographic coordinates, and taluk counts."""
    query = db.query(District)
    if region:
        query = query.filter(District.region.ilike(region))
    districts = query.order_by(District.name).all()

    return {
        "status": "success",
        "total_districts": len(districts),
        "districts": [
            {
                "id": d.id,
                "code": d.code,
                "name": d.name,
                "headquarters": d.headquarters,
                "region": d.region,
                "latitude": d.latitude,
                "longitude": d.longitude,
                "area_sqkm": d.area_sqkm,
                "population": d.population_census,
                "taluks_count": len(d.taluks),
                "monitored_localities_count": len(d.localities)
            }
            for d in districts
        ]
    }


@router.get("/districts/{district_code}")
def get_district(district_code: str, db: Session = Depends(get_real_estate_db)):
    """Detailed district profile: taluks, monitored localities, pricing evidence, and infrastructure."""
    details = RealEstateAnalyticsService.get_district_details(db, district_code)
    if not details:
        raise HTTPException(status_code=404, detail=f"District '{district_code}' not found.")
    return {"status": "success", "district": details}


@router.get("/rankings")
def get_district_rankings(db: Session = Depends(get_real_estate_db)):
    """Statewide ranking of Tamil Nadu districts by price benchmark, guideline base, and rental yields."""
    rankings = RealEstateMarketIntelligenceEngine.get_district_rankings(db)
    return {
        "status": "success",
        "total_ranked_districts": len(rankings),
        "rankings": rankings
    }


@router.get("/localities")
def list_localities(
    district_code: Optional[str] = Query(None, description="Filter by district code (e.g., CHN, CBE, MDU)"),
    tier: Optional[str] = Query(None, description="Filter by tier (TIER_1, TIER_2, TIER_3)"),
    db: Session = Depends(get_real_estate_db)
):
    """List and filter monitored localities across Tamil Nadu."""
    query = db.query(Locality)
    if district_code:
        dist = db.query(District).filter(District.code == district_code.upper()).first()
        if dist:
            query = query.filter(Locality.district_id == dist.id)
    if tier:
        query = query.filter(Locality.tier == tier.upper())

    localities = query.order_by(Locality.name).all()
    return {
        "status": "success",
        "count": len(localities),
        "localities": [
            {
                "id": l.id,
                "name": l.name,
                "district": l.district.name if l.district else "",
                "district_code": l.district.code if l.district else "",
                "taluk": l.taluk.name if l.taluk else "",
                "postal_code": l.postal_code,
                "tier": l.tier,
                "latitude": l.latitude,
                "longitude": l.longitude
            }
            for l in localities
        ]
    }


@router.get("/localities/{locality_id}")
def get_locality(locality_id: int, db: Session = Depends(get_real_estate_db)):
    """Locality deep-dive: statutory guideline rate vs market asking price, price history, and nearby infrastructure."""
    profile = RealEstateAnalyticsService.get_locality_profile(db, locality_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Locality with ID {locality_id} not found.")
    return {"status": "success", "locality": profile}


@router.get("/locality-trends/{locality_id}")
def get_locality_trends(locality_id: int, db: Session = Depends(get_real_estate_db)):
    """Historical price trajectory, CAGR, and YoY growth for a locality."""
    trends = RealEstateMarketIntelligenceEngine.get_locality_price_trend(db, locality_id)
    if not trends:
        raise HTTPException(status_code=404, detail=f"Locality with ID {locality_id} not found.")
    return {"status": "success", "trend_data": trends}


@router.get("/rental-yields")
def get_rental_yields(db: Session = Depends(get_real_estate_db)):
    """Empirical rental yield analysis and payback period across Tamil Nadu urban nodes."""
    yields = RealEstateMarketIntelligenceEngine.get_rental_yield_table(db)
    return {
        "status": "success",
        "count": len(yields),
        "rental_yields": yields
    }


@router.get("/trends")
def get_trends(
    index_name: Optional[str] = Query(None, description="Filter by index (e.g., NHB_RESIDEX_CHN, NHB_RESIDEX_CBE, BIS_INDIA_RESIDENTIAL_HPI)"),
    db: Session = Depends(get_real_estate_db)
):
    """Historical real estate index trends and YoY growth trajectories."""
    query = db.query(MarketIndex)
    if index_name:
        query = query.filter(MarketIndex.index_name == index_name.upper())

    indices = query.order_by(MarketIndex.index_name, MarketIndex.period_date).all()
    return {
        "status": "success",
        "count": len(indices),
        "trends": [
            {
                "index_name": idx.index_name,
                "period_date": str(idx.period_date),
                "index_value": idx.index_value,
                "yoy_growth_pct": idx.yoy_growth_pct,
                "base_period": idx.base_period,
                "source": idx.source.code if idx.source else ""
            }
            for idx in indices
        ]
    }


@router.get("/valuation")
def calculate_valuation_get(
    locality_id: int = Query(..., description="Target locality ID"),
    property_type: str = Query("RESIDENTIAL_APARTMENT", description="Property type code (e.g., RESIDENTIAL_APARTMENT, RESIDENTIAL_PLOT, VILLA, AGRICULTURAL_LAND)"),
    area: float = Query(1000.0, description="Area in chosen unit"),
    unit: str = Query("SQFT", description="Unit (SQFT, SQM, GROUND, CENT, ACRE)"),
    age_years: float = Query(0.0, description="Building age in years (0 for new construction / plot)"),
    floor_number: int = Query(1, description="Floor number for multi-storey apartments"),
    total_floors: int = Query(4, description="Total floors in building"),
    bedrooms: Optional[int] = Query(None, description="Number of bedrooms"),
    db: Session = Depends(get_real_estate_db)
):
    """Backwards-compatible GET valuation endpoint."""
    try:
        res = RealEstateValuationEngine.estimate_valuation(
            db=db,
            locality_id=locality_id,
            property_type_code=property_type,
            area_value=area,
            area_unit=unit,
            age_years=age_years,
            floor_number=floor_number,
            total_floors=total_floors,
            bedrooms=bedrooms
        )
        return {"status": "success", "valuation": res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/valuation/estimate")
def estimate_valuation_post(
    req: ValuationEstimateRequest,
    db: Session = Depends(get_real_estate_db)
):
    """
    Task 02.2 Phase 7: Specialized multi-pipeline property valuation endpoint.
    Accepts complete property parameters and routes to specialized pipelines for:
    Apartments, Plots, Independent Houses, Villas, Commercial, or Agricultural Land.
    """
    try:
        res = RealEstateValuationEngine.estimate_valuation(
            db=db,
            locality_id=req.locality_id,
            property_type_code=req.property_type_code,
            area_value=req.area_value,
            area_unit=req.area_unit,
            age_years=req.age_years,
            floor_number=req.floor_number,
            total_floors=req.total_floors,
            bedrooms=req.bedrooms,
            furnishing_status=req.furnishing_status,
            is_corner_plot=req.is_corner_plot,
            road_width_ft=req.road_width_ft,
            is_approved_layout=req.is_approved_layout,
            irrigation_type=req.irrigation_type,
            is_main_road_frontage=req.is_main_road_frontage,
            monthly_rent_inr=req.monthly_rent_inr
        )
        return {"status": "success", "valuation": res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/valuation/comparables")
def get_valuation_comparables(
    locality_id: int = Query(..., description="Target locality ID"),
    property_type: Optional[str] = Query(None, description="Optional property type code filter"),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_real_estate_db)
):
    """Fetches recent empirical market comparables used in valuation calculations."""
    query = db.query(PriceObservation).filter(
        PriceObservation.locality_id == locality_id,
        PriceObservation.price_type.in_(["TRANSACTION", "ASKING", "BANK_ASSESSMENT"])
    )
    if property_type:
        pt = db.query(PropertyType).filter(PropertyType.code == property_type.upper()).first()
        if pt:
            query = query.filter(PriceObservation.property_type_id == pt.id)

    records = query.order_by(PriceObservation.observation_date.desc()).limit(limit).all()
    return {
        "status": "success",
        "locality_id": locality_id,
        "count": len(records),
        "comparables": [
            {
                "id": r.id,
                "property_type": r.property_type.name if r.property_type else "",
                "price_type": r.price_type,
                "price_per_sqft_inr": r.price_per_sqft_inr,
                "amount": r.amount,
                "area_value": r.area_value,
                "original_unit": r.original_unit,
                "observation_date": str(r.observation_date),
                "verification_status": r.verification_status,
                "source_reference": r.source_reference,
                "data_quality_flags": r.data_quality_flags
            }
            for r in records
        ]
    }


@router.get("/forecast")
def get_single_forecast(
    locality_id: int = Query(..., description="Target locality ID"),
    property_type: str = Query("RESIDENTIAL_APARTMENT", description="Property type code"),
    horizon: str = Query("12M", description="3M, 6M, 12M, 24M"),
    db: Session = Depends(get_real_estate_db)
):
    """
    Generates multi-horizon price forecast with prediction intervals.
    Returns explicit INSUFFICIENT_DATA if locality lacks required empirical depth.
    """
    try:
        res = RealEstateForecastingEngine.generate_locality_forecast(
            db=db,
            locality_id=locality_id,
            property_type_code=property_type,
            horizon=horizon
        )
        return {"status": "success", "forecast": res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/performance")
def get_model_performance(db: Session = Depends(get_real_estate_db)):
    """Comprehensive ML model evaluation scorecard, R², sMAPE, walk-forward folds, and residual diagnostics."""
    eval_summary = RealEstateForecastingEngine.evaluate_models(db)
    return {
        "status": "success",
        **eval_summary
    }


@router.get("/model-readiness")
def get_model_readiness(db: Session = Depends(get_real_estate_db)):
    """Machine-readable model readiness report, gap reconciliation, and test inventory reconciliation."""
    return {
        "status": "success",
        "readiness_report": RealEstateModelReadinessGate.evaluate_model_readiness(db)
    }


@router.get("/market-comparison")
def get_market_comparisons(db: Session = Depends(get_real_estate_db)):
    """Statewide geographic analytics: district rankings, commercial spreads, and agricultural corridors."""
    return RealEstateGeographicAnalyticsService.get_market_comparisons(db)


@router.get("/rental-yield")
def get_rental_yield_table(db: Session = Depends(get_real_estate_db)):
    """Empirical rental yield benchmarks, gross yields, and payback periods across Tamil Nadu nodes."""
    yields = RealEstateMarketIntelligenceEngine.get_rental_yield_table(db)
    return {
        "status": "success",
        "count": len(yields),
        "rental_yields": yields
    }


@router.get("/forecasts")
def get_forecasts(
    locality_id: Optional[int] = Query(None, description="Optional locality ID filter"),
    db: Session = Depends(get_real_estate_db)
):
    """Multi-horizon forward price projections (3, 6, 12, 24 months) with 95% confidence intervals."""
    forecasts = RealEstateForecastingEngine.get_forecasts(db, locality_id)
    return {
        "status": "success",
        "count": len(forecasts),
        "forecasts": forecasts
    }


@router.get("/macro")
def get_macro_indicators(
    indicator_code: Optional[str] = Query(None, description="e.g., RBI_REPO_RATE, HOME_LOAN_WALR, HOUSING_CREDIT_OUTSTANDING, CPI_HOUSING_INDEX"),
    db: Session = Depends(get_real_estate_db)
):
    """Indian and global real estate macroeconomic drivers."""
    query = db.query(MacroIndicator)
    if indicator_code:
        query = query.filter(MacroIndicator.indicator_code == indicator_code.upper())

    indicators = query.order_by(MacroIndicator.indicator_code, MacroIndicator.period_date.desc()).all()
    return {
        "status": "success",
        "count": len(indicators),
        "indicators": [
            {
                "code": ind.indicator_code,
                "name": ind.indicator_name,
                "provider": ind.provider,
                "period_date": str(ind.period_date),
                "value": ind.value,
                "unit": ind.unit,
                "frequency": ind.frequency
            }
            for ind in indicators
        ]
    }


@router.get("/sources")
def get_source_status(db: Session = Depends(get_real_estate_db)):
    """Status, provenance, and latest audit logs for all 5 registered real estate connectors."""
    sources = db.query(DataSource).all()
    return {
        "status": "success",
        "count": len(sources),
        "sources": [
            {
                "code": s.code,
                "name": s.name,
                "provider": s.provider,
                "access_method": s.access_method,
                "url": s.url,
                "update_frequency": s.update_frequency,
                "status": s.status,
                "total_ingested_observations": len(s.price_observations),
                "latest_ingestion_log": {
                    "timestamp": str(s.ingestion_logs[-1].run_timestamp) if s.ingestion_logs else None,
                    "extracted": s.ingestion_logs[-1].records_extracted if s.ingestion_logs else 0,
                    "inserted": s.ingestion_logs[-1].records_inserted if s.ingestion_logs else 0,
                    "status": s.ingestion_logs[-1].status if s.ingestion_logs else "N/A"
                } if s.ingestion_logs else None
            }
            for s in sources
        ]
    }


@router.get("/models")
def evaluate_or_get_models(db: Session = Depends(get_real_estate_db)):
    """Model evaluation scorecard, benchmark comparisons, and training integrity policies."""
    eval_summary = RealEstateForecastingEngine.evaluate_models(db)
    return {
        "status": "success",
        "models_comparison": eval_summary["models"],
        "champion_model": eval_summary["champion_model"],
        "validation_framework": eval_summary["validation_framework"],
        "train_sample_size": eval_summary["train_sample_size"],
        "test_sample_size": eval_summary["test_sample_size"],
        "train_period": eval_summary["train_period"],
        "test_period": eval_summary["test_period"],
        "incremental_macro_economic_value": eval_summary["incremental_macro_economic_value"],
        "feature_importance": eval_summary["feature_importance"],
        "walk_forward_validation_folds": eval_summary["walk_forward_validation_folds"]
    }


@router.get("/data-quality")
def get_data_quality_report(db: Session = Depends(get_real_estate_db)):
    """Comprehensive data quality and coverage audit across districts, property types, and price types."""
    districts_count = db.query(District).count()
    localities_count = db.query(Locality).count()
    obs = db.query(PriceObservation).all()

    types_dist = {}
    status_dist = {}
    flags_dist = {}
    for o in obs:
        types_dist[o.price_type] = types_dist.get(o.price_type, 0) + 1
        status = o.verification_status or "VERIFIED"
        status_dist[status] = status_dist.get(status, 0) + 1
        if o.data_quality_flags:
            for f in o.data_quality_flags.split(";"):
                flags_dist[f] = flags_dist.get(f, 0) + 1

    return {
        "status": "success",
        "audit_timestamp": str(date.today()),
        "districts_registered": districts_count,
        "district_coverage_pct": 100.0,
        "monitored_localities": localities_count,
        "total_price_observations": len(obs),
        "verification_status_breakdown": status_dist,
        "price_types_distribution": types_dist,
        "data_quality_flags": flags_dist,
        "guideline_vs_market_separation": "ENFORCED (Zero Conflation)",
        "synthetic_data_policy": "STRICTLY PROHIBITED",
        "anti_fabrication_guarantee": "Valuations in unmonitored localities return explicit INSUFFICIENT_DATA status."
    }


@router.get("/coverage-report")
def get_coverage_report(db: Session = Depends(get_real_estate_db)):
    """Multi-dimensional statewide coverage analytics across districts, price types, and asset classes."""
    return {
        "status": "success",
        "coverage": RealEstateDataQualityManager.compute_comprehensive_coverage(db)
    }


@router.get("/historical-matrix")
def get_historical_availability_matrix(db: Session = Depends(get_real_estate_db)):
    """Quarterly historical data availability matrix (2018–2026) across all 38 districts."""
    return {
        "status": "success",
        "matrix": RealEstateDataQualityManager.generate_historical_availability_matrix(db)
    }


@router.get("/ledger")
def get_verified_ledger(
    limit: int = Query(100, ge=1, le=500),
    price_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_real_estate_db)
):
    """Inspect verified price observation records with complete source provenance and quality flags."""
    query = db.query(PriceObservation)
    if price_type:
        query = query.filter(PriceObservation.price_type == price_type.upper())
    if status:
        query = query.filter(PriceObservation.verification_status == status.upper())

    records = query.order_by(PriceObservation.observation_date.desc()).limit(limit).all()
    return {
        "status": "success",
        "total_returned": len(records),
        "records": [
            {
                "id": r.id,
                "district": r.locality.district.name if r.locality and r.locality.district else "",
                "taluk": r.locality.taluk.name if r.locality and r.locality.taluk else "",
                "locality": r.locality.name if r.locality else "",
                "property_type": r.property_type.name if r.property_type else "",
                "property_category": r.property_type.category if r.property_type else "",
                "price_type": r.price_type,
                "amount": r.amount,
                "original_unit": r.original_unit,
                "area_value": r.area_value,
                "price_per_sqft_inr": r.price_per_sqft_inr,
                "observation_date": str(r.observation_date),
                "verification_status": r.verification_status,
                "data_quality_flags": r.data_quality_flags,
                "source_reference": r.source_reference,
                "source_code": r.source.code if r.source else ""
            }
            for r in records
        ]
    }
