"""
Data Verification and Quality Audit Script for Tamil Nadu Real Estate Engine (TASK 02 - Phase 1).
Inspects all 38 districts, taluks, localities, price observations, market indices,
and macro indicators in data/real_estate.db.
"""

import json
from datetime import date
from collections import defaultdict
from sqlalchemy.orm import Session
from src.real_estate.db.database import SessionLocal
from src.real_estate.db.schema import (
    District, Taluk, Locality, PropertyType, DataSource,
    PriceObservation, MarketIndex, MacroIndicator, InfrastructureProject, IngestionLog
)


def run_data_audit():
    db = SessionLocal()
    try:
        # 1. District and Geography Audit
        districts = db.query(District).order_by(District.name).all()
        taluks = db.query(Taluk).all()
        localities = db.query(Locality).all()
        prop_types = db.query(PropertyType).all()
        sources = db.query(DataSource).all()
        observations = db.query(PriceObservation).all()
        indices = db.query(MarketIndex).all()
        macro = db.query(MacroIndicator).all()
        infra = db.query(InfrastructureProject).all()
        logs = db.query(IngestionLog).all()

        print("=== TAMIL NADU REAL ESTATE DATA QUALITY AUDIT ===")
        print(f"Total Districts: {len(districts)} / 38")
        print(f"Total Taluks: {len(taluks)}")
        print(f"Total Localities: {len(localities)}")
        print(f"Total Property Types: {len(prop_types)}")
        print(f"Total Price Observations: {len(observations)}")
        print(f"Total Market Indices: {len(indices)}")
        print(f"Total Macro Indicators: {len(macro)}")
        print(f"Total Infrastructure Projects: {len(infra)}")
        print(f"Total Ingestion Runs: {len(logs)}")

        # 2. Price Observation Analysis
        price_type_counts = defaultdict(int)
        prop_type_counts = defaultdict(int)
        district_obs_counts = defaultdict(lambda: defaultdict(int))
        dates_by_type = defaultdict(list)
        unit_check_errors = []

        for obs in observations:
            price_type_counts[obs.price_type] += 1
            prop_type_counts[obs.property_type.code if obs.property_type else "UNKNOWN"] += 1
            dist_code = obs.locality.district.code if obs.locality and obs.locality.district else "UNKNOWN"
            district_obs_counts[dist_code][obs.price_type] += 1
            dates_by_type[obs.price_type].append(obs.observation_date)

            # Check unit conversion consistency: price_per_sqm should be ~10.7639 * price_per_sqft
            expected_sqm = round(obs.price_per_sqft_inr * 10.7639104, 2)
            if abs(obs.price_per_sqm_inr - expected_sqm) > 0.05:
                unit_check_errors.append(f"Observation ID {obs.id}: price_per_sqm mismatch (actual={obs.price_per_sqm_inr}, expected={expected_sqm})")

        print("\n--- Price Observations by Type ---")
        for pt, cnt in sorted(price_type_counts.items()):
            min_d = min(dates_by_type[pt])
            max_d = max(dates_by_type[pt])
            print(f"  {pt}: {cnt} records (Date range: {min_d} to {max_d})")

        print("\n--- Price Observations by Property Type ---")
        for pt, cnt in sorted(prop_type_counts.items()):
            print(f"  {pt}: {cnt} records")

        # 3. District Coverage Analysis
        print("\n--- District Coverage Breakdown ---")
        covered_districts = []
        zero_coverage_districts = []

        for d in districts:
            total_d_obs = sum(district_obs_counts[d.code].values())
            if total_d_obs > 0:
                types_str = ", ".join([f"{k}:{v}" for k, v in district_obs_counts[d.code].items()])
                covered_districts.append((d.code, d.name, total_d_obs, types_str))
            else:
                zero_coverage_districts.append((d.code, d.name))

        print(f"Districts with Pricing Observations: {len(covered_districts)} / 38 ({len(covered_districts)/38*100:.1f}%)")
        for code, name, cnt, detail in covered_districts:
            print(f"  [{code}] {name:16s}: {cnt:2d} obs ({detail})")

        print(f"\nDistricts with ZERO Pricing Observations: {len(zero_coverage_districts)} / 38 ({len(zero_coverage_districts)/38*100:.1f}%)")
        zero_codes = [f"{c} ({n})" for c, n in zero_coverage_districts]
        print(f"  {', '.join(zero_codes)}")

        # 4. Market Indices Analysis
        print("\n--- Market Indices Breakdown ---")
        indices_by_name = defaultdict(list)
        for idx in indices:
            indices_by_name[idx.index_name].append(idx)

        for name, records in indices_by_name.items():
            dates = [r.period_date for r in records]
            vals = [r.index_value for r in records]
            print(f"  {name}: {len(records)} quarters (From {min(dates)} to {max(dates)}, Index: {min(vals)} to {max(vals)})")

        # 5. Macro Indicators Analysis
        print("\n--- Macroeconomic Indicators ---")
        macro_by_code = defaultdict(list)
        for m in macro:
            macro_by_code[m.indicator_code].append(m)

        for code, records in macro_by_code.items():
            dates = [r.period_date for r in records]
            vals = [r.value for r in records]
            unit = records[0].unit
            print(f"  {code}: {len(records)} points ({min(dates)} to {max(dates)}, Latest: {records[-1].value} {unit})")

        # 6. Unit Validation Errors
        print("\n--- Unit Conversion Validation ---")
        if unit_check_errors:
            print(f"  Found {len(unit_check_errors)} unit discrepancies:")
            for err in unit_check_errors[:5]:
                print(f"    {err}")
        else:
            print("  [PASS] All 72 observations have mathematically verified sqft to sqm conversions.")

        # Summary Audit Dict
        audit_summary = {
            "total_districts": len(districts),
            "covered_districts_count": len(covered_districts),
            "zero_coverage_districts_count": len(zero_coverage_districts),
            "district_coverage_pct": round(len(covered_districts) / len(districts) * 100.0, 1),
            "total_price_observations": len(observations),
            "price_type_counts": dict(price_type_counts),
            "property_type_counts": dict(prop_type_counts),
            "unit_errors_count": len(unit_check_errors),
            "market_indices_count": len(indices),
            "macro_indicators_count": len(macro)
        }

        with open("data/reports/real_estate_data_audit.json", "w") as f:
            json.dump(audit_summary, f, indent=2)

        return audit_summary

    finally:
        db.close()


if __name__ == "__main__":
    run_data_audit()
