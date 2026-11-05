"""
Collector for COMEX Gold Futures (GC=F) and Global Gold Benchmarks.
Collects daily OHLCV gold prices in USD per troy ounce spanning 20+ years (2000-present).
"""

from pathlib import Path
from typing import Optional
import pandas as pd
import yfinance as yf

from src.collectors.base_collector import BaseCollector
from src.config import SOURCE_METADATA

class ComexGoldCollector(BaseCollector):
    """Collects historical global gold futures and spot ETF data from market feeds."""

    def __init__(self):
        super().__init__(name="comex_gold")
        self.meta = SOURCE_METADATA["COMEX_GOLD"]

    def collect(self, start_date: str = "2000-01-01") -> Optional[Path]:
        """
        Fetches maximum daily historical data for GC=F (COMEX Gold Futures).
        
        Args:
            start_date: Start date for historical extraction.
            
        Returns:
            Path to raw CSV file if successful, else None.
        """
        ticker_symbol = self.meta["ticker"]
        self.logger.info(f"Querying ticker '{ticker_symbol}' for continuous gold futures...")

        try:
            ticker = yf.Ticker(ticker_symbol)
            # Query max period to ensure 20+ years of coverage
            df_raw = ticker.history(period="max", auto_adjust=False)

            if df_raw.empty:
                self.logger.error(f"No data returned for ticker {ticker_symbol}")
                return None

            # Reset index to expose Date
            df_raw = df_raw.reset_index()

            # Convert to standard CSV representation
            raw_csv = df_raw.to_csv(index=False)
            
            metadata = {
                "ticker": ticker_symbol,
                "unit": self.meta["unit"],
                "provider": self.meta["provider"],
                "total_rows": len(df_raw),
                "earliest_date": str(df_raw["Date"].min()),
                "latest_date": str(df_raw["Date"].max()),
                "columns": list(df_raw.columns)
            }

            raw_path = self.save_raw_file(
                filename="comex_gold_raw.csv",
                content=raw_csv,
                source_name="COMEX_Gold_Futures",
                metadata=metadata
            )
            self.logger.info(
                f"COMEX Gold raw data collected: {len(df_raw)} records "
                f"from {metadata['earliest_date']} to {metadata['latest_date']}"
            )
            return raw_path

        except Exception as exc:
            self.logger.error(f"Failed to collect COMEX gold futures: {exc}", exc_info=True)
            return None
