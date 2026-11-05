"""
Analytics and trend aggregation service for Tamil Nadu Real Estate Intelligence.
Provides statewide district metrics, locality profiles, index rollups, and macro correlation.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.real_estate.db.schema import (
    District, Taluk, Locality, PropertyType, PriceObservation,
    MarketIndex, MacroIndicator, InfrastructureProject, DataSource
)


class RealEstateAnalyticsService:
    """Aggregates real estate trends, district statistics, and macroeconomic status."""

    @classmethod
    def get_statewide_overview(cls, db: Session) -> Dict[str, Any]:
        """Provides statewide executive summary across all 38 districts."""
        total_districts = db.query(District).count()
        total_taluks = db.query(Taluk).count()
        total_localities = db.query(Locality).count()
        total_observations = db.query(PriceObservation).count()
        total_sources = db.query(DataSource).count()
        total_infra_projects = db.query(InfrastructureProject).count()

        # Observation breakdown by price type
        obs_by_type = dict(
            db.query(PriceObservation.price_type, func.count(PriceObservation.id))
            .group_by(PriceObservation.price_type).all()
        )

        # Latest NHB RESIDEX indices
        nhb_chennai = db.query(MarketIndex).filter(
            MarketIndex.index_name == "NHB_RESIDEX_CHN"
        ).order_by(MarketIndex.period_date.desc()).first()

        nhb_coimbatore = db.query(MarketIndex).filter(
            MarketIndex.index_name == "NHB_RESIDEX_CBE"
        ).order_by(MarketIndex.period_date.desc()).first()

        # Latest Macro Benchmarks
        repo_rate = db.query(MacroIndicator).filter(
            MacroIndicator.indicator_code == "RBI_REPO_RATE"
        ).order_by(MacroIndicator.period_date.desc()).first()

        home_loan_walr = db.query(MacroIndicator).filter(
            MacroIndicator.indicator_code == "HOME_LOAN_WALR"
        ).order_by(MacroIndicator.period_date.desc()).first()

        return {
            "status": "success",
            "state": "Tamil Nadu",
            "geographic_coverage": {
                "total_districts": total_districts,
                "total_taluks": total_taluks,
                "monitored_localities": total_localities,
                "monitored_infrastructure_projects": total_infra_projects
            },
            "evidence_ledger": {
                "total_price_observations": total_observations,
                "price_types_distribution": obs_by_type,
                "registered_data_sources": total_sources
            },
            "official_indices_summary": {
                "nhb_residex_chennai": {
                    "index_value": nhb_chennai.index_value if nhb_chennai else None,
                    "yoy_growth_pct": nhb_chennai.yoy_growth_pct if nhb_chennai else None,
                    "as_of": str(nhb_chennai.period_date) if nhb_chennai else None,
                    "base_year": "2017-18=100"
                },
                "nhb_residex_coimbatore": {
                    "index_value": nhb_coimbatore.index_value if nhb_coimbatore else None,
                    "yoy_growth_pct": nhb_coimbatore.yoy_growth_pct if nhb_coimbatore else None,
                    "as_of": str(nhb_coimbatore.period_date) if nhb_coimbatore else None,
                    "base_year": "2017-18=100"
                }
            },
            "macro_financial_climate": {
                "rbi_policy_repo_rate_pct": repo_rate.value if repo_rate else None,
                "home_loan_walr_pct": home_loan_walr.value if home_loan_walr else None,
                "monetary_stance": "Accommodative / Normalized Lending Environment"
            }
        }

    @classmethod
    def get_district_details(cls, db: Session, district_code: str) -> Optional[Dict[str, Any]]:
        """Deep dive for a specific district."""
        dist = db.query(District).filter(District.code == district_code.upper()).first()
        if not dist:
            return None

        taluks = [t.name for t in dist.taluks]
        localities = [
            {"id": l.id, "name": l.name, "postal_code": l.postal_code, "tier": l.tier}
            for l in dist.localities
        ]

        # Price observations within this district
        obs_summary = (
            db.query(
                PropertyType.name,
                PriceObservation.price_type,
                func.avg(PriceObservation.price_per_sqft_inr).label("avg_sqft"),
                func.min(PriceObservation.price_per_sqft_inr).label("min_sqft"),
                func.max(PriceObservation.price_per_sqft_inr).label("max_sqft"),
                func.count(PriceObservation.id).label("count")
            )
            .join(Locality, PriceObservation.locality_id == Locality.id)
            .join(PropertyType, PriceObservation.property_type_id == PropertyType.id)
            .filter(Locality.district_id == dist.id)
            .group_by(PropertyType.name, PriceObservation.price_type)
            .all()
        )

        infra = [
            {
                "name": p.project_name,
                "type": p.project_type,
                "status": p.status,
                "completion_year": p.expected_completion_year,
                "investment_crores": p.investment_inr_crores
            }
            for p in dist.infrastructure
        ]

        return {
            "code": dist.code,
            "name": dist.name,
            "headquarters": dist.headquarters,
            "region": dist.region,
            "area_sqkm": dist.area_sqkm,
            "population": dist.population_census,
            "coordinates": {"latitude": dist.latitude, "longitude": dist.longitude},
            "taluks": taluks,
            "monitored_localities": localities,
            "infrastructure_catalysts": infra,
            "pricing_evidence": [
                {
                    "property_type": row[0],
                    "price_type": row[1],
                    "avg_price_per_sqft_inr": round(float(row[2]), 2),
                    "min_price_per_sqft_inr": round(float(row[3]), 2),
                    "max_price_per_sqft_inr": round(float(row[4]), 2),
                    "data_points": row[5]
                }
                for row in obs_summary
            ]
        }

    @classmethod
    def get_locality_profile(cls, db: Session, locality_id: int) -> Optional[Dict[str, Any]]:
        """Granular locality profile."""
        loc = db.query(Locality).filter(Locality.id == locality_id).first()
        if not loc:
            return None

        # Fetch recent observations
        obs_list = (
            db.query(PriceObservation)
            .filter(PriceObservation.locality_id == locality_id)
            .order_by(PriceObservation.observation_date.desc())
            .all()
        )

        guideline_rates = [o for o in obs_list if o.price_type == "GUIDELINE"]
        asking_rates = [o for o in obs_list if o.price_type == "ASKING"]

        latest_guideline = guideline_rates[0].price_per_sqft_inr if guideline_rates else None
        latest_asking = asking_rates[0].price_per_sqft_inr if asking_rates else None

        infra = [
            {
                "name": p.project_name,
                "type": p.project_type,
                "status": p.status,
                "completion_year": p.expected_completion_year
            }
            for p in loc.infrastructure
        ]

        return {
            "id": loc.id,
            "name": loc.name,
            "district": loc.district.name if loc.district else "",
            "district_code": loc.district.code if loc.district else "",
            "taluk": loc.taluk.name if loc.taluk else "",
            "postal_code": loc.postal_code,
            "tier": loc.tier,
            "coordinates": {"latitude": loc.latitude, "longitude": loc.longitude},
            "summary_metrics": {
                "latest_guideline_rate_per_sqft_inr": latest_guideline,
                "latest_asking_rate_per_sqft_inr": latest_asking,
                "guideline_spread_pct": round(((latest_asking - latest_guideline) / latest_guideline) * 100.0, 1) if (latest_guideline and latest_asking) else None
            },
            "nearby_infrastructure": infra,
            "price_history": [
                {
                    "price_type": o.price_type,
                    "price_per_sqft_inr": o.price_per_sqft_inr,
                    "price_per_sqm_inr": o.price_per_sqm_inr,
                    "date": str(o.observation_date),
                    "source": o.source.code if o.source else ""
                }
                for o in obs_list[:15]
            ]
        }
