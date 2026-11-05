"""
Market Regime Detector Module.
Identifies macroeconomic and structural market regimes:
- 2008 Global Financial Crisis (GFC)
- 2020 COVID-19 Pandemic Shock
- 2024-2026 Structural Bull Regime & Historical All-Time Highs
- Intervening stabilization and consolidation eras.

Provides regime tagging and regime-wise risk & return analytics.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from src.config import MARKET_REGIMES, setup_logging

logger = setup_logging()

class RegimeDetector:
    """Classifies dates into macro market regimes and computes regime analytics."""

    def __init__(self, regimes: List[Dict[str, str]] = None):
        self.regimes = regimes or MARKET_REGIMES

    def assign_regimes(self, df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
        """
        Assigns regime labels and crisis indicators to each row based on the date column.
        
        Args:
            df: DataFrame containing date column (YYYY-MM-DD string or datetime).
            date_col: Name of the date column.
            
        Returns:
            DataFrame augmented with 'regime_name' and 'is_crisis_regime'.
        """
        df_out = df.copy()
        date_series = pd.to_datetime(df_out[date_col])

        # Default fallback
        df_out["regime_name"] = "Unclassified"
        df_out["is_crisis_regime"] = False

        crisis_regime_names = {
            "2008 Global Financial Crisis (GFC)",
            "2020 COVID-19 Pandemic Shock",
            "2024-2026 Structural Gold Bull Regime & Record Highs"
        }

        for regime in self.regimes:
            start = pd.to_datetime(regime["start_date"])
            end = pd.to_datetime(regime["end_date"])
            mask = (date_series >= start) & (date_series <= end)
            
            df_out.loc[mask, "regime_name"] = regime["name"]
            if regime["name"] in crisis_regime_names:
                df_out.loc[mask, "is_crisis_regime"] = True

        logger.info(f"Assigned market regimes across {len(df_out)} records.")
        return df_out

    def compute_regime_statistics(
        self,
        df: pd.DataFrame,
        price_col: str = "close_usd_per_troy_oz",
        date_col: str = "date"
    ) -> pd.DataFrame:
        """
        Computes statistical and financial metrics for each regime:
        - Observation count
        - Price mean, min, max
        - Annualized Volatility
        - Regime Return (%)
        - Max Drawdown (%)
        """
        df_work = df.copy()
        df_work = df_work.sort_values(date_col).reset_index(drop=True)
        
        # Calculate daily returns
        df_work["daily_return"] = df_work[price_col].pct_change()

        stats = []
        for regime in self.regimes:
            name = regime["name"]
            sub = df_work[df_work["regime_name"] == name]
            if sub.empty:
                continue

            prices = sub[price_col]
            daily_rets = sub["daily_return"].dropna()

            # Cumulative returns and drawdown
            cum_returns = (1 + daily_rets).cumprod()
            rolling_max = cum_returns.cummax()
            drawdowns = (cum_returns - rolling_max) / rolling_max
            max_drawdown = drawdowns.min() if not drawdowns.empty else 0.0

            # Annualized volatility (assuming ~252 trading days/year)
            ann_vol = daily_rets.std() * np.sqrt(252) if len(daily_rets) > 1 else np.nan

            # Total regime return
            start_price = prices.iloc[0]
            end_price = prices.iloc[-1]
            total_return_pct = ((end_price - start_price) / start_price) * 100.0

            stats.append({
                "regime_name": name,
                "start_date": regime["start_date"],
                "end_date": regime["end_date"],
                "observations": len(sub),
                "start_price_usd": round(start_price, 2),
                "end_price_usd": round(end_price, 2),
                "min_price_usd": round(prices.min(), 2),
                "max_price_usd": round(prices.max(), 2),
                "mean_price_usd": round(prices.mean(), 2),
                "regime_return_pct": round(total_return_pct, 2),
                "annualized_volatility_pct": round(ann_vol * 100, 2) if not np.isnan(ann_vol) else None,
                "max_drawdown_pct": round(max_drawdown * 100, 2)
            })

        return pd.DataFrame(stats)
