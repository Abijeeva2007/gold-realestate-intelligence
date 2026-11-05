"""
Multi-Horizon Forecasting Engine Module.
Generates 30-day, 90-day, 180-day, and 365-day forecasts across all models:
1. Naive Random Walk Baseline
2. ARIMA
3. Prophet
4. XGBoost

Produces:
- data/processed/gold_predictions.csv
- data/processed/validated_predictions.csv
with point forecasts and 95% uncertainty intervals.
"""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np

from src.config import BASE_DIR, PROCESSED_DATA_DIR, setup_logging
from ml.gold.feature_engineering import GoldFeatureEngineer
from ml.gold.train_models import (
    NaiveBaselineForecaster,
    ArimaForecaster,
    ProphetForecaster,
    XGBoostMultiHorizonForecaster,
    save_models_artifacts
)

logger = setup_logging()

class GoldForecastingEngine:
    """Executes multi-horizon forecasting across all 4 statistical & machine learning models."""

    def __init__(self, data_path: Path = None):
        self.data_path = data_path or (BASE_DIR / "data" / "processed" / "gold_master_daily_unified.csv")
        self.processed_dir = Path(PROCESSED_DATA_DIR)
        self.horizons = [30, 90, 180, 365]

        self.feature_engineer = GoldFeatureEngineer()
        self.naive_model = NaiveBaselineForecaster()
        self.arima_model = ArimaForecaster(order=(1, 1, 1))
        self.prophet_model = ProphetForecaster()
        self.xgb_model = XGBoostMultiHorizonForecaster(horizons=self.horizons)

    def run_pipeline(self) -> Dict[str, Any]:
        """Loads validated data, trains all models, and generates unified predictions tables."""
        logger.info("================================================================")
        logger.info("EXECUTING GOLD MULTI-HORIZON FORECASTING ENGINE")
        logger.info("================================================================")

        df_raw = pd.read_csv(self.data_path)
        df_gold = df_raw[df_raw["gold_market_open"]].sort_values("date").reset_index(drop=True)
        current_price = float(df_gold["close_usd_per_troy_oz"].iloc[-1])
        latest_date = pd.to_datetime(df_gold["date"].iloc[-1])

        logger.info(f"Loaded {len(df_gold)} historical trading records up to {latest_date.date()} (${current_price:,.2f}/oz).")

        # 1. Feature Engineering (strictly backward-looking)
        df_feat = self.feature_engineer.build_features(df_gold, drop_na=True)
        feature_cols = self.feature_engineer.feature_names

        # 2. Fit Models on historical series
        logger.info("Fitting Naive Baseline...")
        self.naive_model.fit(df_feat)

        logger.info("Fitting ARIMA Model...")
        self.arima_model.fit(df_feat)

        logger.info("Fitting Prophet Model...")
        self.prophet_model.fit(df_feat)

        logger.info("Fitting Multi-Horizon XGBoost...")
        self.xgb_model.fit(df_feat, feature_cols=feature_cols)

        # 3. Save Model Artifacts
        save_models_artifacts(
            self.naive_model,
            self.arima_model,
            self.prophet_model,
            self.xgb_model,
            self.feature_engineer
        )

        # 4. Generate Predictions for 30d, 90d, 180d, 365d
        preds_naive = self.naive_model.predict(self.horizons)
        preds_arima = self.arima_model.predict(self.horizons)
        preds_prophet = self.prophet_model.predict(self.horizons)
        preds_xgb = self.xgb_model.predict(df_feat, current_price=current_price)

        all_preds = preds_naive + preds_arima + preds_prophet + preds_xgb

        rows = []
        for p in all_preds:
            h = p["horizon_days"]
            # Target calendar date approx (1.4 trading days per calendar day)
            target_date = latest_date + pd.Timedelta(days=int(h * 1.45))
            point = p["point_forecast"]
            ret_pct = ((point - current_price) / current_price) * 100.0

            rows.append({
                "model": p["model"],
                "horizon_days": h,
                "forecast_origin_date": str(latest_date.date()),
                "target_date_approx": str(target_date.date()),
                "current_price_usd": round(current_price, 2),
                "point_forecast_usd": point,
                "lower_bound_95_usd": p["lower_bound_95"],
                "upper_bound_95_usd": p["upper_bound_95"],
                "forecast_return_pct": round(ret_pct, 2)
            })

        df_preds = pd.DataFrame(rows)
        
        # Save both gold_predictions.csv and validated_predictions.csv
        pred_path = self.processed_dir / "gold_predictions.csv"
        val_pred_path = self.processed_dir / "validated_predictions.csv"
        
        df_preds.to_csv(pred_path, index=False)
        df_preds.to_csv(val_pred_path, index=False)
        logger.info(f"Saved predictions to {pred_path} and {val_pred_path}")

        return {
            "latest_date": str(latest_date.date()),
            "current_price": current_price,
            "predictions_df": df_preds,
            "predictions_path": str(pred_path)
        }

if __name__ == "__main__":
    engine = GoldForecastingEngine()
    engine.run_pipeline()
