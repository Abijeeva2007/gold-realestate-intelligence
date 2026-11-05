"""
Module 1: Market Regime Intelligence Engine.
Computes multi-factor quantitative market regimes:
- Bullish
- Bearish
- Sideways
- High Volatility

Indicators:
- SMA 50 and SMA 200 (Golden/Death Cross, distance from price)
- 21-day and 63-day momentum returns
- 30-day and 90-day annualized rolling volatility
- 14-period Average Directional Index (ADX) with +DI and -DI
- Multi-day market return trajectories

Stores regime history with timestamps and supporting indicator values.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from src.config import PROCESSED_DATA_DIR, setup_logging
from src.db.database import get_engine

logger = setup_logging()


class GoldRegimeEngine:
    """Quantitative Market Regime Classification and Historical Regime Tracking."""

    def __init__(self, data_path: Optional[Path] = None):
        self.processed_dir = Path(PROCESSED_DATA_DIR)
        self.data_path = data_path or (self.processed_dir / "gold_master_daily_unified.csv")

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculates Welles Wilder's Average Directional Index (ADX), +DI, and -DI.
        Handles missing high/low with close proxies if needed.
        """
        df_work = df.copy()
        high = df_work["high_usd_per_troy_oz"] if "high_usd_per_troy_oz" in df_work else df_work["close_usd_per_troy_oz"]
        low = df_work["low_usd_per_troy_oz"] if "low_usd_per_troy_oz" in df_work else df_work["close_usd_per_troy_oz"]
        close = df_work["close_usd_per_troy_oz"]
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        up_move = high - high.shift(1)
        down_move = low.shift(1) - low

        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

        # Wilder's Smoothing (alpha = 1 / period)
        tr_smooth = pd.Series(tr).ewm(alpha=1.0/period, adjust=False).mean()
        plus_dm_smooth = pd.Series(plus_dm, index=df_work.index).ewm(alpha=1.0/period, adjust=False).mean()
        minus_dm_smooth = pd.Series(minus_dm, index=df_work.index).ewm(alpha=1.0/period, adjust=False).mean()

        plus_di = 100.0 * (plus_dm_smooth / (tr_smooth + 1e-9))
        minus_di = 100.0 * (minus_dm_smooth / (tr_smooth + 1e-9))

        dx = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-9)
        adx = dx.ewm(alpha=1.0/period, adjust=False).mean()

        df_work["adx_14d"] = adx
        df_work["plus_di_14d"] = plus_di
        df_work["minus_di_14d"] = minus_di
        return df_work

    def compute_regime_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes all technical, momentum, volatility, and trend strength indicators."""
        df_calc = df.copy()
        if "gold_market_open" in df_calc.columns:
            df_calc = df_calc[df_calc["gold_market_open"]].copy()

        df_calc = df_calc.sort_values("date").reset_index(drop=True)
        price = df_calc["close_usd_per_troy_oz"].astype(float)

        # 1. Moving Averages
        df_calc["sma_50d"] = price.rolling(50, min_periods=50).mean()
        df_calc["sma_200d"] = price.rolling(200, min_periods=200).mean()
        df_calc["sma_ratio"] = df_calc["sma_50d"] / df_calc["sma_200d"]
        df_calc["price_to_sma50"] = price / df_calc["sma_50d"]

        # 2. Momentum
        df_calc["return_1d"] = price.pct_change(1)
        df_calc["return_5d"] = price.pct_change(5)
        df_calc["return_21d"] = price.pct_change(21)
        df_calc["return_63d"] = price.pct_change(63)

        # 3. Realized Annualized Volatility
        log_ret = np.log(price / price.shift(1))
        df_calc["rolling_vol_30d"] = log_ret.rolling(30, min_periods=30).std() * np.sqrt(252) * 100.0
        df_calc["rolling_vol_90d"] = log_ret.rolling(90, min_periods=90).std() * np.sqrt(252) * 100.0

        # 4. ADX and Trend Strength
        df_calc = self.calculate_adx(df_calc, period=14)

        # 5. Rolling Drawdown from 63-day high
        rolling_max_63 = price.rolling(63, min_periods=21).max()
        df_calc["drawdown_63d_pct"] = ((price - rolling_max_63) / rolling_max_63) * 100.0

        return df_calc

    def classify_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Multi-factor regime classification logic.
        Assigns: 'Bullish', 'Bearish', 'Sideways', 'High Volatility'.
        """
        df_work = self.compute_regime_indicators(df)
        regimes = []
        regime_scores = []
        descriptions = []

        for idx, row in df_work.iterrows():
            # Warm-up period check
            if pd.isna(row["sma_200d"]) or pd.isna(row["rolling_vol_90d"]):
                regimes.append("Warm-up / Unclassified")
                regime_scores.append(0.0)
                descriptions.append("Insufficient data history for 200-day baseline.")
                continue

            price = row["close_usd_per_troy_oz"]
            sma_50 = row["sma_50d"]
            sma_200 = row["sma_200d"]
            sma_ratio = row["sma_ratio"]
            vol_30 = row["rolling_vol_30d"]
            vol_90 = row["rolling_vol_90d"]
            ret_21 = row["return_21d"]
            ret_63 = row["return_63d"]
            adx = row["adx_14d"]
            p_di = row["plus_di_14d"]
            m_di = row["minus_di_14d"]
            dd_63 = row["drawdown_63d_pct"]

            # Multi-factor voting
            # High Volatility Regime: annualized volatility > 24% or rapid drawdown > 10%
            is_high_vol = (vol_30 > 24.0 or vol_90 > 22.5 or dd_63 < -12.0)
            
            # Trend strength
            is_trending = (adx >= 20.0)

            # Bullish criteria
            bullish_factors = [
                sma_ratio > 1.015,
                price > sma_50,
                ret_21 > 0.0,
                ret_63 > 0.03,
                p_di > m_di
            ]
            bull_score = sum(bullish_factors) / len(bullish_factors)

            # Bearish criteria
            bearish_factors = [
                sma_ratio < 0.985,
                price < sma_50,
                ret_21 < 0.0,
                ret_63 < -0.03,
                m_di > p_di
            ]
            bear_score = sum(bearish_factors) / len(bearish_factors)

            if is_high_vol and (dd_63 < -10.0 or vol_30 > 26.0):
                regime = "High Volatility"
                score = round(float(vol_30), 2)
                desc = f"Elevated market volatility (30d Ann. Vol: {vol_30:.1f}%, 63d Drawdown: {dd_63:.1f}%)."
            elif bull_score >= 0.6:
                regime = "Bullish"
                score = round(bull_score * 100.0, 1)
                desc = f"Uptrend confirmed: Golden cross alignment (50/200 DMA ratio: {sma_ratio:.4f}), ADX={adx:.1f} (+DI>{m_di:.1f})."
            elif bear_score >= 0.6:
                regime = "Bearish"
                score = round(bear_score * 100.0, 1)
                desc = f"Downtrend confirmed: Death cross alignment (50/200 DMA ratio: {sma_ratio:.4f}), ADX={adx:.1f} (-DI>{p_di:.1f})."
            else:
                regime = "Sideways"
                score = round((1.0 - max(bull_score, bear_score)) * 100.0, 1)
                desc = f"Consolidating market: Compressed moving averages (ratio: {sma_ratio:.4f}), low trend conviction (ADX={adx:.1f})."

            regimes.append(regime)
            regime_scores.append(score)
            descriptions.append(desc)

        df_work["regime"] = regimes
        df_work["regime_conviction_score"] = regime_scores
        df_work["regime_description"] = descriptions
        return df_work

    def run_regime_intelligence(self) -> Dict[str, Any]:
        """Executes full regime classification, persists to disk and database."""
        df = pd.read_csv(self.data_path)
        logger.info(f"Loaded {len(df)} records from {self.data_path} for Regime Intelligence.")

        df_regimes = self.classify_regimes(df)

        # Output columns for persistence
        out_cols = [
            "date", "close_usd_per_troy_oz", "regime", "regime_conviction_score",
            "sma_50d", "sma_200d", "sma_ratio", "return_21d", "return_63d",
            "rolling_vol_30d", "rolling_vol_90d", "adx_14d", "plus_di_14d",
            "minus_di_14d", "drawdown_63d_pct", "regime_description"
        ]
        save_df = df_regimes[out_cols].copy()
        
        # Save CSV
        out_path = self.processed_dir / "gold_regime_history.csv"
        save_df.to_csv(out_path, index=False)
        logger.info(f"Saved {len(save_df)} regime records to {out_path}.")

        # Save to SQLite table 'gold_regime_history'
        try:
            eng = get_engine()
            save_df.to_sql("gold_regime_history", eng, if_exists="replace", index=False)
            logger.info("Persisted gold_regime_history table to SQLite database.")
        except Exception as exc:
            logger.warning(f"Database persistence warning: {exc}")

        # Current regime summary
        latest = save_df.iloc[-1]
        regime_counts = save_df["regime"].value_counts().to_dict()

        return {
            "latest_date": str(latest["date"])[:10],
            "current_price_usd": float(latest["close_usd_per_troy_oz"]),
            "current_regime": str(latest["regime"]),
            "conviction_score": float(latest["regime_conviction_score"]),
            "description": str(latest["regime_description"]),
            "sma_50d": round(float(latest["sma_50d"]), 2) if pd.notna(latest["sma_50d"]) else None,
            "sma_200d": round(float(latest["sma_200d"]), 2) if pd.notna(latest["sma_200d"]) else None,
            "sma_ratio": round(float(latest["sma_ratio"]), 4) if pd.notna(latest["sma_ratio"]) else None,
            "adx_14d": round(float(latest["adx_14d"]), 2) if pd.notna(latest["adx_14d"]) else None,
            "rolling_vol_30d_pct": round(float(latest["rolling_vol_30d"]), 2) if pd.notna(latest["rolling_vol_30d"]) else None,
            "return_21d_pct": round(float(latest["return_21d"]) * 100.0, 2) if pd.notna(latest["return_21d"]) else None,
            "regime_distribution": regime_counts
        }


if __name__ == "__main__":
    engine = GoldRegimeEngine()
    summary = engine.run_regime_intelligence()
    print("Market Regime Intelligence Summary:", summary)
