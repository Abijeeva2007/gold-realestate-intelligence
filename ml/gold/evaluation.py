"""
Model Evaluation, Interval Calibration, and Walk-Forward Validation Module.
Provides mathematically rigorous quantitative metrics:
- MAE, RMSE, MAPE
- Directional Accuracy (Hit Rate: sign of predicted return vs sign of realized return)
- Skill Score vs. Naive Baseline: (1 - RMSE_model / RMSE_naive) * 100%
- Empirical 95% Prediction Interval Coverage (% of observations within [L, U])
- Average Prediction Interval Width ($)
- Annualized Historical Volatility
- Maximum Peak-to-Trough Drawdown
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd

from src.config import setup_logging

logger = setup_logging()

class ModelEvaluator:
    """Evaluates time series forecasting models and validates uncertainty calibration."""

    @staticmethod
    def calculate_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_origin: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Calculates MAE, RMSE, MAPE, and true Horizon Directional Accuracy.
        
        Args:
            y_true: Realized prices at t+h.
            y_pred: Forecast prices at t+h.
            y_origin: Base price at forecast origin t (for calculating directional return correctness).
        """
        y_true = np.asarray(y_true, dtype=float)
        y_pred = np.asarray(y_pred, dtype=float)

        valid_mask = ~np.isnan(y_true) & ~np.isnan(y_pred) & (y_true > 0)
        if y_origin is not None:
            y_origin = np.asarray(y_origin, dtype=float)
            valid_mask = valid_mask & ~np.isnan(y_origin) & (y_origin > 0)

        yt = y_true[valid_mask]
        yp = y_pred[valid_mask]

        if len(yt) == 0:
            return {"mae": np.nan, "rmse": np.nan, "mape": np.nan, "directional_accuracy_pct": np.nan}

        mae = float(np.mean(np.abs(yt - yp)))
        rmse = float(np.sqrt(np.mean((yt - yp) ** 2)))
        mape = float(np.mean(np.abs((yt - yp) / yt)) * 100.0)

        # Correct Horizon Directional Accuracy: Did the model predict the correct sign of price change?
        if y_origin is not None:
            yo = y_origin[valid_mask]
            pred_return_sign = np.sign(yp - yo)
            actual_return_sign = np.sign(yt - yo)
            dir_acc = float(np.mean(pred_return_sign == actual_return_sign) * 100.0)
        else:
            dir_acc = float(np.mean(np.sign(np.diff(yt)) == np.sign(np.diff(yp))) * 100.0) if len(yt) > 1 else np.nan

        return {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "directional_accuracy_pct": round(dir_acc, 2) if not np.isnan(dir_acc) else None
        }

    @staticmethod
    def calculate_interval_metrics(
        y_true: np.ndarray,
        lower_bounds: np.ndarray,
        upper_bounds: np.ndarray
    ) -> Dict[str, float]:
        """
        Validates 95% Prediction Interval Calibration:
        - Empirical Coverage: % of true observations within [Lower, Upper]
        - Average Interval Width: Mean of (Upper - Lower)
        """
        yt = np.asarray(y_true, dtype=float)
        lb = np.asarray(lower_bounds, dtype=float)
        ub = np.asarray(upper_bounds, dtype=float)

        valid = ~np.isnan(yt) & ~np.isnan(lb) & ~np.isnan(ub)
        yt = yt[valid]
        lb = lb[valid]
        ub = ub[valid]

        if len(yt) == 0:
            return {"coverage_95_pct": np.nan, "avg_interval_width_usd": np.nan}

        inside = (yt >= lb) & (yt <= ub)
        coverage = float(np.mean(inside) * 100.0)
        width = float(np.mean(ub - lb))

        return {
            "coverage_95_pct": round(coverage, 2),
            "avg_interval_width_usd": round(width, 2)
        }

    @staticmethod
    def compare_against_baseline(
        metrics_model: Dict[str, float],
        metrics_baseline: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculates skill score relative to naive baseline:
        Skill Score = (1 - RMSE_model / RMSE_baseline) * 100%
        """
        rmse_m = metrics_model.get("rmse")
        rmse_b = metrics_baseline.get("rmse")
        if rmse_m is not None and rmse_b is not None and rmse_b > 0:
            skill = (1.0 - (rmse_m / rmse_b)) * 100.0
            return {"skill_score_pct": round(skill, 2)}
        return {"skill_score_pct": np.nan}

    @staticmethod
    def calculate_annualized_volatility(price_series: pd.Series, periods_per_year: int = 252) -> float:
        """Calculates standard annualized volatility from daily log returns."""
        clean_prices = price_series.dropna()
        log_rets = np.log(clean_prices / clean_prices.shift(1)).dropna()
        if len(log_rets) < 2:
            return 0.0
        return float(log_rets.std() * np.sqrt(periods_per_year) * 100.0)

    @staticmethod
    def calculate_max_drawdown(price_series: pd.Series) -> Dict[str, Any]:
        """Calculates peak-to-trough historical maximum drawdown and peak/trough indices."""
        clean_prices = price_series.dropna().reset_index(drop=True)
        rolling_max = clean_prices.cummax()
        drawdowns = (clean_prices - rolling_max) / rolling_max
        max_dd = float(drawdowns.min() * 100.0)
        trough_idx = int(drawdowns.idxmin())
        peak_idx = int(clean_prices.iloc[:trough_idx + 1].idxmax())

        return {
            "max_drawdown_pct": round(max_dd, 2),
            "peak_price": float(clean_prices.iloc[peak_idx]),
            "trough_price": float(clean_prices.iloc[trough_idx]),
            "peak_idx": peak_idx,
            "trough_idx": trough_idx
        }

    @staticmethod
    def chronological_split(
        df: pd.DataFrame,
        date_col: str = "date",
        train_end: str = "2022-12-31",
        val_end: str = "2023-12-31"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Chronologically partitions data into Train, Validation, and Test sets without look-ahead."""
        df_sort = df.sort_values(date_col).copy()
        dates = pd.to_datetime(df_sort[date_col])

        train_mask = dates <= pd.to_datetime(train_end)
        val_mask = (dates > pd.to_datetime(train_end)) & (dates <= pd.to_datetime(val_end))
        test_mask = dates > pd.to_datetime(val_end)

        df_train = df_sort[train_mask].copy()
        df_val = df_sort[val_mask].copy()
        df_test = df_sort[test_mask].copy()

        logger.info(
            f"Chronological Split: "
            f"Train={len(df_train)} ({df_train[date_col].min()} to {df_train[date_col].max()}), "
            f"Val={len(df_val)} ({df_val[date_col].min()} to {df_val[date_col].max()}), "
            f"Test={len(df_test)} ({df_test[date_col].min()} to {df_test[date_col].max()})"
        )
        return df_train, df_val, df_test
