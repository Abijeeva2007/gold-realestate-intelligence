"""
Collector for Historical USD/INR Exchange Rates.
Retrieves historical exchange rates from:
1. Federal Reserve Economic Data (FRED Series: DEXINUS) covering 1973 to present.
2. Market Spot USD/INR (Yahoo Finance: INR=X) covering 2003 to present.
"""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import yfinance as yf

from src.collectors.base_collector import BaseCollector
from src.config import SOURCE_METADATA

class FXCollector(BaseCollector):
    """Collects historical USD/INR exchange rates from multiple official & market sources."""

    def __init__(self):
        super().__init__(name="fx_rates")
        self.fred_meta = SOURCE_METADATA["FRED_USD_INR"]
        self.yahoo_meta = SOURCE_METADATA["USD_INR_SPOT"]

    def collect_fred(self) -> Optional[Path]:
        """
        Fetches historical USD/INR spot rates from FRED (Series DEXINUS).
        Data originates from the Federal Reserve Board H.10 statistical release.
        """
        url = self.fred_meta["url"]
        self.logger.info(f"Downloading FRED DEXINUS exchange rate dataset from {url}...")
        
        response = self.fetch_url(url, retries=1, timeout=8)
        if response and response.status_code == 200:
            csv_text = response.text
            
            # Quick validation check on CSV structure
            lines = [line.strip() for line in csv_text.splitlines() if line.strip()]
            if len(lines) > 10 and "observation_date" in lines[0]:
                meta = {
                    "source": "FRED_DEXINUS",
                    "url": url,
                    "unit": self.fred_meta["unit"],
                    "total_lines": len(lines),
                    "header": lines[0]
                }
                return self.save_raw_file(
                    filename="fred_dexinus_raw.csv",
                    content=csv_text,
                    source_name="FRED_DEXINUS",
                    metadata=meta
                )
        self.logger.warning("Could not download FRED DEXINUS directly; will rely on Yahoo FX feed.")
        return None

    def collect_yahoo_fx(self) -> Optional[Path]:
        """
        Fetches daily USD/INR exchange rate history from Yahoo Finance ticker INR=X.
        """
        ticker_symbol = self.yahoo_meta["ticker"]
        self.logger.info(f"Fetching USD/INR rates from ticker '{ticker_symbol}'...")
        try:
            ticker = yf.Ticker(ticker_symbol)
            df = ticker.history(period="max", auto_adjust=False)
            if df.empty:
                self.logger.error(f"No FX data returned for ticker {ticker_symbol}")
                return None
                
            df = df.reset_index()
            raw_csv = df.to_csv(index=False)
            meta = {
                "ticker": ticker_symbol,
                "unit": self.yahoo_meta["unit"],
                "total_rows": len(df),
                "earliest_date": str(df["Date"].min()),
                "latest_date": str(df["Date"].max())
            }
            return self.save_raw_file(
                filename="yahoo_usdinr_raw.csv",
                content=raw_csv,
                source_name="Yahoo_USDINR_Spot",
                metadata=meta
            )
        except Exception as exc:
            self.logger.error(f"Failed to fetch Yahoo USD/INR data: {exc}", exc_info=True)
            return None

    def collect_all(self) -> Dict[str, Optional[Path]]:
        """Executes collection for both FX sources."""
        return {
            "fred": self.collect_fred(),
            "yahoo": self.collect_yahoo_fx()
        }
