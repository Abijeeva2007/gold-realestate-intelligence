"""
Test Suite for Gold Price Forecasting Engine and FastAPI Endpoints (Task 02).
Tests:
- Leak-free feature engineering (no future data leakage)
- Chronological train/val/test split purity
- Naive Random Walk Baseline properties (volatility cone expansion)
- Model fitting and prediction interval consistency (ARIMA, Prophet, XGBoost)
- FastAPI endpoints integration (history, forecast, metrics, trends, regimes)
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from ml.gold.feature_engineering import GoldFeatureEngineer
from ml.gold.evaluation import ModelEvaluator
from ml.gold.train_models import (
    NaiveBaselineForecaster,
    ArimaForecaster,
    ProphetForecaster,
    XGBoostMultiHorizonForecaster
)
from src.api.app import app

client = TestClient(app)

@pytest.fixture
def synthetic_gold_series():
    """Generates synthetic daily price history for reproducible unit tests."""
    np.random.seed(42)
    dates = pd.date_range("2018-01-01", periods=1000, freq="B")
    prices = 1300.0 + np.cumsum(np.random.normal(0.5, 8.0, size=len(dates))).clip(min=100)
    fx = 68.0 + np.cumsum(np.random.normal(0.01, 0.15, size=len(dates))).clip(min=10)

    df = pd.DataFrame({
        "date": dates,
        "close_usd_per_troy_oz": prices,
        "fx_usdinr": fx,
        "gold_market_open": True,
        "regime_name": "Test Regime"
    })
    return df


class TestFeatureEngineering:
    def test_no_future_leakage_in_lags(self, synthetic_gold_series):
        fe = GoldFeatureEngineer()
        df_feat = fe.build_features(synthetic_gold_series, drop_na=True)

        # Verify that lag_price_1d at index t is strictly equal to close price at t-1
        for idx in range(1, 15):
            assert df_feat["lag_price_1d"].iloc[idx] == df_feat["close_usd_per_troy_oz"].iloc[idx - 1]
        for idx in range(5, 15):
            assert df_feat["lag_price_5d"].iloc[idx] == df_feat["close_usd_per_troy_oz"].iloc[idx - 5]

    def test_rolling_averages_calculation(self, synthetic_gold_series):
        fe = GoldFeatureEngineer()
        df_feat = fe.build_features(synthetic_gold_series, drop_na=True)

        # Verify rolling mean 7d matches past 7 days average
        expected_7d = df_feat["close_usd_per_troy_oz"].iloc[10-7+1:11].mean()
        assert abs(df_feat["rolling_mean_7d"].iloc[10] - expected_7d) < 1e-4

    def test_multistep_targets_separation(self, synthetic_gold_series):
        fe = GoldFeatureEngineer()
        df_feat = fe.build_features(synthetic_gold_series, drop_na=True)
        df_targets = fe.create_multistep_targets(df_feat, horizons=[30, 90])

        assert "target_price_30d" in df_targets.columns
        assert "target_price_90d" in df_targets.columns
        # Target must NOT be in feature_names
        assert "target_price_30d" not in fe.feature_names
        assert "target_price_90d" not in fe.feature_names


class TestEvaluationAndSplits:
    def test_chronological_splits_strictly_ordered(self, synthetic_gold_series):
        evaluator = ModelEvaluator()
        train, val, test = evaluator.chronological_split(
            synthetic_gold_series,
            date_col="date",
            train_end="2020-06-30",
            val_end="2020-12-31"
        )
        assert train["date"].max() <= pd.to_datetime("2020-06-30")
        assert val["date"].min() > pd.to_datetime("2020-06-30")
        assert val["date"].max() <= pd.to_datetime("2020-12-31")
        assert test["date"].min() > pd.to_datetime("2020-12-31")

    def test_metrics_calculation(self):
        y_true = np.array([100.0, 110.0, 120.0])
        y_pred = np.array([105.0, 108.0, 125.0])
        metrics = ModelEvaluator.calculate_metrics(y_true, y_pred)
        assert metrics["mae"] == round((5.0 + 2.0 + 5.0) / 3, 2)
        assert metrics["rmse"] > 0
        assert metrics["mape"] > 0


class TestModelTraining:
    def test_naive_baseline_volatility_cone(self, synthetic_gold_series):
        naive = NaiveBaselineForecaster().fit(synthetic_gold_series)
        preds = naive.predict(horizons=[30, 90, 180, 365])
        assert len(preds) == 4

        # Confidence intervals must widen as horizon increases
        margins = [p["upper_bound_95"] - p["point_forecast"] for p in preds]
        assert margins[0] < margins[1] < margins[2] < margins[3]

    def test_arima_forecaster_bounds(self, synthetic_gold_series):
        arima = ArimaForecaster(order=(1, 1, 0)).fit(synthetic_gold_series.iloc[:200])
        preds = arima.predict(horizons=[30, 90])
        for p in preds:
            assert p["lower_bound_95"] <= p["point_forecast"] <= p["upper_bound_95"]

    def test_xgboost_forecaster(self, synthetic_gold_series):
        fe = GoldFeatureEngineer()
        df_feat = fe.build_features(synthetic_gold_series.iloc[:300], drop_na=True)
        xgb_m = XGBoostMultiHorizonForecaster(horizons=[30, 90])
        xgb_m.fit(df_feat, feature_cols=fe.feature_names)
        preds = xgb_m.predict(df_feat)
        assert len(preds) == 2
        for p in preds:
            assert p["lower_bound_95"] <= p["point_forecast"] <= p["upper_bound_95"]


class TestFastApiEndpoints:
    def test_get_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ONLINE"

    def test_get_gold_history(self):
        response = client.get("/api/gold/history?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 10
        assert "close_usd_per_troy_oz" in data["data"][0]

    def test_get_gold_forecast(self):
        response = client.get("/api/gold/forecast")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_forecasts"] >= 4

    def test_get_gold_forecast_filtered(self):
        response = client.get("/api/gold/forecast?model=XGBoost&horizon_days=30")
        assert response.status_code == 200
        data = response.json()
        assert len(data["forecasts"]) == 1
        assert data["forecasts"][0]["horizon_days"] == 30
        assert data["forecasts"][0]["model"] == "XGBoost"

    def test_get_gold_metrics(self):
        response = client.get("/api/gold/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["models"]) >= 4

    def test_get_gold_trends(self):
        response = client.get("/api/gold/trends")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        analysis = data["market_analysis"]
        assert analysis["trend"]["classification"] in ["Bullish", "Bearish", "Sideways / Consolidating"]
        assert "sma_50d" in analysis["trend"]
        assert "rolling_vol_30d_pct" in analysis["volatility"]

    def test_get_gold_regimes(self):
        response = client.get("/api/gold/regimes")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_regimes"] >= 5
