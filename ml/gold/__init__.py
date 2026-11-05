"""
Machine Learning & Forecasting Package for Gold Intelligence.
"""

from ml.gold.feature_engineering import GoldFeatureEngineer
from ml.gold.evaluation import ModelEvaluator
from ml.gold.train_models import (
    NaiveBaselineForecaster,
    ArimaForecaster,
    ProphetForecaster,
    XGBoostMultiHorizonForecaster
)
from ml.gold.forecasting import GoldForecastingEngine
from ml.gold.model_comparison import GoldModelComparisonEngine

__all__ = [
    "GoldFeatureEngineer",
    "ModelEvaluator",
    "NaiveBaselineForecaster",
    "ArimaForecaster",
    "ProphetForecaster",
    "XGBoostMultiHorizonForecaster",
    "GoldForecastingEngine",
    "GoldModelComparisonEngine"
]
