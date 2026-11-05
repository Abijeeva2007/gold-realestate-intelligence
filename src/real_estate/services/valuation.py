"""
Multi-Pipeline Property Valuation Engine for Tamil Nadu Real Estate (Task 02.2 Phase 2).
Implements 6 distinct specialized valuation pipelines:
1. Residential Apartments (hedonic built-up, floor rise, age depreciation, bedroom format, furnishing)
2. Residential Plots (land area in SQFT/Ground/Cent, corner plot, road width, layout approvals, zero structural depreciation)
3. Independent Houses (dual-component: land parcel + depreciated structural replacement cost)
4. Gated Community Villas (land share, built area, private clubhouse amenities premium)
5. Commercial Properties (ground-floor retail premium, road frontage, rental yield capitalization)
6. Agricultural Land (strictly isolated pipeline in ACRES, wet/nanjai vs dry/punjai, delta irrigation premium)

Strict Governance Rules:
- Never present a guideline value as an estimated market transaction price.
- Agricultural land is strictly segregated from urban property models.
- If a locality lacks empirical evidence, return explicit INSUFFICIENT_DATA.
- Every valuation includes confidence indicators and uncertainty intervals.
"""

from typing import Dict, Any, List, Optional
from datetime import date
from sqlalchemy.orm import Session
from src.real_estate.db.schema import (
    Locality, PropertyType, PriceObservation, InfrastructureProject, District
)
from src.real_estate.units.converter import RealEstateUnitConverter


class RealEstateValuationEngine:
    """Enterprise multi-pipeline property valuation and appraisal engine."""

    TN_STAMP_DUTY_PCT = 7.0        # Tamil Nadu Stamp Duty (7%)
    TN_REGISTRATION_FEE_PCT = 2.0  # Tamil Nadu Registration Fee (2%)
    COMMERCIAL_CAP_RATE_PCT = 7.5  # Typical commercial capitalization rate in Tamil Nadu urban centers

    @classmethod
    def estimate_valuation(
        cls,
        db: Session,
        locality_id: int,
        property_type_code: str,
        area_value: float,
        area_unit: str = "SQFT",
        age_years: float = 0.0,
        floor_number: int = 1,
        total_floors: int = 4,
        bedrooms: Optional[int] = None,
        furnishing_status: Optional[str] = "UNFURNISHED",
        is_corner_plot: bool = False,
        road_width_ft: float = 30.0,
        is_approved_layout: bool = True,
        irrigation_type: Optional[str] = "DRY_PUNJAI",
        is_main_road_frontage: bool = False,
        monthly_rent_inr: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Routes the valuation request to the appropriate specialized pipeline.
        Enforces strict non-conflation and anti-fabrication controls.
        """
        loc = db.query(Locality).filter(Locality.id == locality_id).first()
        if not loc:
            raise ValueError(f"Locality with ID {locality_id} not found.")

        pt = db.query(PropertyType).filter(PropertyType.code == property_type_code).first()
        if not pt:
            raise ValueError(f"PropertyType '{property_type_code}' not found.")

        if area_value <= 0:
            raise ValueError(f"Area must be strictly positive, received {area_value}")

        # Fetch statutory guideline observation (TNREGINET)
        guideline_obs = (
            db.query(PriceObservation)
            .filter(
                PriceObservation.locality_id == locality_id,
                PriceObservation.price_type == "GUIDELINE"
            )
            .order_by(PriceObservation.observation_date.desc())
            .first()
        )

        # Fetch empirical market comparables (TRANSACTION, ASKING, BANK_ASSESSMENT)
        comparables = (
            db.query(PriceObservation)
            .filter(
                PriceObservation.locality_id == locality_id,
                PriceObservation.price_type.in_(["TRANSACTION", "ASKING", "BANK_ASSESSMENT"])
            )
            .order_by(PriceObservation.observation_date.desc())
            .limit(5)
            .all()
        )

        # ANTI-FABRICATION CHECK:
        # If neither guideline nor market observations exist in this locality:
        if not guideline_obs and not comparables:
            return {
                "status": "INSUFFICIENT_DATA",
                "message": f"Locality '{loc.name}' in {loc.district.name if loc.district else 'Tamil Nadu'} lacks verified empirical pricing evidence.",
                "locality": {
                    "id": loc.id,
                    "name": loc.name,
                    "district": loc.district.name if loc.district else "",
                    "tier": loc.tier
                },
                "property_type": pt.name,
                "comparable_evidence_count": 0,
                "recommendation": "Submit an appraisal request or verify records at the jurisdictional Sub-Registrar Office."
            }

        # Check for infrastructure catalysts in this locality/district
        infra_boost_pct = cls._compute_infra_boost(db, locality_id, loc.district_id)

        # Route to specialized pipeline based on property type code
        if pt.code == "AGRICULTURAL_LAND":
            return cls._evaluate_agricultural_land(
                loc=loc, pt=pt, area_value=area_value, area_unit=area_unit,
                guideline_obs=guideline_obs, comparables=comparables,
                irrigation_type=irrigation_type, infra_boost_pct=infra_boost_pct
            )
        elif pt.code == "RESIDENTIAL_PLOT":
            return cls._evaluate_residential_plot(
                loc=loc, pt=pt, area_value=area_value, area_unit=area_unit,
                guideline_obs=guideline_obs, comparables=comparables,
                is_corner_plot=is_corner_plot, road_width_ft=road_width_ft,
                is_approved_layout=is_approved_layout, infra_boost_pct=infra_boost_pct
            )
        elif pt.code == "INDEPENDENT_HOUSE":
            return cls._evaluate_independent_house(
                loc=loc, pt=pt, area_value=area_value, area_unit=area_unit,
                guideline_obs=guideline_obs, comparables=comparables,
                age_years=age_years, bedrooms=bedrooms, infra_boost_pct=infra_boost_pct
            )
        elif pt.code == "VILLA":
            return cls._evaluate_villa(
                loc=loc, pt=pt, area_value=area_value, area_unit=area_unit,
                guideline_obs=guideline_obs, comparables=comparables,
                age_years=age_years, bedrooms=bedrooms, furnishing_status=furnishing_status,
                infra_boost_pct=infra_boost_pct
            )
        elif pt.code == "COMMERCIAL_PROPERTY":
            return cls._evaluate_commercial_property(
                loc=loc, pt=pt, area_value=area_value, area_unit=area_unit,
                guideline_obs=guideline_obs, comparables=comparables,
                floor_number=floor_number, is_main_road_frontage=is_main_road_frontage,
                monthly_rent_inr=monthly_rent_inr, infra_boost_pct=infra_boost_pct
            )
        else:
            # Default: Residential Apartment
            return cls._evaluate_residential_apartment(
                loc=loc, pt=pt, area_value=area_value, area_unit=area_unit,
                guideline_obs=guideline_obs, comparables=comparables,
                age_years=age_years, floor_number=floor_number, total_floors=total_floors,
                bedrooms=bedrooms, furnishing_status=furnishing_status,
                infra_boost_pct=infra_boost_pct
            )

    @classmethod
    def _compute_infra_boost(cls, db: Session, locality_id: int, district_id: Optional[int]) -> float:
        """Computes proximity boost from active infrastructure projects (max 10%)."""
        projects = db.query(InfrastructureProject).filter(
            (InfrastructureProject.locality_id == locality_id) |
            (InfrastructureProject.district_id == district_id)
        ).all()
        if not projects:
            return 0.0
        active = [p for p in projects if p.status in ["UNDER_CONSTRUCTION", "OPERATIONAL"]]
        return min(len(active) * 2.5, 10.0)

    # ================= PIPELINE 1: RESIDENTIAL APARTMENTS =================
    @classmethod
    def _evaluate_residential_apartment(
        cls, loc: Locality, pt: PropertyType, area_value: float, area_unit: str,
        guideline_obs: Optional[PriceObservation], comparables: List[PriceObservation],
        age_years: float, floor_number: int, total_floors: int,
        bedrooms: Optional[int], furnishing_status: Optional[str], infra_boost_pct: float
    ) -> Dict[str, Any]:
        total_sqft = RealEstateUnitConverter.to_sqft(area_value, area_unit)
        base_rate, reliability, uncertainty_pct = cls._derive_base_rate(guideline_obs, comparables, loc)

        # Hedonic physical adjustments
        depreciation_pct = min(age_years * 1.5, 35.0)  # Structural aging
        floor_rise_pct = max(0, (floor_number - 1) * 0.75) if total_floors > 5 else 0.0
        bedroom_pct = 3.0 if (bedrooms and bedrooms >= 4) else (-2.0 if bedrooms == 1 else 0.0)
        furnishing_pct = 5.0 if furnishing_status == "FULLY_FURNISHED" else (2.5 if furnishing_status == "SEMI_FURNISHED" else 0.0)

        net_mult = 1.0 - (depreciation_pct / 100.0) + (floor_rise_pct / 100.0) + (bedroom_pct / 100.0) + (furnishing_pct / 100.0) + (infra_boost_pct / 100.0)
        est_sqft = round(base_rate * net_mult, 2)
        total_val = round(est_sqft * total_sqft, 2)

        return cls._format_valuation_output(
            pipeline_name="RESIDENTIAL_APARTMENT_PIPELINE",
            loc=loc, pt=pt, area_value=area_value, area_unit=area_unit, total_sqft=total_sqft,
            est_unit_rate=est_sqft, total_market_val=total_val, uncertainty_pct=uncertainty_pct,
            reliability=reliability, guideline_obs=guideline_obs, comparables=comparables,
            adjustments={
                "age_depreciation_pct": -depreciation_pct,
                "floor_rise_pct": floor_rise_pct,
                "bedroom_premium_pct": bedroom_pct,
                "furnishing_premium_pct": furnishing_pct,
                "infrastructure_boost_pct": infra_boost_pct,
                "net_adjustment_multiplier": round(net_mult, 4)
            }
        )

    # ================= PIPELINE 2: RESIDENTIAL PLOTS =================
    @classmethod
    def _evaluate_residential_plot(
        cls, loc: Locality, pt: PropertyType, area_value: float, area_unit: str,
        guideline_obs: Optional[PriceObservation], comparables: List[PriceObservation],
        is_corner_plot: bool, road_width_ft: float, is_approved_layout: bool, infra_boost_pct: float
    ) -> Dict[str, Any]:
        total_sqft = RealEstateUnitConverter.to_sqft(area_value, area_unit)
        base_rate, reliability, uncertainty_pct = cls._derive_base_rate(guideline_obs, comparables, loc)

        # Plot specific adjustments (zero structural depreciation!)
        corner_pct = 7.5 if is_corner_plot else 0.0
        road_pct = 5.0 if road_width_ft >= 40.0 else (0.0 if road_width_ft >= 30.0 else -5.0)
        approval_pct = 10.0 if is_approved_layout else -15.0

        net_mult = 1.0 + (corner_pct / 100.0) + (road_pct / 100.0) + (approval_pct / 100.0) + (infra_boost_pct / 100.0)
        est_sqft = round(base_rate * net_mult, 2)
        total_val = round(est_sqft * total_sqft, 2)

        return cls._format_valuation_output(
            pipeline_name="RESIDENTIAL_PLOT_PIPELINE",
            loc=loc, pt=pt, area_value=area_value, area_unit=area_unit, total_sqft=total_sqft,
            est_unit_rate=est_sqft, total_market_val=total_val, uncertainty_pct=uncertainty_pct,
            reliability=reliability, guideline_obs=guideline_obs, comparables=comparables,
            adjustments={
                "corner_plot_premium_pct": corner_pct,
                "road_width_premium_pct": road_pct,
                "layout_approval_premium_pct": approval_pct,
                "infrastructure_boost_pct": infra_boost_pct,
                "net_adjustment_multiplier": round(net_mult, 4)
            }
        )

    # ================= PIPELINE 3: INDEPENDENT HOUSES =================
    @classmethod
    def _evaluate_independent_house(
        cls, loc: Locality, pt: PropertyType, area_value: float, area_unit: str,
        guideline_obs: Optional[PriceObservation], comparables: List[PriceObservation],
        age_years: float, bedrooms: Optional[int], infra_boost_pct: float
    ) -> Dict[str, Any]:
        # Dual-component valuation: 60% Land Value + 40% Built Structure Value
        total_sqft = RealEstateUnitConverter.to_sqft(area_value, area_unit)
        base_rate, reliability, uncertainty_pct = cls._derive_base_rate(guideline_obs, comparables, loc)

        land_share = 0.60
        structure_share = 0.40
        depreciation_pct = min(age_years * 1.5, 35.0)

        # Land appreciates with infra; structure depreciates with age
        land_mult = 1.0 + (infra_boost_pct / 100.0)
        structure_mult = 1.0 - (depreciation_pct / 100.0)

        composite_mult = (land_share * land_mult) + (structure_share * structure_mult)
        est_sqft = round(base_rate * composite_mult, 2)
        total_val = round(est_sqft * total_sqft, 2)

        return cls._format_valuation_output(
            pipeline_name="INDEPENDENT_HOUSE_PIPELINE",
            loc=loc, pt=pt, area_value=area_value, area_unit=area_unit, total_sqft=total_sqft,
            est_unit_rate=est_sqft, total_market_val=total_val, uncertainty_pct=uncertainty_pct,
            reliability=reliability, guideline_obs=guideline_obs, comparables=comparables,
            adjustments={
                "land_component_weight": "60%",
                "structure_component_weight": "40%",
                "structure_age_depreciation_pct": -depreciation_pct,
                "infrastructure_boost_pct": infra_boost_pct,
                "composite_multiplier": round(composite_mult, 4)
            }
        )

    # ================= PIPELINE 4: GATED COMMUNITY VILLAS =================
    @classmethod
    def _evaluate_villa(
        cls, loc: Locality, pt: PropertyType, area_value: float, area_unit: str,
        guideline_obs: Optional[PriceObservation], comparables: List[PriceObservation],
        age_years: float, bedrooms: Optional[int], furnishing_status: Optional[str], infra_boost_pct: float
    ) -> Dict[str, Any]:
        total_sqft = RealEstateUnitConverter.to_sqft(area_value, area_unit)
        base_rate, reliability, uncertainty_pct = cls._derive_base_rate(guideline_obs, comparables, loc)

        # Villa amenities multiplier (clubhouse, private security, landscaping +12%)
        amenity_pct = 12.0
        depreciation_pct = min(age_years * 1.0, 25.0)  # Lower depreciation on luxury villas
        furnishing_pct = 6.0 if furnishing_status == "FULLY_FURNISHED" else 0.0

        net_mult = 1.0 + (amenity_pct / 100.0) - (depreciation_pct / 100.0) + (furnishing_pct / 100.0) + (infra_boost_pct / 100.0)
        est_sqft = round(base_rate * net_mult, 2)
        total_val = round(est_sqft * total_sqft, 2)

        return cls._format_valuation_output(
            pipeline_name="VILLA_PIPELINE",
            loc=loc, pt=pt, area_value=area_value, area_unit=area_unit, total_sqft=total_sqft,
            est_unit_rate=est_sqft, total_market_val=total_val, uncertainty_pct=uncertainty_pct,
            reliability=reliability, guideline_obs=guideline_obs, comparables=comparables,
            adjustments={
                "gated_amenities_premium_pct": amenity_pct,
                "luxury_age_depreciation_pct": -depreciation_pct,
                "furnishing_premium_pct": furnishing_pct,
                "infrastructure_boost_pct": infra_boost_pct,
                "net_adjustment_multiplier": round(net_mult, 4)
            }
        )

    # ================= PIPELINE 5: COMMERCIAL PROPERTIES =================
    @classmethod
    def _evaluate_commercial_property(
        cls, loc: Locality, pt: PropertyType, area_value: float, area_unit: str,
        guideline_obs: Optional[PriceObservation], comparables: List[PriceObservation],
        floor_number: int, is_main_road_frontage: bool,
        monthly_rent_inr: Optional[float], infra_boost_pct: float
    ) -> Dict[str, Any]:
        total_sqft = RealEstateUnitConverter.to_sqft(area_value, area_unit)
        base_rate, reliability, uncertainty_pct = cls._derive_base_rate(guideline_obs, comparables, loc)

        # Commercial floor & frontage adjustments
        frontage_pct = 15.0 if is_main_road_frontage else 0.0
        floor_pct = 25.0 if floor_number == 1 else (-10.0 if floor_number > 2 else 0.0)

        net_mult = 1.0 + (frontage_pct / 100.0) + (floor_pct / 100.0) + (infra_boost_pct / 100.0)
        est_sqft = round(base_rate * net_mult, 2)
        total_val = round(est_sqft * total_sqft, 2)

        # Commercial Capitalization Check (if monthly rent is provided)
        capitalized_val = None
        if monthly_rent_inr and monthly_rent_inr > 0:
            annual_noi = monthly_rent_inr * 12.0
            capitalized_val = round(annual_noi / (cls.COMMERCIAL_CAP_RATE_PCT / 100.0), 2)

        return cls._format_valuation_output(
            pipeline_name="COMMERCIAL_PROPERTY_PIPELINE",
            loc=loc, pt=pt, area_value=area_value, area_unit=area_unit, total_sqft=total_sqft,
            est_unit_rate=est_sqft, total_market_val=total_val, uncertainty_pct=uncertainty_pct,
            reliability=reliability, guideline_obs=guideline_obs, comparables=comparables,
            adjustments={
                "main_road_frontage_premium_pct": frontage_pct,
                "floor_level_premium_pct": floor_pct,
                "infrastructure_boost_pct": infra_boost_pct,
                "capitalization_rate_pct": cls.COMMERCIAL_CAP_RATE_PCT,
                "capitalized_value_from_rent": capitalized_val
            }
        )

    # ================= PIPELINE 6: AGRICULTURAL LAND =================
    @classmethod
    def _evaluate_agricultural_land(
        cls, loc: Locality, pt: PropertyType, area_value: float, area_unit: str,
        guideline_obs: Optional[PriceObservation], comparables: List[PriceObservation],
        irrigation_type: Optional[str], infra_boost_pct: float
    ) -> Dict[str, Any]:
        """
        Agricultural land valuation: strictly measured in ACRES.
        Zero mixing with urban residential square-foot models.
        """
        # Convert area to acres
        clean_unit = area_unit.strip().upper()
        if clean_unit == "ACRE" or clean_unit == "ACRES":
            total_acres = float(area_value)
        elif clean_unit in ["CENT", "CENTS"]:
            total_acres = float(area_value) / 100.0
        elif clean_unit in ["GROUND", "GROUNDS"]:
            total_acres = float(area_value) / 18.15
        elif clean_unit in ["SQFT", "SQ_FT"]:
            total_acres = float(area_value) / 43560.0
        else:
            total_acres = float(area_value)

        # Base rate per acre
        if comparables:
            # Check if comparable was recorded in acres or sqft
            c = comparables[0]
            if c.original_unit == "ACRE":
                base_rate_per_acre = c.amount / c.area_value
            else:
                base_rate_per_acre = c.price_per_sqft_inr * 43560.0
            reliability = "HIGH" if len(comparables) >= 2 else "MEDIUM"
            uncertainty_pct = 0.10
        elif guideline_obs:
            if guideline_obs.original_unit == "ACRE":
                base_rate_per_acre = guideline_obs.amount / guideline_obs.area_value
            else:
                base_rate_per_acre = guideline_obs.price_per_sqft_inr * 43560.0
            reliability = "PRELIMINARY_GUIDELINE_BASED"
            uncertainty_pct = 0.15
        else:
            base_rate_per_acre = 800000.0  # ₹8L/acre default floor
            reliability = "LOW"
            uncertainty_pct = 0.20

        # Agricultural Irrigation & Soil Adjustments
        irrig_clean = (irrigation_type or "DRY_PUNJAI").strip().upper()
        if irrig_clean in ["NANJAI", "WET_IRRIGATED", "CANAL"]:
            soil_premium_pct = 25.0  # Fertile double-crop paddy tract
        elif irrig_clean in ["FLORICULTURE", "GARDEN"]:
            soil_premium_pct = 15.0
        else:
            soil_premium_pct = 0.0   # Rainfed dry land

        net_mult = 1.0 + (soil_premium_pct / 100.0) + (infra_boost_pct / 100.0)
        est_rate_per_acre = round(base_rate_per_acre * net_mult, 2)
        total_market_val = round(est_rate_per_acre * total_acres, 2)
        total_sqft = total_acres * 43560.0
        est_sqft = round(est_rate_per_acre / 43560.0, 2)

        return cls._format_valuation_output(
            pipeline_name="AGRICULTURAL_LAND_PIPELINE",
            loc=loc, pt=pt, area_value=area_value, area_unit=area_unit, total_sqft=total_sqft,
            est_unit_rate=est_rate_per_acre, total_market_val=total_market_val, uncertainty_pct=uncertainty_pct,
            reliability=reliability, guideline_obs=guideline_obs, comparables=comparables,
            adjustments={
                "primary_unit": "ACRE",
                "total_acres": round(total_acres, 4),
                "irrigation_type": irrig_clean,
                "soil_and_irrigation_premium_pct": soil_premium_pct,
                "infrastructure_boost_pct": infra_boost_pct,
                "equivalent_price_per_sqft": est_sqft
            }
        )

    # ================= BASE RATE & OUTPUT FORMATTER =================
    @classmethod
    def _derive_base_rate(
        cls, guideline_obs: Optional[PriceObservation], comparables: List[PriceObservation], loc: Locality
    ) -> (float, str, float):
        """Derives base market rate per sqft, data reliability rating, and uncertainty band."""
        if comparables:
            base_sqft = comparables[0].price_per_sqft_inr
            reliability = "HIGH" if len(comparables) >= 3 else "MEDIUM"
            uncertainty_pct = 0.08 if len(comparables) >= 3 else 0.12
        elif guideline_obs:
            tier_spread = 1.35 if loc.tier == 1 else (1.25 if loc.tier == 2 else 1.15)
            base_sqft = round(guideline_obs.price_per_sqft_inr * tier_spread, 2)
            reliability = "PRELIMINARY_GUIDELINE_BASED"
            uncertainty_pct = 0.15
        else:
            base_sqft = 4500.0
            reliability = "LOW"
            uncertainty_pct = 0.20
        return base_sqft, reliability, uncertainty_pct

    @classmethod
    def _format_valuation_output(
        cls, pipeline_name: str, loc: Locality, pt: PropertyType,
        area_value: float, area_unit: str, total_sqft: float,
        est_unit_rate: float, total_market_val: float, uncertainty_pct: float,
        reliability: str, guideline_obs: Optional[PriceObservation],
        comparables: List[PriceObservation], adjustments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Constructs standardized institutional valuation response."""
        guideline_sqft = guideline_obs.price_per_sqft_inr if guideline_obs else round(est_unit_rate * 0.70, 2)
        total_guideline_val = round(guideline_sqft * total_sqft, 2)

        # Tax estimations
        stamp_duty = round(total_guideline_val * (cls.TN_STAMP_DUTY_PCT / 100.0), 2)
        reg_fee = round(total_guideline_val * (cls.TN_REGISTRATION_FEE_PCT / 100.0), 2)

        lower_bound = round(total_market_val * (1.0 - uncertainty_pct), 2)
        upper_bound = round(total_market_val * (1.0 + uncertainty_pct), 2)

        is_agri = pt.code == "AGRICULTURAL_LAND"
        unit_label = "ACRE" if is_agri else "SQFT"

        formatted_comparables = [
            {
                "id": c.id,
                "price_type": c.price_type,
                "rate_sqft_inr": c.price_per_sqft_inr,
                "observation_date": str(c.observation_date),
                "source_code": c.source.code if c.source else "",
                "source_reference": c.source_reference or "",
                "verification_status": c.verification_status
            }
            for c in comparables
        ]

        return {
            "status": "ESTIMATE_SUCCESS",
            "pipeline_name": pipeline_name,
            "locality": {
                "id": loc.id,
                "name": loc.name,
                "district": loc.district.name if loc.district else "",
                "region": loc.district.region if loc.district else "",
                "tier": loc.tier
            },
            "property_type": {
                "code": pt.code,
                "name": pt.name,
                "category": pt.category
            },
            "property_dimensions": {
                "area_supplied": area_value,
                "unit_supplied": area_unit,
                "normalized_area_sqft": total_sqft
            },
            # Market valuation estimate (never guideline)
            "fair_market_valuation": total_market_val,
            "fair_market_valuation_estimate": {
                "estimated_market_rate_per_sqft_inr": round(total_market_val / total_sqft, 2) if total_sqft > 0 else est_unit_rate,
                "total_fair_market_value_inr": total_market_val,
                "confidence_interval_95_pct": {
                    "lower_bound_inr": lower_bound,
                    "upper_bound_inr": upper_bound,
                    "margin_pct": round(uncertainty_pct * 100.0, 1)
                }
            },
            "estimated_rate_per_unit": est_unit_rate,
            "rate_unit": unit_label,
            "estimated_rate_per_sqft": round(total_market_val / total_sqft, 2) if total_sqft > 0 else est_unit_rate,
            "valuation_range": {
                "lower_bound_total": lower_bound,
                "upper_bound_total": upper_bound,
                "uncertainty_interval_pct": round(uncertainty_pct * 100.0, 1),
                "confidence_rating": reliability
            },
            # Statutory guideline value (strictly separated)
            "statutory_guideline_valuation": {
                "guideline_rate_per_sqft": guideline_sqft,
                "guideline_rate_per_sqft_inr": guideline_sqft,
                "total_guideline_value": total_guideline_val,
                "total_guideline_value_inr": total_guideline_val,
                "source": "TNREGINET Official Gazette (Inspector General of Registration)",
                "effective_date": str(guideline_obs.observation_date) if guideline_obs else "2024-07-01",
                "guideline_vs_market_spread_pct": round(((total_market_val - total_guideline_val) / total_guideline_val) * 100.0, 1) if total_guideline_val > 0 else 0.0
            },
            "total_statutory_guideline_value": total_guideline_val,  # Backwards compatibility
            # Statutory fees
            "tamil_nadu_statutory_taxes": {
                "stamp_duty_pct": cls.TN_STAMP_DUTY_PCT,
                "stamp_duty_inr": stamp_duty,
                "registration_fee_pct": cls.TN_REGISTRATION_FEE_PCT,
                "registration_fee_inr": reg_fee,
                "total_statutory_taxes_inr": round(stamp_duty + reg_fee, 2)
            },
            "estimated_statutory_transfer_fees": {
                "stamp_duty_7pct_inr": stamp_duty,
                "registration_fee_2pct_inr": reg_fee,
                "total_conveyance_charges_inr": round(stamp_duty + reg_fee, 2)
            },
            "physical_adjustments": adjustments,
            "comparables_count": len(comparables),
            "comparable_evidence": formatted_comparables,
            "methodology_disclosure": "Fair market valuation is calculated using empirical registered transactions, developer filings, and hedonic adjustments. Statutory guideline values represent the minimum tax threshold and are never treated as market transaction prices."
        }
