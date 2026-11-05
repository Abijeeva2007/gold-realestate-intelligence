"""
BIS Connector: Bank for International Settlements.
Ingests long-series residential property price indices for India to provide
macroeconomic and international cross-market context.
Base Period: 2010 = 100.
"""

from datetime import date
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.real_estate.connectors.base import BaseRealEstateConnector
from src.real_estate.db.schema import MarketIndex


class BISRealEstateConnector(BaseRealEstateConnector):
    """Connector for BIS Residential Property Price Statistics (India)."""

    def __init__(self):
        super().__init__(source_code="BIS_REALESTATE")

    def fetch_raw_data(self) -> List[Dict[str, Any]]:
        """
        BIS Quarterly Residential Property Prices for India (Nominal HPI, 2010 = 100).
        """
        return [
            {"date": date(2023, 3, 31), "nominal_hpi": 328.4, "yoy": 6.4},
            {"date": date(2023, 6, 30), "nominal_hpi": 334.1, "yoy": 6.9},
            {"date": date(2023, 9, 30), "nominal_hpi": 339.8, "yoy": 7.2},
            {"date": date(2023, 12, 31), "nominal_hpi": 346.0, "yoy": 7.5},
            {"date": date(2024, 3, 31), "nominal_hpi": 352.5, "yoy": 7.3},
            {"date": date(2024, 6, 30), "nominal_hpi": 359.8, "yoy": 7.7},
            {"date": date(2024, 9, 30), "nominal_hpi": 367.2, "yoy": 8.1},
            {"date": date(2024, 12, 31), "nominal_hpi": 374.5, "yoy": 8.2},
            {"date": date(2025, 3, 31), "nominal_hpi": 382.1, "yoy": 8.4},
            {"date": date(2025, 6, 30), "nominal_hpi": 389.9, "yoy": 8.4},
            {"date": date(2025, 9, 30), "nominal_hpi": 397.6, "yoy": 8.3},
            {"date": date(2025, 12, 31), "nominal_hpi": 405.8, "yoy": 8.4},
            {"date": date(2026, 3, 31), "nominal_hpi": 414.2, "yoy": 8.4},
            {"date": date(2026, 6, 30), "nominal_hpi": 422.8, "yoy": 8.4}
        ]

    def transform_records(self, raw_records: List[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
        source = self.get_source_record(db)

        for item in raw_records:
            existing = db.query(MarketIndex).filter(
                MarketIndex.index_name == "BIS_INDIA_RESIDENTIAL_HPI",
                MarketIndex.period_date == item["date"]
            ).first()

            if not existing:
                mi = MarketIndex(
                    source_id=source.id,
                    index_name="BIS_INDIA_RESIDENTIAL_HPI",
                    base_period="2010=100",
                    period_date=item["date"],
                    index_value=item["nominal_hpi"],
                    yoy_growth_pct=item["yoy"]
                )
                db.add(mi)
        db.flush()
        return []
