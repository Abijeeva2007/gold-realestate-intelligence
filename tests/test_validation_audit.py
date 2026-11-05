"""
Research Validation and Correction Audit Test Suite (Task 02).
Validates:
1. Latest-date consistency and price series integrity.
2. Forecast-origin consistency.
3. Target alignment and zero-leakage feature construction.
4. Chronological walk-forward validation without data leakage.
5. Prediction interval coverage and monotonic width expansion.
6. Maximum drawdown calculation and historical peak/trough verification.
7. Annualized volatility calculation with standard financial square-root scaling.
8. Naive baseline comparison and horizon directional accuracy.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from ml.gold.feature_engineering import GoldFeatureEngineer
from ml.gold.evaluation import ModelEvaluator
from ml.gold.train_models import NaiveBaselineForecaster, XGBoostMultiHorizonForecaster


PROCESSED_DIR = Path("data/processed")
MASTER_DATA_PATH = PROCESSED_DIR / "gold_master_daily_unified.csv"
PREDICTIONS_PATH = PROCESSED_DIR / "validated_predictions.csv"
METRICS_PATH = PROCESSED_DIR / "validated_model_metrics.csv"
FEATURE_IMPORTANCE_PATH = PROCESSED_DIR / "validated_feature_importance.csv"


class TestValidationAudit:

    # -------------------------------------------------------------
    # 1. Latest-Date & Price Consistency
    # -------------------------------------------------------------
    def test_latest_date_consistency(self):
        """Verify the unified master dataset contains authentic 2026 data up to Nov 2026 and ATH $5,318.40."""
        assert MASTER_DATA_PATH.exists(), f"Missing {MASTER_DATA_PATH}"
        df = pd.read_csv(MASTER_DATA_PATH)
        df["date"] = pd.to_datetime(df["date"])

        latest_date = df["date"].max()
        assert latest_date >= pd.to_datetime("2026-11-04"), (
            f"Expected latest date >= 2026-11-04, found {latest_date}"
        )

        max_price = df["close_usd_per_troy_oz"].max()
        assert abs(max_price - 5318.40) < 0.1, (
            f"Expected CME ATH $5,318.40, found ${max_price:.2f}. "
            "Verify synthetic test fixture did not overwrite master CSV."
        )

        # Confirm trading rows count is ~6,571
        valid_trading_days = df["close_usd_per_troy_oz"].dropna()
        assert len(valid_trading_days) >= 6500

    # -------------------------------------------------------------
    # 2. Forecast-Origin Consistency
    # -------------------------------------------------------------
    def test_forecast_origin_consistency(self):
        """Verify all production models share the identical forecast origin and spot base price."""
        assert PREDICTIONS_PATH.exists(), f"Missing {PREDICTIONS_PATH}"
        df_pred = pd.read_csv(PREDICTIONS_PATH)

        assert len(df_pred) == 16, f"Expected 16 predictions (4 models x 4 horizons), found {len(df_pred)}"

        # All models must use the latest observation date as origin
        unique_origins = df_pred["forecast_origin_date"].unique()
        assert len(unique_origins) == 1
        assert unique_origins[0] == "2026-11-04"

        # All models must anchor on the latest market close price
        unique_base_prices = df_pred["current_price_usd"].unique()
        assert len(unique_base_prices) == 1
        assert abs(unique_base_prices[0] - 4073.00) < 0.1

        # Check all 4 models and 4 horizons are represented
        expected_models = {"Naive Random Walk", "ARIMA", "Prophet", "XGBoost"}
        assert set(df_pred["model"].unique()) == expected_models
        assert set(df_pred["horizon_days"].unique()) == {30, 90, 180, 365}

    # -------------------------------------------------------------
    # 3. Target Alignment
    # -------------------------------------------------------------
    def test_target_alignment(self):
        """Verify targets are correctly shifted by horizon h without look-ahead in features."""
        dates = pd.date_range("2020-01-01", periods=100, freq="B")
        prices = np.linspace(1500, 2000, 100)
        df = pd.DataFrame({"date": dates, "close_usd_per_troy_oz": prices})

        fe = GoldFeatureEngineer()
        df_feat = fe.build_features(df, drop_na=False)
        df_targets = fe.create_multistep_targets(df_feat, horizons=[30, 90])

        # At index i, target for h=30 must be exactly close price at i+30
        for i in range(20):
            expected_target_30 = df_feat["close_usd_per_troy_oz"].iloc[i + 30]
            assert df_targets["target_price_30d"].iloc[i] == expected_target_30

            expected_return_30 = (expected_target_30 - df_feat["close_usd_per_troy_oz"].iloc[i]) / df_feat["close_usd_per_troy_oz"].iloc[i]
            assert abs(df_targets["target_return_30d"].iloc[i] - expected_return_30) < 1e-6

        # Target columns must never leak into feature set
        for f in fe.feature_names:
            assert not f.startswith("target_")

    # -------------------------------------------------------------
    # 4. Walk-Forward Leakage Prevention
    # -------------------------------------------------------------
    def test_walk_forward_leakage(self):
        """Verify feature engineering at time t is strictly invariant to future observations."""
        fe = GoldFeatureEngineer()

        dates = pd.date_range("2021-01-01", periods=300, freq="B")
        np.random.seed(123)
        prices = 1800.0 + np.cumsum(np.random.normal(0, 10, size=len(dates)))
        fx = 75.0 + np.cumsum(np.random.normal(0, 0.1, size=len(dates)))
        df_full = pd.DataFrame({"date": dates, "close_usd_per_troy_oz": prices, "fx_usdinr": fx})

        # Calculate features on full series
        df_feat_full = fe.build_features(df_full, drop_na=True)

        # Calculate features on truncated series (up to index 200)
        df_trunc = df_full.iloc[:200].copy()
        df_feat_trunc = fe.build_features(df_trunc, drop_na=True)

        # For common historical indices, feature values must match identically
        overlap_idx = df_feat_trunc.index
        for col in fe.feature_names:
            diff = np.abs(df_feat_full.loc[overlap_idx, col] - df_feat_trunc.loc[overlap_idx, col])
            assert diff.max() < 1e-8, f"Feature {col} leaked future data!"

    # -------------------------------------------------------------
    # 5. Prediction Interval Coverage Calculations
    # -------------------------------------------------------------
    def test_prediction_interval_coverage_calculations(self):
        """Verify empirical coverage and width calculations."""
        y_true = np.array([100.0, 105.0, 95.0, 110.0, 90.0])
        # Lower bound 92, upper bound 108 -> covers 100, 105, 95 (3 out of 5 = 60%)
        lb = np.array([92.0] * 5)
        ub = np.array([108.0] * 5)

        ci_stats = ModelEvaluator.calculate_interval_metrics(y_true, lb, ub)
        assert ci_stats["coverage_95_pct"] == 60.0
        assert ci_stats["avg_interval_width_usd"] == 16.0

        # Monotonic cone expansion check in actual saved predictions
        df_pred = pd.read_csv(PREDICTIONS_PATH)
        for model_name in ["Naive Random Walk", "ARIMA", "XGBoost"]:
            sub = df_pred[df_pred["model"] == model_name].sort_values("horizon_days")
            widths = (sub["upper_bound_95_usd"] - sub["lower_bound_95_usd"]).tolist()
            # Interval widths must strictly expand as horizon increases
            assert widths[0] < widths[1] < widths[2] < widths[3], (
                f"Prediction interval width failed to expand monotonically for {model_name}: {widths}"
            )

    # -------------------------------------------------------------
    # 6. Maximum Drawdown Calculation
    # -------------------------------------------------------------
    def test_maximum_drawdown(self):
        """Verify historical maximum drawdown calculation matches financial reality."""
        # Test synthetic series: 100 -> 150 -> 75 -> 120 -> max drawdown is (75 - 150) / 150 = -50%
        synthetic = pd.Series([100.0, 150.0, 75.0, 120.0])
        dd = ModelEvaluator.calculate_max_drawdown(synthetic)
        assert dd["max_drawdown_pct"] == -50.0
        assert dd["peak_price"] == 150.0
        assert dd["trough_price"] == 75.0

        # Test full master dataset historical drawdown
        df_master = pd.read_csv(MASTER_DATA_PATH)
        prices = df_master["close_usd_per_troy_oz"].dropna()
        hist_dd = ModelEvaluator.calculate_max_drawdown(prices)

        # Gold post-2011 peak (~$1,888) to late 2015 low (~$1,050) was -44.36%
        assert -46.0 <= hist_dd["max_drawdown_pct"] <= -43.0, (
            f"Expected historical max drawdown around -44.36%, got {hist_dd['max_drawdown_pct']}%"
        )
        assert hist_dd["peak_price"] > 1800.0
        assert hist_dd["trough_price"] < 1100.0

    # -------------------------------------------------------------
    # 7. Annualized Volatility Calculation
    # -------------------------------------------------------------
    def test_annualized_volatility(self):
        """Verify annualized volatility is scaled by sqrt(252) and matches authentic ~18%."""
        df_master = pd.read_csv(MASTER_DATA_PATH)
        prices = df_master["close_usd_per_troy_oz"].dropna()

        vol = ModelEvaluator.calculate_annualized_volatility(prices)
        # Gold historical annualized volatility is ~17.98%
        assert 16.0 <= vol <= 20.0, (
            f"Expected annualized volatility between 16% and 20%, got {vol:.2f}%. "
            "Rejecting erroneous synthetic 2.71%."
        )

    # -------------------------------------------------------------
    # 8. Naive Baseline Comparison & Directional Accuracy
    # -------------------------------------------------------------
    def test_naive_baseline_comparison(self):
        """Verify baseline comparison across horizons and non-degenerate directional accuracy."""
        assert METRICS_PATH.exists(), f"Missing {METRICS_PATH}"
        df_metrics = pd.read_csv(METRICS_PATH)

        # Baseline skill score must be exactly 0
        naive_rows = df_metrics[df_metrics["model"] == "Naive Random Walk Baseline"]
        assert len(naive_rows) == 4
        assert (naive_rows["skill_score_pct"] == 0.0).all()

        # XGBoost multi-step directional accuracy test
        xgb_rows = df_metrics[df_metrics["model"] == "XGBoost (Time-Series Features)"]
        assert len(xgb_rows) == 4

        # With correct sign(y_t+h - y_t) == sign(y_pred - y_t) definition,
        # directional accuracy across horizons is strong (>= 60%),
        # resolving the flawed 0.41% daily-diff artifact.
        for _, r in xgb_rows.iterrows():
            assert r["directional_accuracy_pct"] >= 60.0, (
                f"Horizon {r['horizon_days']} directional accuracy {r['directional_accuracy_pct']}% is below expected threshold."
            )


class TestRegressionAndDefectVerification:
    """Regression tests for all confirmed audit defects and behavioral edge cases."""

    def test_defect_production_dataset_cannot_be_overwritten_by_merger(self):
        """Regression test: Ensure calling DataMerger with save_to_disk=False never touches disk."""
        import hashlib
        from src.processors.merger import DataMerger

        assert MASTER_DATA_PATH.exists()
        pre_hash = hashlib.sha256(MASTER_DATA_PATH.read_bytes()).hexdigest()

        # Run merger with synthetic data and save_to_disk=False
        fake_gold = pd.DataFrame({
            "date": pd.date_range("2020-01-01", periods=10),
            "close_usd_per_troy_oz": [100.0] * 10,
            "open_usd_per_troy_oz": [100.0] * 10,
            "high_usd_per_troy_oz": [105.0] * 10,
            "low_usd_per_troy_oz": [95.0] * 10,
            "volume": [1000.0] * 10,
            "gold_market_open": True
        })
        fake_fx = pd.DataFrame({
            "date": pd.date_range("2020-01-01", periods=10),
            "fx_usdinr": [70.0] * 10
        })

        merger = DataMerger()
        merged_df, _ = merger.build_master_daily_dataset(fake_gold, fake_fx, save_to_disk=False)
        assert len(merged_df) == 10

        # Verify production dataset on disk was completely untouched
        post_hash = hashlib.sha256(MASTER_DATA_PATH.read_bytes()).hexdigest()
        assert pre_hash == post_hash, "Regression: Master unified CSV was modified by DataMerger call!"

    def test_defect_api_endpoints_all_load_latest_nov_2026_date(self):
        """Regression test: Ensure all API endpoints expose the authentic Nov 4, 2026 data."""
        from fastapi.testclient import TestClient
        from src.api.app import app

        client = TestClient(app)

        # /api/gold/history
        res_hist = client.get("/api/gold/history?limit=1").json()
        assert res_hist["data"][0]["date"] == "2026-11-04"
        assert abs(res_hist["data"][0]["close_usd_per_troy_oz"] - 4073.0) < 0.1

        # /api/gold/forecast
        res_fc = client.get("/api/gold/forecast").json()
        assert res_fc["forecast_origin_date"] == "2026-11-04"
        assert abs(res_fc["current_price_usd"] - 4073.0) < 0.1

        # /api/gold/trends
        res_tr = client.get("/api/gold/trends").json()
        assert res_tr["market_analysis"]["latest_date"] == "2026-11-04"
        assert abs(res_tr["market_analysis"]["current_price_usd"] - 4073.0) < 0.1

    def test_defect_naive_directional_accuracy_mechanics(self):
        """Regression test: Mathematically proves why Naive persistence yields 0% directional accuracy."""
        yo = np.array([100.0, 105.0, 110.0])
        # Naive forecast is always persistence: y_pred == y_origin
        yp_naive = yo.copy()
        # Realized prices have moved up or down
        yt = np.array([102.0, 101.0, 115.0])

        metrics = ModelEvaluator.calculate_metrics(yt, yp_naive, y_origin=yo)
        # Because yp - yo == 0, sign is 0. sign(yt - yo) is +1 or -1. 0 == +1 is False.
        assert metrics["directional_accuracy_pct"] == 0.0

    def test_defect_xgboost_365d_directional_accuracy_mechanics(self):
        """Regression test: Verifies that 100% directional accuracy in 2024-2026 was driven by secular bull regime."""
        df_metrics = pd.read_csv(METRICS_PATH)
        xgb_365 = df_metrics[(df_metrics["model"] == "XGBoost (Time-Series Features)") & (df_metrics["horizon_days"] == 365)]
        assert len(xgb_365) == 1
        assert xgb_365["directional_accuracy_pct"].iloc[0] == 100.0

        # Confirm that the out-of-sample test set (2024-2026) experienced strictly positive 365d returns
        df_master = pd.read_csv(MASTER_DATA_PATH)
        df_master = df_master[df_master["gold_market_open"]].sort_values("date").reset_index(drop=True)
        test_indices = df_master[df_master["date"] >= "2024-01-02"].index
        valid_365 = [i for i in test_indices if i + 365 < len(df_master)]

        y_origin = df_master.loc[valid_365, "close_usd_per_troy_oz"].values
        y_future = df_master.loc[[i + 365 for i in valid_365], "close_usd_per_troy_oz"].values
        actual_returns = (y_future - y_origin) / y_origin

        # All 351 test origins had positive 365-day forward returns in reality
        assert (actual_returns > 0).all()

    def test_defect_fastapi_nan_serialization_safety(self):
        """Regression test: Ensure missing FX or NaN floats never crash the API with JSON compliance errors."""
        from fastapi.testclient import TestClient
        from src.api.app import app

        client = TestClient(app)
        # Fetch 200 history items which contain market holiday NaN FX records
        response = client.get("/api/gold/history?limit=200")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # None/null must be present for some FX fields without crash
        fx_values = [r["fx_usdinr"] for r in data["data"]]
        assert any(v is None for v in fx_values)

