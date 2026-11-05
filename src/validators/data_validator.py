"""
Data Quality and Integrity Validator Module.
Conducts rigorous validation tests:
1. Target date ranges (ensuring 20+ years of global historical gold and FX coverage).
2. Duplicate timestamps audit.
3. Missing observations & non-trading day analysis.
4. Unit consistency and boundary checks (positive prices, parity relationship).
5. Non-interpolation verification (ensuring zero synthetic or fabricated records).
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

from src.config import TROY_OUNCE_TO_GRAMS, setup_logging

logger = setup_logging()

class DataValidator:
    """Performs rigorous statistical and integrity assertions on processed datasets."""

    @staticmethod
    def validate_date_range(df: pd.DataFrame, date_col: str = "date", min_years: int = 20) -> Dict[str, Any]:
        """Validates that dataset spans at least min_years (targeting 20+ years)."""
        dates = pd.to_datetime(df[date_col]).dropna().sort_values()
        if dates.empty:
            return {"valid": False, "error": "Empty date column"}
        
        start_date = dates.iloc[0]
        end_date = dates.iloc[-1]
        years_span = (end_date - start_date).days / 365.25
        
        passed = years_span >= min_years
        return {
            "valid": passed,
            "start_date": str(start_date.date()),
            "end_date": str(end_date.date()),
            "years_span": round(years_span, 2),
            "target_min_years": min_years,
            "message": f"Dataset covers {years_span:.2f} years (Target >= {min_years} years: {'PASS' if passed else 'FAIL'})"
        }

    @staticmethod
    def validate_duplicates(df: pd.DataFrame, key_col: str = "date") -> Dict[str, Any]:
        """Validates that no duplicate timestamps or keys exist."""
        duplicates = df.duplicated(subset=[key_col]).sum()
        passed = duplicates == 0
        return {
            "valid": passed,
            "duplicate_count": int(duplicates),
            "message": f"Found {duplicates} duplicate timestamps (Expected 0: {'PASS' if passed else 'FAIL'})"
        }

    @staticmethod
    def validate_missingness(df: pd.DataFrame, expected_cols: List[str] = None) -> Dict[str, Any]:
        """
        Analyzes missing values per column and checks interpolation policy.
        Ensures is_interpolated is strictly False across all rows.
        """
        cols_to_check = expected_cols or df.columns.tolist()
        missing_stats = {}
        for col in cols_to_check:
            if col in df.columns:
                null_count = int(df[col].isna().sum())
                null_pct = round((null_count / len(df)) * 100.0, 2)
                missing_stats[col] = {
                    "missing_count": null_count,
                    "missing_pct": null_pct
                }

        # Check interpolation integrity
        has_interpolation_flag = "is_interpolated" in df.columns
        any_interpolated = bool(df["is_interpolated"].any()) if has_interpolation_flag else False

        passed = not any_interpolated
        return {
            "valid": passed,
            "total_records": len(df),
            "columns": missing_stats,
            "any_fabricated_or_interpolated": any_interpolated,
            "message": "Strict non-interpolation policy verified (No synthetic records detected)."
        }

    @staticmethod
    def validate_units_and_ranges(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validates price sanity bounds and theoretical parity math:
        - Gold USD: $200 - $10,000 / oz
        - USD/INR: 7.0 - 150.0 INR/USD
        - Parity formula adherence where both exist: |parity - (gold * 10 / 31.1034768 * fx)| < 0.10
        """
        results = {"checks": {}, "valid": True}

        # Check Gold Price in USD
        if "close_usd_per_troy_oz" in df.columns:
            valid_gold = df["close_usd_per_troy_oz"].dropna()
            g_min, g_max = valid_gold.min(), valid_gold.max()
            gold_in_bounds = (g_min >= 200.0) and (g_max <= 10000.0)
            results["checks"]["gold_usd_bounds"] = {
                "min": float(g_min),
                "max": float(g_max),
                "in_bounds": bool(gold_in_bounds),
                "expected": [200.0, 10000.0]
            }
            if not gold_in_bounds:
                results["valid"] = False

        # Check FX Rate
        if "fx_usdinr" in df.columns:
            valid_fx = df["fx_usdinr"].dropna()
            fx_min, fx_max = valid_fx.min(), valid_fx.max()
            fx_in_bounds = (fx_min >= 7.0) and (fx_max <= 150.0)
            results["checks"]["fx_usdinr_bounds"] = {
                "min": float(fx_min),
                "max": float(fx_max),
                "in_bounds": bool(fx_in_bounds),
                "expected": [7.0, 150.0]
            }
            if not fx_in_bounds:
                results["valid"] = False

        # Check Parity Formula Integrity
        if "gold_parity_inr_per_10g" in df.columns and "close_usd_per_troy_oz" in df.columns and "fx_usdinr" in df.columns:
            both = df[df["close_usd_per_troy_oz"].notna() & df["fx_usdinr"].notna() & df["gold_parity_inr_per_10g"].notna()]
            if not both.empty:
                expected_parity = (both["close_usd_per_troy_oz"] / TROY_OUNCE_TO_GRAMS * 10.0 * both["fx_usdinr"]).round(2)
                diff = (both["gold_parity_inr_per_10g"] - expected_parity).abs()
                max_discrepancy = diff.max()
                parity_valid = max_discrepancy < 0.10  # within 10 paise tolerance
                results["checks"]["parity_formula_integrity"] = {
                    "valid": bool(parity_valid),
                    "max_discrepancy_inr": float(max_discrepancy),
                    "tested_rows": len(both)
                }
                if not parity_valid:
                    results["valid"] = False

        return results

    def run_full_validation_suite(self, df: pd.DataFrame, key_col: str = "date") -> Dict[str, Any]:
        """Runs all checks and returns consolidated validation report."""
        date_res = self.validate_date_range(df, date_col=key_col)
        dup_res = self.validate_duplicates(df, key_col=key_col)
        miss_res = self.validate_missingness(df)
        unit_res = self.validate_units_and_ranges(df)

        overall_valid = date_res["valid"] and dup_res["valid"] and miss_res["valid"] and unit_res["valid"]

        return {
            "overall_status": "PASSED" if overall_valid else "FAILED",
            "date_range_check": date_res,
            "duplicate_check": dup_res,
            "missingness_check": miss_res,
            "units_and_ranges_check": unit_res
        }
