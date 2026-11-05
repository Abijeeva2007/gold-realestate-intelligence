"""
Main Pipeline Orchestrator Module.
Executes the reproducible end-to-end historical data engineering workflow:
1. Multi-source collection (COMEX Gold, USD/INR FX, RBI Domestic Spot, World Bank).
2. Data cleaning, duplicate removal, date ISO-8601 standardization, and non-interpolation enforcement.
3. Macroeconomic regime classification (2008 GFC, 2020 COVID, 2024-2026 Structural Bull).
4. Master cross-market dataset alignment & domestic parity calculation.
5. Strict validation suite execution & markdown quality report generation.
6. SQLAlchemy database loading (SQLite / PostgreSQL ready).
"""

from pathlib import Path
from typing import Dict, Any
import pandas as pd

from src.config import PROCESSED_DATA_DIR, setup_logging
from src.collectors import (
    ComexGoldCollector,
    FXCollector,
    RbiGoldCollector,
    WorldBankCollector
)
from src.processors import (
    DataCleaner,
    RegimeDetector,
    DataMerger
)
from src.validators import (
    DataValidator,
    QualityReporter
)
from src.db.database import (
    init_db,
    load_dataframe_to_db
)

logger = setup_logging()

class GoldDataPipeline:
    """Orchestrates the complete data engineering pipeline."""

    def __init__(self):
        self.processed_dir = Path(PROCESSED_DATA_DIR)
        self.cleaner = DataCleaner()
        self.regime_detector = RegimeDetector()
        self.merger = DataMerger()
        self.validator = DataValidator()
        self.reporter = QualityReporter()

    def run(self) -> Dict[str, Any]:
        """Executes end-to-end pipeline."""
        logger.info("================================================================")
        logger.info("STARTING GOLD HISTORICAL DATA ENGINEERING PIPELINE")
        logger.info("================================================================")

        # -------------------------------------------------------------
        # 1. Collection Phase
        # -------------------------------------------------------------
        logger.info("PHASE 1: Data Collection from Official & Market Feeds...")
        
        # 1a. COMEX Gold
        comex_coll = ComexGoldCollector()
        comex_raw_path = comex_coll.collect()
        
        # 1b. FX USD/INR
        fx_coll = FXCollector()
        fx_raw_paths = fx_coll.collect_all()
        
        # 1c. RBI Domestic Indian Gold
        rbi_coll = RbiGoldCollector()
        rbi_raw_paths = rbi_coll.collect_all()

        # 1d. World Bank Pink Sheet (Monthly)
        wb_coll = WorldBankCollector()
        wb_raw_path = wb_coll.collect()

        collection_meta = {
            "comex_raw": str(comex_raw_path),
            "fx_fred_raw": str(fx_raw_paths["fred"]),
            "fx_yahoo_raw": str(fx_raw_paths["yahoo"]),
            "rbi_annual_raw": str(rbi_raw_paths["annual"]),
            "rbi_monthly_raw": str(rbi_raw_paths["monthly"]),
            "world_bank_raw": str(wb_raw_path)
        }

        # -------------------------------------------------------------
        # 2. Cleaning and Standardization Phase
        # -------------------------------------------------------------
        logger.info("PHASE 2: Cleaning, Date ISO Standardization & Deduplication...")
        
        # 2a. COMEX Gold
        if not comex_raw_path or not comex_raw_path.exists():
            raise RuntimeError("COMEX Gold raw data collection failed.")
        raw_comex_df = pd.read_csv(comex_raw_path)
        clean_gold_df, gold_meta = self.cleaner.clean_comex_gold(raw_comex_df)
        clean_gold_path = self.processed_dir / "gold_global_daily_usd.csv"
        clean_gold_df.to_csv(clean_gold_path, index=False)

        # 2b. FX USD/INR (Prefer FRED if available, otherwise Yahoo)
        if fx_raw_paths["fred"] and fx_raw_paths["fred"].exists():
            raw_fx_df = pd.read_csv(fx_raw_paths["fred"])
            clean_fx_df, fx_meta = self.cleaner.clean_usdinr_fx(raw_fx_df, source_type="fred")
        elif fx_raw_paths["yahoo"] and fx_raw_paths["yahoo"].exists():
            raw_fx_df = pd.read_csv(fx_raw_paths["yahoo"])
            clean_fx_df, fx_meta = self.cleaner.clean_usdinr_fx(raw_fx_df, source_type="yahoo")
        else:
            raise RuntimeError("USD/INR raw data collection failed.")
        clean_fx_path = self.processed_dir / "usdinr_daily.csv"
        clean_fx_df.to_csv(clean_fx_path, index=False)

        # 2c. RBI Annual
        clean_rbi_annual_df = pd.DataFrame()
        if rbi_raw_paths["annual"] and rbi_raw_paths["annual"].exists():
            raw_rbi_a = pd.read_csv(rbi_raw_paths["annual"])
            clean_rbi_annual_df, _ = self.cleaner.clean_rbi_annual(raw_rbi_a)
            clean_rbi_annual_df.to_csv(self.processed_dir / "gold_india_rbi_annual.csv", index=False)

        # 2d. RBI Monthly
        clean_rbi_monthly_df = pd.DataFrame()
        if rbi_raw_paths["monthly"] and rbi_raw_paths["monthly"].exists():
            raw_rbi_m = pd.read_csv(rbi_raw_paths["monthly"])
            clean_rbi_monthly_df, _ = self.cleaner.clean_rbi_monthly(raw_rbi_m)
            clean_rbi_monthly_df.to_csv(self.processed_dir / "gold_india_rbi_monthly.csv", index=False)

        # 2e. World Bank Monthly
        if wb_raw_path and wb_raw_path.exists():
            raw_wb = pd.read_csv(wb_raw_path)
            clean_wb_df, _ = self.cleaner.clean_world_bank_monthly(raw_wb)
            clean_wb_df.to_csv(self.processed_dir / "world_bank_gold_monthly.csv", index=False)

        # -------------------------------------------------------------
        # 3. Merging & Macro Regime Classification Phase
        # -------------------------------------------------------------
        logger.info("PHASE 3: Cross-Market Alignment & Macro Regime Tagging...")
        master_df, merge_meta = self.merger.build_master_daily_dataset(
            df_gold_daily=clean_gold_df,
            df_fx_daily=clean_fx_df,
            df_rbi_monthly=clean_rbi_monthly_df
        )

        regime_stats_df = self.regime_detector.compute_regime_statistics(
            master_df[master_df["gold_market_open"]],
            price_col="close_usd_per_troy_oz"
        )
        regime_stats_path = self.processed_dir / "regime_performance_metrics.csv"
        regime_stats_df.to_csv(regime_stats_path, index=False)

        # -------------------------------------------------------------
        # 4. Rigorous Validation and Reporting Phase
        # -------------------------------------------------------------
        logger.info("PHASE 4: Executing Validation Suite & Generating Reports...")
        val_results = self.validator.run_full_validation_suite(
            master_df[master_df["gold_market_open"]],
            key_col="date"
        )
        logger.info(f"Validation Status: {val_results['overall_status']}")

        # Generate Reports
        quality_report_path = self.reporter.generate_data_quality_report(
            validation_results=val_results,
            collection_meta=collection_meta
        )
        regime_report_path = self.reporter.generate_regime_report(regime_stats_df)

        # -------------------------------------------------------------
        # 5. Database Integration Phase (SQLAlchemy)
        # -------------------------------------------------------------
        logger.info("PHASE 5: Loading Processed Datasets into Database...")
        try:
            engine = init_db()
            load_dataframe_to_db(master_df, "gold_daily_prices", engine=engine)
            if not clean_rbi_annual_df.empty:
                load_dataframe_to_db(clean_rbi_annual_df, "rbi_annual_gold_prices", engine=engine)
            if not clean_rbi_monthly_df.empty:
                load_dataframe_to_db(clean_rbi_monthly_df, "rbi_monthly_gold_prices", engine=engine)
            logger.info("Database loading completed successfully.")
        except Exception as db_err:
            logger.warning(f"Database loading encountered non-fatal error: {db_err}")

        logger.info("================================================================")
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"Master CSV: {self.processed_dir / 'gold_master_daily_unified.csv'}")
        logger.info(f"Quality Report: {quality_report_path}")
        logger.info(f"Regime Report: {regime_report_path}")
        logger.info("================================================================")

        return {
            "status": "SUCCESS",
            "validation_results": val_results,
            "master_rows": len(master_df),
            "date_range": (master_df["date"].min(), master_df["date"].max()),
            "quality_report": str(quality_report_path),
            "regime_report": str(regime_report_path)
        }

if __name__ == "__main__":
    pipeline = GoldDataPipeline()
    pipeline.run()
