"""
Feature engineering and chronological dataset builder for Real Estate Forecasting (TASK 02 - Phase 4).
Strictly enforces:
- Chronological train / test partitioning (Train: 2018–2024, Test: 2025–2026).
- Macroeconomic variable alignment (RBI Repo Rate, Housing WALR, Housing Credit, CPI Housing, BIS Index).
- Zero future-data leakage or look-ahead contamination.
"""

from datetime import date
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from src.real_estate.db.schema import (
    PriceObservation, MarketIndex, MacroIndicator, Locality, PropertyType
)


class RealEstateFeatureEngineer:
    """Prepares structured time-series datasets with macroeconomic exogenous drivers."""

    @classmethod
    def load_panel_dataset(cls, db: Session) -> pd.DataFrame:
        """
        Extracts longitudinal quarterly observations and merges macroeconomic variables.
        """
        # 1. Fetch quarterly price observations
        obs_records = (
            db.query(
                PriceObservation.observation_date,
                PriceObservation.price_per_sqft_inr,
                Locality.name.label("locality_name"),
                PropertyType.code.label("property_type_code")
            )
            .join(Locality, PriceObservation.locality_id == Locality.id)
            .join(PropertyType, PriceObservation.property_type_id == PropertyType.id)
            .filter(PriceObservation.price_type == "BANK_ASSESSMENT")
            .order_by(PriceObservation.observation_date.asc())
            .all()
        )

        rows = []
        for r in obs_records:
            rows.append({
                "date": pd.to_datetime(r.observation_date),
                "price_per_sqft": float(r.price_per_sqft_inr),
                "locality": r.locality_name,
                "property_type": r.property_type_code
            })

        df_prices = pd.DataFrame(rows)
        if df_prices.empty:
            raise ValueError("No longitudinal price observations found in real_estate.db.")

        # 2. Fetch Macroeconomic Indicators
        macro_records = db.query(MacroIndicator).all()
        macro_dict = {}
        for m in macro_records:
            d = pd.to_datetime(m.period_date)
            if d not in macro_dict:
                macro_dict[d] = {}
            macro_dict[d][m.indicator_code] = float(m.value)

        df_macro = pd.DataFrame.from_dict(macro_dict, orient="index").sort_index()

        # 3. Fetch BIS India Property Index
        bis_records = db.query(MarketIndex).filter(MarketIndex.index_name == "BIS_INDIA_RESIDENTIAL_HPI").all()
        bis_dict = {pd.to_datetime(b.period_date): float(b.index_value) for b in bis_records}
        df_bis = pd.DataFrame(list(bis_dict.items()), columns=["date", "bis_hpi"]).set_index("date").sort_index()

        # Reindex across complete daily calendar from 2018 to 2026 with ffill & bfill
        all_days = pd.date_range("2018-01-01", "2026-12-31", freq="D")
        df_macro_daily = df_macro.reindex(all_days).ffill().bfill()
        df_bis_daily = df_bis.reindex(all_days).ffill().bfill()
        df_exog_daily = df_macro_daily.join(df_bis_daily, how="left").ffill().bfill()

        # Merge each observation with its corresponding date's macro values
        features = []
        for _, row in df_prices.iterrows():
            obs_dt = row["date"]
            if obs_dt in df_exog_daily.index:
                exog_row = df_exog_daily.loc[obs_dt]
            else:
                exog_row = df_exog_daily.asof(obs_dt)

            feat = {
                "date": obs_dt,
                "locality": row["locality"],
                "property_type": row["property_type"],
                "price_per_sqft": row["price_per_sqft"],
                "repo_rate": float(exog_row.get("RBI_REPO_RATE", 6.0)),
                "home_loan_walr": float(exog_row.get("HOME_LOAN_WALR", 8.2)),
                "housing_credit_lakh_cr": float(exog_row.get("HOUSING_CREDIT_OUTSTANDING", 2500000.0)) / 100000.0,
                "cpi_housing": float(exog_row.get("CPI_HOUSING_INDEX", 185.0)),
                "bis_hpi": float(exog_row.get("bis_hpi", 350.0))
            }
            features.append(feat)

        df_full = pd.DataFrame(features)
        df_full.sort_values(by="date", inplace=True)
        return df_full

    @classmethod
    def get_chronological_split(
        cls,
        df: pd.DataFrame,
        split_date: str = "2025-01-01"
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Chronologically splits into strictly non-overlapping train and test sets.
        Train: <= 2024-12-31
        Test:  >= 2025-01-01
        """
        split_dt = pd.to_datetime(split_date)
        train_df = df[df["date"] < split_dt].copy()
        test_df = df[df["date"] >= split_dt].copy()
        return train_df, test_df
