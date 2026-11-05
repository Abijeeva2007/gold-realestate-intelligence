"""
Unit and Integration Test Suite for the Gold Data Engineering Pipeline.
Tests:
- Date range span (> 20 years target)
- Zero duplicate timestamps
- Strict non-interpolation policy (is_interpolated is always False)
- Valuation sanity bounds (USD gold prices, USD/INR exchange rates)
- Exact mathematical identity of theoretical Indian gold parity
- Market regime classification for 2008, 2020, and 2024-2026
- Database schema and persistence
"""

import pytest
import pandas as pd
import numpy as np

from src.config import TROY_OUNCE_TO_GRAMS, PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.processors.cleaner import DataCleaner
from src.processors.regime_detector import RegimeDetector
from src.processors.merger import DataMerger
from src.validators.data_validator import DataValidator
from src.db.database import get_engine, init_db, load_dataframe_to_db

@pytest.fixture
def sample_daily_data():
    """Generates synthetic multi-year daily market records for deterministic unit testing."""
    dates = pd.date_range(start="2000-01-01", end="2026-01-01", freq="B")
    np.random.seed(42)
    
    # Synthetic random walk within realistic historical bounds
    prices = 300.0 + np.cumsum(np.random.normal(0.5, 5, size=len(dates))).clip(min=0)
    fx = 43.0 + np.cumsum(np.random.normal(0.01, 0.1, size=len(dates))).clip(min=0)

    df_gold = pd.DataFrame({
        "Date": dates,
        "Open": prices * 0.99,
        "High": prices * 1.01,
        "Low": prices * 0.98,
        "Close": prices,
        "Volume": 100000
    })

    df_fx = pd.DataFrame({
        "Date": dates,
        "Close": fx
    })

    return df_gold, df_fx

class TestDataCleaner:
    def test_clean_comex_gold_standards(self, sample_daily_data):
        raw_gold, _ = sample_daily_data
        clean_df, metrics = DataCleaner.clean_comex_gold(raw_gold)

        assert "date" in clean_df.columns
        assert "close_usd_per_troy_oz" in clean_df.columns
        assert clean_df["is_interpolated"].all() == False
        assert clean_df.duplicated(subset=["date"]).sum() == 0
        assert (clean_df["close_usd_per_troy_oz"] > 0).all()

    def test_clean_usdinr_fx_standards(self, sample_daily_data):
        _, raw_fx = sample_daily_data
        clean_fx, metrics = DataCleaner.clean_usdinr_fx(raw_fx, source_type="yahoo")

        assert "date" in clean_fx.columns
        assert "fx_usdinr" in clean_fx.columns
        assert clean_fx["is_interpolated"].all() == False
        assert clean_fx.duplicated(subset=["date"]).sum() == 0
        assert (clean_fx["fx_usdinr"] > 0).all()

    def test_rbi_annual_cleaning(self):
        raw_rbi = pd.DataFrame({
            "financial_year": ["2022-23", "2023-24", "2024-25"],
            "gold_mumbai_inr_per_10g": ["52,730.77", "60,623.95", "75,841.87"],
            "gold_london_usd_per_troy_oz": ["1,804.82", "1,989.00", "2,584.53"],
            "spread_inr_per_10g": ["6,125.03", "7,939.53", "5,526.46"]
        })
        clean_rbi, metrics = DataCleaner.clean_rbi_annual(raw_rbi)
        assert len(clean_rbi) == 3
        assert clean_rbi["gold_mumbai_inr_per_10g"].iloc[0] == 52730.77
        assert clean_rbi["gold_london_usd_per_troy_oz"].iloc[0] == 1804.82

class TestRegimeDetector:
    def test_regime_classification_key_eras(self):
        detector = RegimeDetector()
        test_df = pd.DataFrame({
            "date": ["2008-09-15", "2020-04-10", "2024-10-15", "2005-06-01"]
        })
        tagged = detector.assign_regimes(test_df, date_col="date")

        gfc_row = tagged[tagged["date"] == "2008-09-15"].iloc[0]
        covid_row = tagged[tagged["date"] == "2020-04-10"].iloc[0]
        bull_row = tagged[tagged["date"] == "2024-10-15"].iloc[0]
        base_row = tagged[tagged["date"] == "2005-06-01"].iloc[0]

        assert "2008 Global Financial Crisis" in gfc_row["regime_name"]
        assert gfc_row["is_crisis_regime"] == True

        assert "2020 COVID-19 Pandemic" in covid_row["regime_name"]
        assert covid_row["is_crisis_regime"] == True

        assert "2024-2026 Structural Gold Bull" in bull_row["regime_name"]
        assert bull_row["is_crisis_regime"] == True

        assert "Pre-GFC Stability" in base_row["regime_name"]
        assert base_row["is_crisis_regime"] == False

class TestDataMergerAndParity:
    def test_domestic_parity_calculation(self, sample_daily_data):
        raw_gold, raw_fx = sample_daily_data
        clean_gold, _ = DataCleaner.clean_comex_gold(raw_gold)
        clean_fx, _ = DataCleaner.clean_usdinr_fx(raw_fx)

        merger = DataMerger()
        master_df, meta = merger.build_master_daily_dataset(clean_gold, clean_fx, save_to_disk=False)

        assert "gold_parity_inr_per_10g" in master_df.columns
        assert master_df["is_interpolated"].all() == False

        # Verify parity formula identity for a sample row
        sample = master_df[master_df["both_markets_open"]].iloc[100]
        expected_parity = round((sample["close_usd_per_troy_oz"] / TROY_OUNCE_TO_GRAMS * 10.0) * sample["fx_usdinr"], 2)
        assert abs(sample["gold_parity_inr_per_10g"] - expected_parity) < 0.05

class TestDataValidator:
    def test_date_range_span_validator(self):
        # 22 years dataset
        df_long = pd.DataFrame({"date": ["2000-01-01", "2022-06-01"]})
        res = DataValidator.validate_date_range(df_long, min_years=20)
        assert res["valid"] == True
        assert res["years_span"] >= 20.0

        # Short dataset
        df_short = pd.DataFrame({"date": ["2020-01-01", "2022-01-01"]})
        res_short = DataValidator.validate_date_range(df_short, min_years=20)
        assert res_short["valid"] == False

    def test_duplicates_validator(self):
        df_clean = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"]})
        assert DataValidator.validate_duplicates(df_clean)["valid"] == True

        df_dup = pd.DataFrame({"date": ["2024-01-01", "2024-01-01"]})
        assert DataValidator.validate_duplicates(df_dup)["valid"] == False

    def test_non_interpolation_enforcement(self):
        df_honest = pd.DataFrame({"date": ["2024-01-01"], "is_interpolated": [False]})
        assert DataValidator.validate_missingness(df_honest)["valid"] == True

        df_interpolated = pd.DataFrame({"date": ["2024-01-01"], "is_interpolated": [True]})
        assert DataValidator.validate_missingness(df_interpolated)["valid"] == False

class TestDatabaseIntegration:
    def test_database_table_persistence(self, tmp_path):
        db_file = tmp_path / "test_gold.db"
        engine = get_engine(f"sqlite:///{db_file}")
        init_db(engine)

        test_data = pd.DataFrame({
            "date": ["2024-01-02", "2024-01-03"],
            "close_usd_per_troy_oz": [2060.50, 2045.20],
            "fx_usdinr": [83.25, 83.30],
            "gold_parity_inr_per_10g": [55148.20, 54772.10],
            "regime_name": ["2024-2026 Structural Bull Regime & Record Highs", "2024-2026 Structural Bull Regime & Record Highs"],
            "is_crisis_regime": [True, True],
            "source": ["COMEX_Gold_Futures", "COMEX_Gold_Futures"],
            "is_interpolated": [False, False]
        })

        load_dataframe_to_db(test_data, "gold_daily_prices", engine=engine)
        
        # Query back
        read_back = pd.read_sql("SELECT * FROM gold_daily_prices", engine)
        assert len(read_back) == 2
        assert read_back["date"].tolist() == ["2024-01-02", "2024-01-03"]
