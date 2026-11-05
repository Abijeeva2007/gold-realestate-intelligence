"""
Data Merger and Pipeline Integrator Module.
Aligns global gold prices in USD/troy oz, USD/INR foreign exchange rates,
and domestic Indian gold prices in INR/10g into a unified research-grade master dataset.

Strictly preserves authentic observations and tags derived metrics explicitly.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from src.config import TROY_OUNCE_TO_GRAMS, PROCESSED_DATA_DIR, setup_logging
from src.processors.regime_detector import RegimeDetector

logger = setup_logging()

class DataMerger:
    """Merges and aligns cross-market datasets while preserving provenance."""

    def __init__(self, processed_dir: Path = None):
        self.processed_dir = Path(processed_dir or PROCESSED_DATA_DIR)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.regime_detector = RegimeDetector()

    def build_master_daily_dataset(
        self,
        df_gold_daily: pd.DataFrame,
        df_fx_daily: pd.DataFrame,
        df_rbi_monthly: pd.DataFrame = None,
        save_to_disk: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Merges daily global gold prices and USD/INR exchange rates into a unified master dataset.
        Computes domestic gold parity price (INR per 10 grams) without interpolating missing values.
        
        Args:
            df_gold_daily: Cleaned COMEX gold futures daily DataFrame.
            df_fx_daily: Cleaned USD/INR FX daily DataFrame.
            df_rbi_monthly: Cleaned RBI monthly gold DataFrame (optional).
            
        Returns:
            Unified daily DataFrame and alignment summary metrics.
        """
        logger.info("Merging daily global gold prices and USD/INR exchange rates...")

        # Ensure date columns are formatted strings YYYY-MM-DD
        gold = df_gold_daily.copy()
        fx = df_fx_daily.copy()
        
        gold["date"] = pd.to_datetime(gold["date"]).dt.strftime("%Y-%m-%d")
        fx["date"] = pd.to_datetime(fx["date"]).dt.strftime("%Y-%m-%d")

        # Outer join to audit missing observations across both markets
        merged = pd.merge(
            gold[["date", "close_usd_per_troy_oz", "open_usd_per_troy_oz", 
                  "high_usd_per_troy_oz", "low_usd_per_troy_oz", "volume"]],
            fx[["date", "fx_usdinr"]],
            on="date",
            how="outer"
        ).sort_values("date").reset_index(drop=True)

        # Flag missing observations explicitly (NO silent forward-fill / interpolation)
        merged["gold_market_open"] = merged["close_usd_per_troy_oz"].notna()
        merged["fx_market_open"] = merged["fx_usdinr"].notna()
        merged["both_markets_open"] = merged["gold_market_open"] & merged["fx_market_open"]

        # Calculate theoretical Indian import parity price (INR per 10g)
        # 1 troy oz = 31.1034768 grams -> price per 10 grams = (USD/troy_oz / 31.1034768) * 10 * FX
        conversion_factor = 10.0 / TROY_OUNCE_TO_GRAMS
        
        # Only compute where both real observations exist
        valid_both = merged["both_markets_open"]
        merged["gold_parity_inr_per_10g"] = np.nan
        merged.loc[valid_both, "gold_parity_inr_per_10g"] = (
            (merged.loc[valid_both, "close_usd_per_troy_oz"] * conversion_factor) * 
            merged.loc[valid_both, "fx_usdinr"]
        ).round(2)

        # Incorporate RBI Monthly Mumbai Benchmark if provided
        if df_rbi_monthly is not None and not df_rbi_monthly.empty:
            rbi = df_rbi_monthly.copy()
            merged["year_month"] = merged["date"].str[:7]
            merged = pd.merge(
                merged,
                rbi[["year_month", "gold_mumbai_inr_per_10g", "spread_inr_per_10g"]].rename(
                    columns={
                        "gold_mumbai_inr_per_10g": "rbi_mumbai_monthly_avg_inr_per_10g",
                        "spread_inr_per_10g": "rbi_monthly_spread_inr_per_10g"
                    }
                ),
                on="year_month",
                how="left"
            ).drop(columns=["year_month"])

        # Tag macroeconomic market regimes
        merged = self.regime_detector.assign_regimes(merged, date_col="date")

        # Set strict data provenance flags
        merged["is_interpolated"] = False

        # Summary statistics
        metrics = {
            "total_calendar_records": len(merged),
            "gold_trading_days": int(merged["gold_market_open"].sum()),
            "fx_trading_days": int(merged["fx_market_open"].sum()),
            "joint_trading_days": int(merged["both_markets_open"].sum()),
            "gold_missing_days": int((~merged["gold_market_open"]).sum()),
            "fx_missing_days": int((~merged["fx_market_open"]).sum()),
            "earliest_date": merged["date"].min(),
            "latest_date": merged["date"].max()
        }

        # Save processed master file if requested
        if save_to_disk:
            master_path = self.processed_dir / "gold_master_daily_unified.csv"
            merged.to_csv(master_path, index=False)
            logger.info(f"Master daily dataset written to {master_path} ({len(merged)} rows).")

        return merged, metrics
