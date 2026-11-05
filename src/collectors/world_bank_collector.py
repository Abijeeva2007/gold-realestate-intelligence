"""
Collector for World Bank Historical Commodity Prices (Pink Sheet).
Downloads official World Bank monthly gold price series covering 1960 to present (60+ years).
Standardized in USD per troy ounce.
"""

from pathlib import Path
from typing import Optional
import io
import pandas as pd

from src.collectors.base_collector import BaseCollector
from src.config import SOURCE_METADATA

class WorldBankCollector(BaseCollector):
    """Downloads and extracts historical monthly benchmark gold prices from the World Bank."""

    def __init__(self):
        super().__init__(name="world_bank")
        self.meta = SOURCE_METADATA["WORLD_BANK_PINK"]

    def collect(self) -> Optional[Path]:
        """
        Downloads the World Bank CMO Historical Data Excel workbook and extracts the Gold series.
        """
        url = self.meta["url"]
        self.logger.info(f"Downloading World Bank historical commodity workbook from {url}...")
        
        response = self.fetch_url(url, timeout=30)
        if not response or response.status_code != 200:
            self.logger.error("Failed to download World Bank workbook.")
            return None

        # Save raw binary excel file
        raw_xlsx_path = self.save_raw_file(
            filename="world_bank_cmo_monthly_raw.xlsx",
            content=response.content,
            source_name="World_Bank_CMO_PinkSheet",
            metadata={"url": url, "unit": self.meta["unit"]}
        )

        try:
            excel_file = pd.ExcelFile(io.BytesIO(response.content))
            if "Monthly Prices" not in excel_file.sheet_names:
                self.logger.error("Sheet 'Monthly Prices' not found in World Bank workbook.")
                return None

            df_raw = pd.read_excel(excel_file, sheet_name="Monthly Prices", header=4)
            date_col = df_raw.columns[0]
            
            # Locate gold column
            gold_cols = [c for c in df_raw.columns if "gold" in str(c).lower()]
            if not gold_cols:
                self.logger.error("Gold column not found in World Bank sheet.")
                return None

            gold_col = gold_cols[0]
            df_gold = df_raw[[date_col, gold_col]].dropna()
            df_gold.columns = ["period", "gold_usd_per_troy_oz"]

            # Filter valid periods (e.g., 1960M01)
            df_gold = df_gold[df_gold["period"].astype(str).str.match(r"^\d{4}M\d{2}$")]

            raw_csv_path = self.save_raw_file(
                filename="world_bank_gold_monthly_raw.csv",
                content=df_gold.to_csv(index=False),
                source_name="World_Bank_Gold_Monthly_CSV",
                metadata={
                    "total_records": len(df_gold),
                    "earliest_period": df_gold["period"].iloc[0],
                    "latest_period": df_gold["period"].iloc[-1],
                    "unit": "USD per troy ounce"
                }
            )
            self.logger.info(
                f"World Bank gold monthly series extracted: {len(df_gold)} records "
                f"from {df_gold['period'].iloc[0]} to {df_gold['period'].iloc[-1]}"
            )
            return raw_csv_path

        except Exception as exc:
            self.logger.error(f"Error extracting World Bank gold series: {exc}", exc_info=True)
            return None
