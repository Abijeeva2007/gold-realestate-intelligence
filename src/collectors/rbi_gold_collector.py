"""
Collector for Official Indian Gold Prices from the Reserve Bank of India (RBI).
Scrapes and parses official tables from the Handbook of Statistics on the Indian Economy:
- Table 35: Annual Average Price of Gold and Silver in Domestic and Foreign Markets (1985-2026).
- Table 164: Monthly Average Price of Gold and Silver in Domestic and Foreign Markets (2022-2026).

Prices are reported in INR per 10 grams (Mumbai) and USD per troy ounce (London/LBMA).
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import re
import pandas as pd
from bs4 import BeautifulSoup

from src.collectors.base_collector import BaseCollector
from src.config import SOURCE_METADATA

class RbiGoldCollector(BaseCollector):
    """Collects domestic Indian gold prices directly from official RBI publications."""

    def __init__(self):
        super().__init__(name="rbi_gold")
        self.meta_annual = SOURCE_METADATA["RBI_GOLD_ANNUAL"]
        self.meta_monthly = SOURCE_METADATA["RBI_GOLD_MONTHLY"]

    def collect_annual_table_35(self) -> Optional[Path]:
        """
        Fetches and stores RBI Table 35 (Annual Spot Gold Prices 1985-2026).
        """
        url = self.meta_annual["url"]
        self.logger.info(f"Fetching RBI Table 35 from {url}...")
        
        response = self.fetch_url(url, timeout=30)
        if not response or response.status_code != 200:
            self.logger.error("Failed to fetch RBI Table 35 HTML.")
            return None

        html_content = response.text
        # Save raw HTML first to preserve raw source data
        raw_html_path = self.save_raw_file(
            filename="rbi_table_35_raw.html",
            content=html_content,
            source_name="RBI_Table_35_Annual",
            metadata={"url": url, "table_title": self.meta_annual["table_name"]}
        )

        # Parse table structure
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table")
        if not table:
            self.logger.error("Table tag not found in RBI Table 35 HTML.")
            return None

        rows = table.find_all("tr")
        records = []
        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
            if len(cols) >= 4 and any(cols[0].startswith(yr) for yr in ["19", "20"]):
                try:
                    records.append({
                        "financial_year": cols[0],
                        "gold_mumbai_inr_per_10g": float(cols[1].replace(",", "")),
                        "gold_london_usd_per_troy_oz": float(cols[2].replace(",", "")),
                        "spread_inr_per_10g": float(cols[3].replace(",", "")) if len(cols) > 3 and cols[3] else None
                    })
                except (ValueError, IndexError) as parse_err:
                    self.logger.warning(f"Skipping malformed row {cols[:4]}: {parse_err}")

        if not records:
            self.logger.error("No valid data records parsed from RBI Table 35.")
            return None

        df_annual = pd.DataFrame(records)
        raw_csv_path = self.save_raw_file(
            filename="rbi_gold_annual_raw.csv",
            content=df_annual.to_csv(index=False),
            source_name="RBI_Table_35_Annual_CSV",
            metadata={
                "record_count": len(df_annual),
                "earliest_fy": df_annual["financial_year"].min(),
                "latest_fy": df_annual["financial_year"].max(),
                "unit_domestic": "INR per 10 grams",
                "unit_foreign": "USD per troy ounce"
            }
        )
        self.logger.info(f"Successfully extracted {len(df_annual)} annual records from RBI Table 35.")
        return raw_csv_path

    def collect_monthly_table_164(self) -> Optional[Path]:
        """
        Fetches and stores RBI Table 164 (Monthly Spot Gold Prices).
        """
        url = self.meta_monthly["url"]
        self.logger.info(f"Fetching RBI Table 164 from {url}...")

        response = self.fetch_url(url, timeout=30)
        if not response or response.status_code != 200:
            self.logger.error("Failed to fetch RBI Table 164 HTML.")
            return None

        html_content = response.text
        self.save_raw_file(
            filename="rbi_table_164_raw.html",
            content=html_content,
            source_name="RBI_Table_164_Monthly",
            metadata={"url": url, "table_title": self.meta_monthly["table_name"]}
        )

        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table")
        if not table:
            self.logger.error("Table tag not found in RBI Table 164 HTML.")
            return None

        rows = table.find_all("tr")
        records = []
        current_fy = None
        months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
            if not cols:
                continue
            text = cols[0]
            m = re.match(r"(20\d\d-\d\d)", text)
            if m:
                current_fy = m.group(1)
                for mon in months:
                    if mon in text:
                        self._append_monthly_record(records, current_fy, mon, cols)
                        break
            elif any(text.startswith(mon) for mon in months):
                mon = [m for m in months if text.startswith(m)][0]
                self._append_monthly_record(records, current_fy, mon, cols)

        if not records:
            self.logger.error("No valid records parsed from RBI Table 164.")
            return None

        df_monthly = pd.DataFrame(records)
        raw_csv_path = self.save_raw_file(
            filename="rbi_gold_monthly_raw.csv",
            content=df_monthly.to_csv(index=False),
            source_name="RBI_Table_164_Monthly_CSV",
            metadata={
                "record_count": len(df_monthly),
                "earliest_period": f"{df_monthly['financial_year'].min()} {df_monthly['month'].iloc[0]}",
                "latest_period": f"{df_monthly['financial_year'].max()} {df_monthly['month'].iloc[-1]}",
                "unit_domestic": "INR per 10 grams",
                "unit_foreign": "USD per troy ounce"
            }
        )
        self.logger.info(f"Successfully extracted {len(df_monthly)} monthly records from RBI Table 164.")
        return raw_csv_path

    def _append_monthly_record(
        self,
        records: List[Dict[str, Any]],
        fy: Optional[str],
        month: str,
        cols: List[str]
    ):
        """Helper to parse and append monthly gold rows."""
        if len(cols) >= 4 and cols[1].replace(".", "", 1).isdigit():
            try:
                records.append({
                    "financial_year": fy,
                    "month": month,
                    "gold_mumbai_inr_per_10g": float(cols[1].replace(",", "")),
                    "gold_london_usd_per_troy_oz": float(cols[2].replace(",", "")),
                    "spread_inr_per_10g": float(cols[3].replace(",", "")) if cols[3] else None
                })
            except (ValueError, IndexError):
                pass

    def collect_all(self) -> Dict[str, Optional[Path]]:
        """Collects both annual and monthly tables from RBI."""
        return {
            "annual": self.collect_annual_table_35(),
            "monthly": self.collect_monthly_table_164()
        }
