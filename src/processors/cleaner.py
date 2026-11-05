"""
Data Cleaner and Standardization Module.
Cleans raw market records, removes duplicate timestamps, standardizes dates into ISO-8601,
normalizes units (USD/troy oz, INR/10g, INR/USD), and strictly refuses to fabricate or interpolate prices.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from src.config import setup_logging

logger = setup_logging()

class DataCleaner:
    """Standardizes dates, formats units, and removes duplicates without interpolation."""

    @staticmethod
    def clean_comex_gold(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cleans COMEX Gold Futures raw dataset.
        Ensures dates are ISO-8601 YYYY-MM-DD, strips timezone offsets, drops duplicates,
        and enforces non-negative price bounds.
        """
        df = raw_df.copy()
        initial_count = len(df)
        
        # Standardize Date column
        if "Date" in df.columns:
            df["date"] = pd.to_datetime(df["Date"], utc=True).dt.strftime("%Y-%m-%d")
        else:
            raise KeyError("Expected 'Date' column in COMEX raw data.")

        # Rename core columns to standard research schema
        col_map = {
            "Open": "open_usd_per_troy_oz",
            "High": "high_usd_per_troy_oz",
            "Low": "low_usd_per_troy_oz",
            "Close": "close_usd_per_troy_oz",
            "Volume": "volume"
        }
        for orig, renamed in col_map.items():
            if orig in df.columns:
                df[renamed] = pd.to_numeric(df[orig], errors="coerce")

        keep_cols = ["date", "open_usd_per_troy_oz", "high_usd_per_troy_oz", 
                     "low_usd_per_troy_oz", "close_usd_per_troy_oz", "volume"]
        df = df[[c for c in keep_cols if c in df.columns]]

        # Remove duplicate dates (keeping latest observation)
        duplicates_removed = df.duplicated(subset=["date"]).sum()
        df = df.drop_duplicates(subset=["date"], keep="last")

        # Sort chronologically
        df = df.sort_values("date").reset_index(drop=True)

        # Drop invalid rows where close price is missing or non-positive (do NOT interpolate)
        valid_price_mask = df["close_usd_per_troy_oz"].notna() & (df["close_usd_per_troy_oz"] > 0)
        invalid_rows = (~valid_price_mask).sum()
        df = df[valid_price_mask].copy()

        # Audit metadata
        df["source"] = "COMEX_Gold_Futures"
        df["unit"] = "USD per troy ounce"
        df["is_interpolated"] = False  # Strictly no silent interpolation

        metrics = {
            "initial_rows": initial_count,
            "final_rows": len(df),
            "duplicates_removed": int(duplicates_removed),
            "invalid_price_rows_dropped": int(invalid_rows),
            "date_range": (df["date"].min(), df["date"].max()) if not df.empty else (None, None)
        }
        logger.info(f"Cleaned COMEX Gold data: {metrics}")
        return df, metrics

    @staticmethod
    def clean_usdinr_fx(raw_df: pd.DataFrame, source_type: str = "yahoo") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cleans USD/INR exchange rate dataset (from FRED or Yahoo Finance).
        """
        df = raw_df.copy()
        initial_count = len(df)

        if source_type == "fred":
            # FRED format: observation_date, DEXINUS
            df = df.rename(columns={"observation_date": "date", "DEXINUS": "fx_usdinr"})
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            # In FRED, dots '.' represent market holidays
            df["fx_usdinr"] = pd.to_numeric(df["fx_usdinr"].replace(".", np.nan), errors="coerce")
            source_label = "FRED_DEXINUS"
        else:
            # Yahoo format: Date, Close
            df["date"] = pd.to_datetime(df["Date"], utc=True).dt.strftime("%Y-%m-%d")
            df["fx_usdinr"] = pd.to_numeric(df["Close"], errors="coerce")
            source_label = "Yahoo_INR=X"

        df = df[["date", "fx_usdinr"]].copy()

        # Deduplicate
        duplicates_removed = df.duplicated(subset=["date"]).sum()
        df = df.drop_duplicates(subset=["date"], keep="last")

        # Sort chronologically
        df = df.sort_values("date").reset_index(drop=True)

        # Drop invalid or non-positive records (no silent interpolation)
        valid_mask = df["fx_usdinr"].notna() & (df["fx_usdinr"] > 0)
        invalid_rows = (~valid_mask).sum()
        df = df[valid_mask].copy()

        df["source"] = source_label
        df["unit"] = "INR per 1 USD"
        df["is_interpolated"] = False

        metrics = {
            "source": source_label,
            "initial_rows": initial_count,
            "final_rows": len(df),
            "duplicates_removed": int(duplicates_removed),
            "invalid_rate_rows_dropped": int(invalid_rows),
            "date_range": (df["date"].min(), df["date"].max()) if not df.empty else (None, None)
        }
        logger.info(f"Cleaned USD/INR FX data: {metrics}")
        return df, metrics

    @staticmethod
    def clean_rbi_annual(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cleans RBI Table 35 Annual Gold Series (1985-2026).
        Extracts start year of the financial year (e.g. 1985-86 -> 1985).
        """
        df = raw_df.copy()
        initial_count = len(df)

        df["fy_start_year"] = df["financial_year"].str.extract(r"^(\d{4})").astype(int)
        
        # Enforce positive values, stripping commas if string
        num_cols = ["gold_mumbai_inr_per_10g", "gold_london_usd_per_troy_oz", "spread_inr_per_10g"]
        for col in num_cols:
            if col in df.columns:
                if df[col].dtype == object or isinstance(df[col].iloc[0] if not df[col].empty else None, str):
                    df[col] = df[col].astype(str).str.replace(",", "")
                df[col] = pd.to_numeric(df[col], errors="coerce")

        duplicates_removed = df.duplicated(subset=["financial_year"]).sum()
        df = df.drop_duplicates(subset=["financial_year"]).sort_values("fy_start_year").reset_index(drop=True)

        df["source"] = "RBI_Table_35_Handbook"
        df["is_interpolated"] = False

        metrics = {
            "initial_rows": initial_count,
            "final_rows": len(df),
            "duplicates_removed": int(duplicates_removed),
            "fy_range": (df["financial_year"].min(), df["financial_year"].max()) if not df.empty else (None, None)
        }
        return df, metrics

    @staticmethod
    def clean_rbi_monthly(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cleans RBI Table 164 Monthly Gold Series.
        Maps Financial Year + Month into standard calendar Year-Month (e.g., 2024-04).
        """
        df = raw_df.copy()
        initial_count = len(df)

        month_map = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
            "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }

        # Calculate calendar year from Indian Financial Year (Apr-Mar)
        # e.g., FY 2023-24: Apr-Dec is 2023, Jan-Mar is 2024.
        def get_calendar_ym(row):
            fy = str(row["financial_year"])
            m_str = str(row["month"])
            m_num = month_map.get(m_str)
            if not m_num:
                return None
            m = re.match(r"^(\d{4})", fy)
            if not m:
                return None
            start_yr = int(m.group(1))
            cal_yr = start_yr if m_num >= 4 else (start_yr + 1)
            return f"{cal_yr}-{m_num:02d}"

        import re
        df["year_month"] = df.apply(get_calendar_ym, axis=1)
        df = df[df["year_month"].notna()].copy()

        num_cols = ["gold_mumbai_inr_per_10g", "gold_london_usd_per_troy_oz", "spread_inr_per_10g"]
        for col in num_cols:
            if col in df.columns:
                if df[col].dtype == object or isinstance(df[col].iloc[0] if not df[col].empty else None, str):
                    df[col] = df[col].astype(str).str.replace(",", "")
                df[col] = pd.to_numeric(df[col], errors="coerce")

        duplicates_removed = df.duplicated(subset=["year_month"]).sum()
        df = df.drop_duplicates(subset=["year_month"]).sort_values("year_month").reset_index(drop=True)

        df["source"] = "RBI_Table_164_Handbook"
        df["is_interpolated"] = False

        metrics = {
            "initial_rows": initial_count,
            "final_rows": len(df),
            "duplicates_removed": int(duplicates_removed),
            "period_range": (df["year_month"].min(), df["year_month"].max()) if not df.empty else (None, None)
        }
        return df, metrics

    @staticmethod
    def clean_world_bank_monthly(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cleans World Bank Pink Sheet Monthly Gold Series (1960-present).
        Standardizes '1960M01' into '1960-01'.
        """
        df = raw_df.copy()
        initial_count = len(df)

        df["year_month"] = df["period"].str.replace("M", "-")
        df["gold_usd_per_troy_oz"] = pd.to_numeric(df["gold_usd_per_troy_oz"], errors="coerce")

        valid_mask = df["gold_usd_per_troy_oz"].notna() & (df["gold_usd_per_troy_oz"] > 0)
        df = df[valid_mask].copy()

        duplicates_removed = df.duplicated(subset=["year_month"]).sum()
        df = df.drop_duplicates(subset=["year_month"]).sort_values("year_month").reset_index(drop=True)

        df["source"] = "World_Bank_CMO_PinkSheet"
        df["unit"] = "USD per troy ounce"
        df["is_interpolated"] = False

        metrics = {
            "initial_rows": initial_count,
            "final_rows": len(df),
            "duplicates_removed": int(duplicates_removed),
            "period_range": (df["year_month"].min(), df["year_month"].max()) if not df.empty else (None, None)
        }
        return df, metrics
