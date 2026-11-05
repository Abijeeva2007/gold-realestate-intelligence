"""
Geographic Analytics & Regional Comparison Service (Task 02.2 Phase 6).
Provides:
- Statewide district comparisons (benchmark price, guideline-market spread, rental yield, confidence)
- Taluk-level granularity within districts
- Residential versus Commercial property spread analysis
- Agricultural land valuation and delta analysis across rural corridors
- Data availability and confidence map indicators
Prioritizes: Chennai, Coimbatore, Madurai, Tiruchirappalli, Salem, Hosur, and Kanniyakumari/Nagercoil.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.real_estate.db.schema import (
    District, Taluk, Locality, PropertyType, PriceObservation, MarketIndex
)
from src.real_estate.services.intelligence import RealEstateMarketIntelligenceEngine


class RealEstateGeographicAnalyticsService:
    """Enterprise spatial and regional analytics service."""

    PRIORITY_DISTRICT_CODES = ["CHN", "CBE", "MDU", "TRY", "SLM", "KRI", "KKM"]

    @classmethod
    def get_market_comparisons(cls, db: Session) -> Dict[str, Any]:
        """
        Comprehensive market comparison across districts,
        residential vs commercial spreads, and agricultural corridors.
        """
        district_rankings = RealEstateMarketIntelligenceEngine.get_district_rankings(db)
        res_vs_comm = cls.get_residential_vs_commercial_spread(db)
        agri_analysis = cls.get_agricultural_land_analysis(db)
        confidence_map = cls.get_data_confidence_map(db)

        return {
            "status": "success",
            "priority_markets_highlighted": cls.PRIORITY_DISTRICT_CODES,
            "district_benchmarks_ranking": district_rankings,
            "residential_vs_commercial_spread": res_vs_comm,
            "agricultural_land_analysis": agri_analysis,
            "data_confidence_and_availability_map": confidence_map
        }

    @classmethod
    def get_residential_vs_commercial_spread(cls, db: Session) -> List[Dict[str, Any]]:
        """
        Compares residential apartment rates against commercial property rates and rental yields
        across key urban hubs.
        """
        priority_districts = (
            db.query(District)
            .filter(District.code.in_(cls.PRIORITY_DISTRICT_CODES))
            .all()
        )

        pt_apt = db.query(PropertyType).filter(PropertyType.code == "RESIDENTIAL_APARTMENT").first()
        pt_comm = db.query(PropertyType).filter(PropertyType.code == "COMMERCIAL_PROPERTY").first()

        spreads = []
        for dist in priority_districts:
            # Average residential apartment rate in this district
            obs_apt = (
                db.query(PriceObservation.price_per_sqft_inr)
                .join(Locality, PriceObservation.locality_id == Locality.id)
                .filter(
                    Locality.district_id == dist.id,
                    PriceObservation.property_type_id == pt_apt.id if pt_apt else None,
                    PriceObservation.price_type.in_(["BANK_ASSESSMENT", "ASKING", "TRANSACTION", "GUIDELINE"])
                )
                .all()
            )
            avg_res = round(sum(r[0] for r in obs_apt) / len(obs_apt), 2) if obs_apt else None

            # Average commercial property rate in this district
            obs_comm = (
                db.query(PriceObservation.price_per_sqft_inr)
                .join(Locality, PriceObservation.locality_id == Locality.id)
                .filter(
                    Locality.district_id == dist.id,
                    PriceObservation.property_type_id == pt_comm.id if pt_comm else None,
                    PriceObservation.price_type.in_(["BANK_ASSESSMENT", "ASKING", "TRANSACTION", "GUIDELINE"])
                )
                .all()
            )
            avg_comm = round(sum(r[0] for r in obs_comm) / len(obs_comm), 2) if obs_comm else None

            spread_pct = None
            if avg_res and avg_comm and avg_res > 0:
                spread_pct = round(((avg_comm - avg_res) / avg_res) * 100.0, 1)

            # Commercial rent yield
            comm_rent = (
                db.query(PriceObservation.price_per_sqft_inr)
                .join(Locality, PriceObservation.locality_id == Locality.id)
                .filter(
                    Locality.district_id == dist.id,
                    PriceObservation.property_type_id == pt_comm.id if pt_comm else None,
                    PriceObservation.price_type == "RENTAL"
                )
                .first()
            )
            comm_rent_rate = comm_rent[0] if comm_rent else None
            comm_yield_pct = round(((comm_rent_rate * 12.0) / avg_comm) * 100.0, 2) if comm_rent_rate and avg_comm else None

            spreads.append({
                "district_code": dist.code,
                "district_name": dist.name,
                "region": dist.region,
                "residential_avg_sqft": avg_res,
                "commercial_avg_sqft": avg_comm,
                "commercial_premium_pct": spread_pct,
                "commercial_monthly_rent_sqft": comm_rent_rate,
                "commercial_gross_yield_pct": comm_yield_pct
            })

        # Sort by commercial average descending
        spreads.sort(key=lambda x: x["commercial_avg_sqft"] or 0, reverse=True)
        return spreads

    @classmethod
    def get_agricultural_land_analysis(cls, db: Session) -> Dict[str, Any]:
        """
        Analyzes agricultural land rates (INR / Acre) across Delta, Coastal, and Industrial corridors.
        Strictly segregated from urban residential property models.
        """
        pt_agri = db.query(PropertyType).filter(PropertyType.code == "AGRICULTURAL_LAND").first()
        if not pt_agri:
            return {"status": "NO_AGRICULTURAL_RECORDS", "records": []}

        agri_obs = (
            db.query(PriceObservation)
            .filter(PriceObservation.property_type_id == pt_agri.id)
            .order_by(PriceObservation.amount.desc())
            .all()
        )

        records = []
        for o in agri_obs:
            loc = o.locality
            dist = loc.district if loc else None
            rate_acre = o.amount if o.original_unit == "ACRE" else round(o.price_per_sqft_inr * 43560.0, 2)
            records.append({
                "id": o.id,
                "district_code": dist.code if dist else "",
                "district_name": dist.name if dist else "",
                "locality_name": loc.name if loc else "",
                "price_type": o.price_type,
                "rate_per_acre_inr": rate_acre,
                "equivalent_price_per_sqft": o.price_per_sqft_inr,
                "observation_date": str(o.observation_date),
                "source_reference": o.source_reference or "",
                "corridor_category": "DELTA_CAUVERY_BASIN" if "Delta" in (loc.name or "") or "Cauvery" in (loc.name or "") else (
                    "COASTAL_FLORICULTURE" if "Floriculture" in (loc.name or "") else "GREENFIELD_AIRPORT_ZONE"
                )
            })

        return {
            "total_agricultural_benchmarks": len(records),
            "state_average_rate_per_acre_inr": round(sum(r["rate_per_acre_inr"] for r in records) / len(records), 2) if records else None,
            "primary_measurement_unit": "ACRE (43,560 sq ft / 100 Cents / 18.15 Grounds)",
            "statutory_isolation_policy": "Strictly segregated from urban residential per-sqft models",
            "corridors": records
        }

    @classmethod
    def get_data_confidence_map(cls, db: Session) -> Dict[str, List[str]]:
        """Classifies all 38 districts by data richness and confidence tier."""
        districts = db.query(District).all()
        high_conf = []
        med_conf = []
        prelim_conf = []

        for d in districts:
            obs = (
                db.query(PriceObservation)
                .join(Locality, PriceObservation.locality_id == Locality.id)
                .filter(Locality.district_id == d.id)
                .all()
            )
            market_obs = [o for o in obs if o.price_type in ["TRANSACTION", "ASKING", "BANK_ASSESSMENT"]]

            if len(obs) >= 15 and len(market_obs) >= 5:
                high_conf.append(f"{d.name} ({d.code})")
            elif len(obs) >= 4 and len(market_obs) >= 1:
                med_conf.append(f"{d.name} ({d.code})")
            else:
                prelim_conf.append(f"{d.name} ({d.code})")

        return {
            "tier_1_high_confidence_markets": high_conf,
            "tier_2_moderate_confidence_markets": med_conf,
            "tier_3_statutory_guideline_only_markets": prelim_conf
        }
