"""
Model Training and Forecasting Architectures Module.
Implements:
1. Naive Random Walk Baseline (persistence model with training volatility cone)
2. ARIMA Time Series Model (ARIMA(1,1,1) with analytical statistical intervals)
3. Facebook Prophet Model (additive seasonal decomposition with Bayesian intervals)
4. XGBoost Multi-Horizon Direct Return Regressors (gradient-boosted trees with SHAP explainability)

Strictly avoids look-ahead leakage and saves trained model artifacts to models/gold/.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import joblib
import numpy as np
import pandas as pd

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import xgboost as xgb
import shap

from src.config import BASE_DIR, setup_logging
from ml.gold.feature_engineering import GoldFeatureEngineer
from ml.gold.evaluation import ModelEvaluator

logger = setup_logging()

MODELS_DIR = BASE_DIR / "models" / "gold"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


class NaiveBaselineForecaster:
    """
    Naive Random Walk Benchmark Forecaster.
    Under the Random Walk Hypothesis, expected future price equals the latest observed price:
    y_hat(t+h) = y(t).
    Uncertainty bounds scale with historical training volatility: +/- 1.96 * sigma_train * sqrt(h/252).
    """

    def __init__(self):
        self.last_observed_price: float = 0.0
        self.last_observed_date: Optional[pd.Timestamp] = None
        self.annualized_vol: float = 0.1798  # historical baseline ~18%

    def fit(self, df_train: pd.DataFrame, price_col: str = "close_usd_per_troy_oz", date_col: str = "date"):
        df_sort = df_train.sort_values(date_col)
        self.last_observed_price = float(df_sort[price_col].iloc[-1])
        self.last_observed_date = pd.to_datetime(df_sort[date_col].iloc[-1])
        
        # Calculate training volatility strictly from training period
        returns = df_sort[price_col].pct_change().dropna()
        if len(returns) > 30:
            self.annualized_vol = float(returns.std() * np.sqrt(252))
        return self

    def predict(self, horizons: List[int] = [30, 90, 180, 365]) -> List[Dict[str, Any]]:
        results = []
        for h in horizons:
            horizon_vol = self.annualized_vol * np.sqrt(h / 252.0)
            margin = 1.96 * horizon_vol * self.last_observed_price
            results.append({
                "model": "Naive Random Walk",
                "horizon_days": h,
                "point_forecast": round(self.last_observed_price, 2),
                "lower_bound_95": round(max(0.0, self.last_observed_price - margin), 2),
                "upper_bound_95": round(self.last_observed_price + margin, 2),
                "volatility_used": round(self.annualized_vol, 4)
            })
        return results

    def predict_test_series(self, base_prices: np.ndarray, horizon: int = 30) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """For walk-forward testing: persistence forecast equals base price at origin."""
        bp = np.asarray(base_prices, dtype=float)
        margin = 1.96 * (self.annualized_vol * np.sqrt(horizon / 252.0)) * bp
        return bp, np.maximum(0.0, bp - margin), bp + margin


class ArimaForecaster:
    """
    ARIMA Time Series Forecaster using statsmodels.
    Configured with ARIMA(1, 1, 1) on gold price series.
    Generates analytical point forecasts and 95% confidence intervals.
    """

    def __init__(self, order: Tuple[int, int, int] = (1, 1, 1)):
        self.order = order
        self.fitted_model = None
        self.last_date = None
        self.last_price = 0.0

    def fit(self, df_train: pd.DataFrame, price_col: str = "close_usd_per_troy_oz", date_col: str = "date"):
        df_sort = df_train.sort_values(date_col)
        prices = df_sort[price_col].astype(float).values
        self.last_date = pd.to_datetime(df_sort[date_col].iloc[-1])
        self.last_price = float(prices[-1])

        logger.info(f"Fitting ARIMA{self.order} model on {len(prices)} training observations...")
        model = ARIMA(prices, order=self.order)
        self.fitted_model = model.fit()
        return self

    def predict(self, horizons: List[int] = [30, 90, 180, 365]) -> List[Dict[str, Any]]:
        if not self.fitted_model:
            raise RuntimeError("ARIMA model must be fitted before predict().")

        max_h = max(horizons)
        forecast_res = self.fitted_model.get_forecast(steps=max_h)
        pred_means = forecast_res.predicted_mean
        conf_ints = forecast_res.conf_int(alpha=0.05)

        results = []
        for h in horizons:
            idx = h - 1
            results.append({
                "model": "ARIMA",
                "horizon_days": h,
                "point_forecast": round(float(pred_means[idx]), 2),
                "lower_bound_95": round(max(0.0, float(conf_ints[idx, 0])), 2),
                "upper_bound_95": round(float(conf_ints[idx, 1]), 2)
            })
        return results

    def predict_test_series(self, n_steps: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if not self.fitted_model:
            raise RuntimeError("ARIMA model must be fitted before predict.")
        res = self.fitted_model.get_forecast(steps=n_steps)
        conf = res.conf_int(alpha=0.05)
        return res.predicted_mean, np.maximum(0.0, conf[:, 0]), conf[:, 1]


class ProphetForecaster:
    """
    Facebook Prophet Forecaster.
    Decomposes price series into trend, weekly seasonality, and yearly seasonality.
    """

    def __init__(self):
        self.model = None

    def fit(self, df_train: pd.DataFrame, price_col: str = "close_usd_per_troy_oz", date_col: str = "date"):
        df_prophet = pd.DataFrame({
            "ds": pd.to_datetime(df_train[date_col]),
            "y": df_train[price_col].astype(float)
        }).sort_values("ds").reset_index(drop=True)

        logger.info(f"Fitting Prophet model on {len(df_prophet)} historical records...")
        self.model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.95
        )
        self.model.fit(df_prophet)
        return self

    def predict(self, horizons: List[int] = [30, 90, 180, 365]) -> List[Dict[str, Any]]:
        if not self.model:
            raise RuntimeError("Prophet model must be fitted before predict.")

        max_h = max(horizons)
        future = self.model.make_future_dataframe(periods=max_h, freq="B")
        forecast = self.model.predict(future)

        future_rows = forecast.iloc[-max_h:].reset_index(drop=True)

        results = []
        for h in horizons:
            idx = min(h - 1, len(future_rows) - 1)
            row = future_rows.iloc[idx]
            results.append({
                "model": "Prophet",
                "horizon_days": h,
                "point_forecast": round(float(row["yhat"]), 2),
                "lower_bound_95": round(max(0.0, float(row["yhat_lower"])), 2),
                "upper_bound_95": round(float(row["yhat_upper"]), 2)
            })
        return results

    def predict_test_series(self, test_dates: pd.Series) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        future = pd.DataFrame({"ds": pd.to_datetime(test_dates)})
        forecast = self.model.predict(future)
        return (
            forecast["yhat"].values,
            np.maximum(0.0, forecast["yhat_lower"].values),
            forecast["yhat_upper"].values
        )


class XGBoostMultiHorizonForecaster:
    """
    XGBoost Direct Multi-Horizon Return Forecaster.
    Trains dedicated gradient boosted tree regressors to predict forward returns R_{t, t+h}
    using strictly stationary, leak-free features.
    
    Reconstructs price forecasts as: y_hat_{t+h} = y_t * (1 + R_hat_{t, t+h}).
    Derives prediction intervals from training set residual standard deviation of returns.
    Computes SHAP explainability on held-out validation/test observations.
    """

    def __init__(self, horizons: List[int] = [30, 90, 180, 365]):
        self.horizons = horizons
        self.models: Dict[int, xgb.XGBRegressor] = {}
        self.residual_return_std: Dict[int, float] = {}
        self.feature_names: List[str] = []
        self.feature_importance_df = pd.DataFrame()

    def fit(
        self,
        df_feat_train: pd.DataFrame,
        feature_cols: List[str],
        price_col: str = "close_usd_per_troy_oz"
    ):
        self.feature_names = feature_cols
        X_train = df_feat_train[feature_cols].copy()
        price_train = df_feat_train[price_col]

        for h in self.horizons:
            logger.info(f"Training XGBoost return regressor for horizon {h} days...")
            # Target is the forward return from t to t + h: (y_{t+h} - y_t) / y_t
            target_return_h = (price_train.shift(-h) - price_train) / price_train
            
            valid_idx = target_return_h.notna()
            X_h = X_train[valid_idx]
            y_h = target_return_h[valid_idx]

            model = xgb.XGBRegressor(
                n_estimators=120,
                max_depth=3,
                learning_rate=0.03,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_h, y_h)
            self.models[h] = model

            # Uncertainty estimate calculated strictly from training residuals (zero test leakage)
            y_pred_train = model.predict(X_h)
            residuals = y_h - y_pred_train
            self.residual_return_std[h] = float(np.std(residuals))

        return self

    def compute_shap_importance(self, X_held_out: pd.DataFrame, horizon: int = 30) -> pd.DataFrame:
        """Computes SHAP TreeExplainer feature importance on held-out test data."""
        try:
            logger.info("Computing SHAP feature importance on held-out observations...")
            model = self.models[horizon]
            X_eval = X_held_out[self.feature_names]
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer.shap_values(X_eval)
            mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)

            fi_df = pd.DataFrame({
                "feature": self.feature_names,
                "importance_mean_abs_shap": mean_abs_shap
            }).sort_values("importance_mean_abs_shap", ascending=False).reset_index(drop=True)

            self.feature_importance_df = fi_df
            return fi_df
        except Exception as exc:
            logger.warning(f"SHAP explanation notice: {exc}")
            return pd.DataFrame()

    def predict(self, latest_feature_row: pd.DataFrame, current_price: Optional[float] = None) -> List[Dict[str, Any]]:
        """Generates multi-horizon forecasts and intervals from latest feature state."""
        if current_price is None:
            if "close_usd_per_troy_oz" in latest_feature_row.columns:
                current_price = float(latest_feature_row["close_usd_per_troy_oz"].iloc[-1])
            else:
                current_price = 1.0
        X_now = latest_feature_row[self.feature_names].iloc[-1:]
        results = []
        for h in self.horizons:
            model = self.models[h]
            pred_return = float(model.predict(X_now)[0])
            pred_price = current_price * (1.0 + pred_return)
            
            # 95% Interval: price * 1.96 * residual_return_std
            res_std = self.residual_return_std.get(h, 0.05)
            margin = 1.96 * res_std * current_price

            results.append({
                "model": "XGBoost",
                "horizon_days": h,
                "point_forecast": round(pred_price, 2),
                "lower_bound_95": round(max(0.0, pred_price - margin), 2),
                "upper_bound_95": round(pred_price + margin, 2),
                "expected_return_pct": round(pred_return * 100.0, 2)
            })
        return results

    def predict_test_series(
        self,
        df_test_feat: pd.DataFrame,
        base_prices: np.ndarray,
        horizon: int = 30
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Walk-forward test predictions: predicted price = base_price * (1 + predicted_return)."""
        model = self.models[horizon]
        pred_returns = model.predict(df_test_feat[self.feature_names])
        bp = np.asarray(base_prices, dtype=float)
        pred_prices = bp * (1.0 + pred_returns)
        
        res_std = self.residual_return_std.get(horizon, 0.05)
        margin = 1.96 * res_std * bp
        return pred_prices, np.maximum(0.0, pred_prices - margin), pred_prices + margin


def save_models_artifacts(
    naive_model: NaiveBaselineForecaster,
    arima_model: ArimaForecaster,
    prophet_model: ProphetForecaster,
    xgb_model: XGBoostMultiHorizonForecaster,
    feature_engineer: GoldFeatureEngineer
):
    """Persists model objects and feature engineer pipeline to disk."""
    joblib.dump(naive_model, MODELS_DIR / "naive_baseline.joblib")
    joblib.dump(arima_model, MODELS_DIR / "arima_model.joblib")
    joblib.dump(prophet_model, MODELS_DIR / "prophet_model.joblib")
    joblib.dump(xgb_model, MODELS_DIR / "xgboost_models.joblib")
    joblib.dump(feature_engineer, MODELS_DIR / "feature_engineer.joblib")
    logger.info(f"Saved all model artifacts to {MODELS_DIR}")
