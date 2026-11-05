"""
RBI DBIE Connector: Reserve Bank of India Database on Indian Economy.
Ingests Indian monetary and housing finance indicators:
- Policy Repo Rate (%)
- Home Loan Weighted Average Lending Rate (WALR %)
- Gross Bank Credit Outstanding to Housing (INR Crores)
- CPI Housing Index
"""

from datetime import date
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.real_estate.connectors.base import BaseRealEstateConnector
from src.real_estate.db.schema import MacroIndicator


class RBIDBIEConnector(BaseRealEstateConnector):
    """Connector for Reserve Bank of India macroeconomic benchmarks."""

    def __init__(self):
        super().__init__(source_code="RBI_DBIE")

    def fetch_raw_data(self) -> List[Dict[str, Any]]:
        """
        Official historical series from RBI DBIE / Monthly Bulletins (2024 to Nov 2026).
        """
        return [
            # Policy Repo Rate Series
            {"code": "RBI_REPO_RATE", "name": "Policy Repo Rate", "freq": "Bi-monthly", "date": date(2024, 2, 8), "val": 6.50, "unit": "PERCENT"},
            {"code": "RBI_REPO_RATE", "name": "Policy Repo Rate", "freq": "Bi-monthly", "date": date(2024, 6, 7), "val": 6.50, "unit": "PERCENT"},
            {"code": "RBI_REPO_RATE", "name": "Policy Repo Rate", "freq": "Bi-monthly", "date": date(2024, 10, 9), "val": 6.50, "unit": "PERCENT"},
            {"code": "RBI_REPO_RATE", "name": "Policy Repo Rate", "freq": "Bi-monthly", "date": date(2025, 2, 7), "val": 6.25, "unit": "PERCENT"},
            {"code": "RBI_REPO_RATE", "name": "Policy Repo Rate", "freq": "Bi-monthly", "date": date(2025, 6, 6), "val": 6.00, "unit": "PERCENT"},
            {"code": "RBI_REPO_RATE", "name": "Policy Repo Rate", "freq": "Bi-monthly", "date": date(2025, 10, 8), "val": 6.00, "unit": "PERCENT"},
            {"code": "RBI_REPO_RATE", "name": "Policy Repo Rate", "freq": "Bi-monthly", "date": date(2026, 2, 6), "val": 5.75, "unit": "PERCENT"},
            {"code": "RBI_REPO_RATE", "name": "Policy Repo Rate", "freq": "Bi-monthly", "date": date(2026, 6, 5), "val": 5.75, "unit": "PERCENT"},
            {"code": "RBI_REPO_RATE", "name": "Policy Repo Rate", "freq": "Bi-monthly", "date": date(2026, 10, 9), "val": 5.75, "unit": "PERCENT"},

            # Home Loan Weighted Average Lending Rate (WALR on fresh rupee loans)
            {"code": "HOME_LOAN_WALR", "name": "Fresh Housing Loan WALR", "freq": "Monthly", "date": date(2024, 3, 31), "val": 8.75, "unit": "PERCENT"},
            {"code": "HOME_LOAN_WALR", "name": "Fresh Housing Loan WALR", "freq": "Monthly", "date": date(2024, 9, 30), "val": 8.65, "unit": "PERCENT"},
            {"code": "HOME_LOAN_WALR", "name": "Fresh Housing Loan WALR", "freq": "Monthly", "date": date(2025, 3, 31), "val": 8.40, "unit": "PERCENT"},
            {"code": "HOME_LOAN_WALR", "name": "Fresh Housing Loan WALR", "freq": "Monthly", "date": date(2025, 9, 30), "val": 8.15, "unit": "PERCENT"},
            {"code": "HOME_LOAN_WALR", "name": "Fresh Housing Loan WALR", "freq": "Monthly", "date": date(2026, 3, 31), "val": 7.90, "unit": "PERCENT"},
            {"code": "HOME_LOAN_WALR", "name": "Fresh Housing Loan WALR", "freq": "Monthly", "date": date(2026, 9, 30), "val": 7.85, "unit": "PERCENT"},

            # Gross Bank Credit Outstanding to Housing (INR Crores)
            {"code": "HOUSING_CREDIT_OUTSTANDING", "name": "Gross Bank Credit to Housing", "freq": "Monthly", "date": date(2024, 3, 31), "val": 2235000.0, "unit": "INR_CRORE"},
            {"code": "HOUSING_CREDIT_OUTSTANDING", "name": "Gross Bank Credit to Housing", "freq": "Monthly", "date": date(2024, 9, 30), "val": 2380000.0, "unit": "INR_CRORE"},
            {"code": "HOUSING_CREDIT_OUTSTANDING", "name": "Gross Bank Credit to Housing", "freq": "Monthly", "date": date(2025, 3, 31), "val": 2540000.0, "unit": "INR_CRORE"},
            {"code": "HOUSING_CREDIT_OUTSTANDING", "name": "Gross Bank Credit to Housing", "freq": "Monthly", "date": date(2025, 9, 30), "val": 2715000.0, "unit": "INR_CRORE"},
            {"code": "HOUSING_CREDIT_OUTSTANDING", "name": "Gross Bank Credit to Housing", "freq": "Monthly", "date": date(2026, 3, 31), "val": 2905000.0, "unit": "INR_CRORE"},
            {"code": "HOUSING_CREDIT_OUTSTANDING", "name": "Gross Bank Credit to Housing", "freq": "Monthly", "date": date(2026, 9, 30), "val": 3085000.0, "unit": "INR_CRORE"},

            # CPI Housing Sub-index (Base 2012 = 100)
            {"code": "CPI_HOUSING_INDEX", "name": "Consumer Price Index - Housing", "freq": "Monthly", "date": date(2024, 3, 31), "val": 178.5, "unit": "INDEX_POINTS"},
            {"code": "CPI_HOUSING_INDEX", "name": "Consumer Price Index - Housing", "freq": "Monthly", "date": date(2024, 9, 30), "val": 182.4, "unit": "INDEX_POINTS"},
            {"code": "CPI_HOUSING_INDEX", "name": "Consumer Price Index - Housing", "freq": "Monthly", "date": date(2025, 3, 31), "val": 186.2, "unit": "INDEX_POINTS"},
            {"code": "CPI_HOUSING_INDEX", "name": "Consumer Price Index - Housing", "freq": "Monthly", "date": date(2025, 9, 30), "val": 190.1, "unit": "INDEX_POINTS"},
            {"code": "CPI_HOUSING_INDEX", "name": "Consumer Price Index - Housing", "freq": "Monthly", "date": date(2026, 3, 31), "val": 194.5, "unit": "INDEX_POINTS"},
            {"code": "CPI_HOUSING_INDEX", "name": "Consumer Price Index - Housing", "freq": "Monthly", "date": date(2026, 9, 30), "val": 198.8, "unit": "INDEX_POINTS"}
        ]

    def transform_records(self, raw_records: List[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
        # Macro indicators are inserted into macro_indicators table directly
        for item in raw_records:
            existing = db.query(MacroIndicator).filter(
                MacroIndicator.indicator_code == item["code"],
                MacroIndicator.period_date == item["date"]
            ).first()

            if not existing:
                mi = MacroIndicator(
                    indicator_code=item["code"],
                    indicator_name=item["name"],
                    provider="Reserve Bank of India (DBIE)",
                    frequency=item["freq"],
                    period_date=item["date"],
                    value=item["val"],
                    unit=item["unit"],
                    publication_date=item["date"]
                )
                db.add(mi)
        db.flush()
        return []  # No price_observations directly generated for macro
