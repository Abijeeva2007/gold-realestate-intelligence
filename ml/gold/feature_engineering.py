"""
Feature Engineering Module for Gold Price Forecasting.
Constructs leak-free, stationary time-series features strictly using historical information
available at or prior to the prediction timestamp t.

Feature Design:
- Stationary Price Ratios: price / SMA7, price / SMA30, price / SMA90, price / SMA50, price / SMA200
- Trend Momentum: SMA50 / SMA200 (Golden Cross / Death Cross indicator)
- Returns: 1-day, 5-day, 21-day, 30-day percentage returns and 1-day log return
- Rolling Volatility: 7-day, 30-day, 90-day annualized volatility
- USD/INR Dynamics: 1-day & 21-day FX returns, FX to 30-day SMA ratio
- Calendar & Cyclical Seasonality: Sine/Cosine encodings for day-of-year and month
- Excludes raw collinear price levels (e.g. close, open, high, low, gold_parity_inr) to avoid
  collinearity and tree extrapolation failure.
"""

from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd

from src.config import setup_logging

logger = setup_logging()

class GoldFeatureEngineer:
    """Constructs leak-free, stationary financial and seasonal features for gold forecasting."""

    def __init__(self, price_col: str = "close_usd_per_troy_oz", fx_col: str = "fx_usdinr"):
        self.price_col = price_col
        self.fx_col = fx_col
        self.feature_names: List[str] = []

    def build_features(self, df: pd.DataFrame, drop_na: bool = True) -> pd.DataFrame:
        """
        Builds stationary, leak-free feature columns from daily price and FX series.
        Ensures strictly backward-looking computations (zero look-ahead leakage).
        """
        df_feat = df.copy()
        df_feat["date"] = pd.to_datetime(df_feat["date"])
        df_feat = df_feat.sort_values("date").reset_index(drop=True)

        price = df_feat[self.price_col]

        # 1. Log Returns and Percentage Returns (strictly at day t vs t-1, t-5, etc.)
        df_feat["log_return_1d"] = np.log(price / price.shift(1))
        df_feat["return_1d"] = price.pct_change(1)
        df_feat["return_5d"] = price.pct_change(5)
        df_feat["return_21d"] = price.pct_change(21)  # ~1 trading month
        df_feat["return_30d"] = price.pct_change(30)

        # 2. Lagged Returns (stationary autoregressive inputs)
        df_feat["lag_return_1d_1"] = df_feat["return_1d"].shift(1)
        df_feat["lag_return_1d_5"] = df_feat["return_1d"].shift(5)

        # 3. Normalized Moving Average Ratios (Stationary Mean-Reversion / Trend Ratios)
        # Ratio of current price to rolling moving averages: price / MA(w)
        rolling_windows = [7, 30, 90]
        for w in rolling_windows:
            df_feat[f"rolling_mean_{w}d"] = price.rolling(window=w, min_periods=w).mean()
            df_feat[f"price_to_rolling_mean_{w}d"] = price / df_feat[f"rolling_mean_{w}d"]

        # 50-day and 200-day Moving Averages and Cross Ratio
        df_feat["sma_50d"] = price.rolling(50, min_periods=50).mean()
        df_feat["sma_200d"] = price.rolling(200, min_periods=200).mean()
        df_feat["price_to_sma_50d"] = price / df_feat["sma_50d"]
        df_feat["price_to_sma_200d"] = price / df_feat["sma_200d"]
        df_feat["sma_cross_ratio"] = df_feat["sma_50d"] / df_feat["sma_200d"]

        # 4. Rolling Volatility (7, 30, 90 days annualized std of daily log returns)
        annual_factor = np.sqrt(252)
        for w in rolling_windows:
            df_feat[f"rolling_vol_{w}d"] = (
                df_feat["log_return_1d"].rolling(window=w, min_periods=w).std() * annual_factor
            )

        # 5. USD/INR Exchange Rate Dynamics (normalized)
        if self.fx_col in df_feat.columns:
            fx = df_feat[self.fx_col].ffill()
            df_feat["fx_usdinr_clean"] = fx
            df_feat["fx_return_1d"] = fx.pct_change(1)
            df_feat["fx_return_21d"] = fx.pct_change(21)
            fx_sma30 = fx.rolling(30, min_periods=30).mean()
            df_feat["fx_to_rolling_mean_30d"] = fx / fx_sma30

        # 6. Calendar & Trigonometric Cyclical Seasonality
        dates = df_feat["date"]
        df_feat["day_of_week"] = dates.dt.day_of_week
        df_feat["day_of_month"] = dates.dt.day
        df_feat["month"] = dates.dt.month
        df_feat["quarter"] = dates.dt.quarter

        # Cyclical trigonometric encodings
        df_feat["sin_day_of_week"] = np.sin(2 * np.pi * df_feat["day_of_week"] / 7.0)
        df_feat["cos_day_of_week"] = np.cos(2 * np.pi * df_feat["day_of_week"] / 7.0)
        df_feat["sin_month"] = np.sin(2 * np.pi * df_feat["month"] / 12.0)
        df_feat["cos_month"] = np.cos(2 * np.pi * df_feat["month"] / 12.0)
        df_feat["sin_day_of_year"] = np.sin(2 * np.pi * dates.dt.day_of_year / 365.25)
        df_feat["cos_day_of_year"] = np.cos(2 * np.pi * dates.dt.day_of_year / 365.25)

        # 7. Backward-Compatible Price Lags (for inspection and tests)
        for lag in [1, 5, 10, 20, 30]:
            df_feat[f"lag_price_{lag}d"] = price.shift(lag)

        # Define the dedicated STATIONARY feature set for tree-based modeling
        # Excludes raw price levels to avoid collinearity and extrapolation failure
        self.feature_names = [
            "return_1d", "return_5d", "return_21d", "return_30d", "log_return_1d",
            "lag_return_1d_1", "lag_return_1d_5",
            "price_to_rolling_mean_7d", "price_to_rolling_mean_30d", "price_to_rolling_mean_90d",
            "price_to_sma_50d", "price_to_sma_200d", "sma_cross_ratio",
            "rolling_vol_7d", "rolling_vol_30d", "rolling_vol_90d",
            "fx_return_1d", "fx_return_21d", "fx_to_rolling_mean_30d",
            "sin_day_of_week", "cos_day_of_week", "sin_month", "cos_month",
            "sin_day_of_year", "cos_day_of_year"
        ]

        if drop_na:
            initial_len = len(df_feat)
            check_cols = [c for c in self.feature_names if c in df_feat.columns]
            df_feat = df_feat.dropna(subset=check_cols).reset_index(drop=True)
            logger.info(f"Engineered features for {len(df_feat)} records (dropped {initial_len - len(df_feat)} warm-up rows).")

        return df_feat

    def create_multistep_targets(self, df: pd.DataFrame, horizons: List[int] = [30, 90, 180, 365]) -> pd.DataFrame:
        """
        Creates forward-looking target prices and returns for specified forecast horizons.
        y_target_{h}d = Price at t+h
        target_return_{h}d = (Price at t+h - Price at t) / Price at t
        """
        df_targets = df.copy()
        price = df_targets[self.price_col]

        for h in horizons:
            df_targets[f"target_price_{h}d"] = price.shift(-h)
            df_targets[f"target_return_{h}d"] = (price.shift(-h) - price) / price

        return df_targets
