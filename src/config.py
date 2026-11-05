"""
Configuration module for the Gold Intelligence and Prediction Platform.
Centralizes paths, endpoints, physical constants, market regimes, and logging settings.
"""

from pathlib import Path
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Project Root Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data Directories
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
RAW_DATA_DIR = BASE_DIR / os.getenv("RAW_DATA_DIR", "data/raw")
PROCESSED_DATA_DIR = BASE_DIR / os.getenv("PROCESSED_DATA_DIR", "data/processed")
REPORTS_DIR = BASE_DIR / os.getenv("REPORTS_DIR", "data/reports")
MODELS_DIR = BASE_DIR / os.getenv("MODELS_DIR", "models/gold")

# Ensure required directories exist
for path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, MODELS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Database URL (SQLite default with PostgreSQL support)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/gold_intelligence.db")

# Physical & Financial Constants
TROY_OUNCE_TO_GRAMS = 31.1034768
TROY_OUNCE_TO_10GRAMS = TROY_OUNCE_TO_GRAMS / 10.0  # 3.11034768

# Source Endpoints & Tickers
SOURCE_METADATA = {
    "COMEX_GOLD": {
        "ticker": "GC=F",
        "description": "CME COMEX continuous Gold Futures contract (100 troy oz)",
        "unit": "USD per troy ounce",
        "frequency": "Daily",
        "provider": "Yahoo Finance (Market Feed)",
        "start_year": 2000,
        "license_notes": "Publicly accessible market data via Yahoo Finance API."
    },
    "USD_INR_SPOT": {
        "ticker": "INR=X",
        "description": "USD to INR spot exchange rate",
        "unit": "INR per 1 USD",
        "frequency": "Daily",
        "provider": "Yahoo Finance / Bank of England / Forex aggregators",
        "start_year": 2003,
        "license_notes": "Publicly accessible FX feed."
    },
    "FRED_USD_INR": {
        "series_id": "DEXINUS",
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXINUS",
        "description": "Indian Rupees to U.S. Dollar Spot Exchange Rate",
        "unit": "INR per 1 USD",
        "frequency": "Daily (business days)",
        "provider": "Board of Governors of the Federal Reserve System (H.10 Release)",
        "start_year": 1973,
        "license_notes": "Public domain official U.S. Federal Reserve statistical release."
    },
    "RBI_GOLD_ANNUAL": {
        "url": "https://rbi.org.in/Scripts/PublicationsView.aspx?id=23860",
        "table_name": "Table 35 : Average Price of Gold and Silver in Domestic and Foreign Markets",
        "description": "Official annual average spot gold prices in Mumbai and London",
        "unit_domestic": "INR per 10 grams",
        "unit_foreign": "USD per troy ounce",
        "frequency": "Annual (Financial Year)",
        "provider": "Reserve Bank of India (Handbook of Statistics on the Indian Economy)",
        "start_year": 1985,
        "license_notes": "Official open publication of the Reserve Bank of India for public research."
    },
    "RBI_GOLD_MONTHLY": {
        "url": "https://rbi.org.in/Scripts/PublicationsView.aspx?id=23989",
        "table_name": "Table 164 : Monthly Average Price of Gold and Silver in Domestic and Foreign Markets",
        "description": "Official monthly average spot gold prices in Mumbai and London with domestic-international spread",
        "unit_domestic": "INR per 10 grams",
        "unit_foreign": "USD per troy ounce",
        "frequency": "Monthly",
        "provider": "Reserve Bank of India (Handbook of Statistics on the Indian Economy)",
        "start_year": 2022,
        "license_notes": "Official open publication of the Reserve Bank of India for public research."
    },
    "WORLD_BANK_PINK": {
        "url": "https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx",
        "description": "World Bank Commodity Markets Pink Sheet historical monthly gold prices",
        "unit": "USD per troy ounce",
        "frequency": "Monthly",
        "provider": "World Bank Development Prospects Group",
        "start_year": 1960,
        "license_notes": "Open Data from the World Bank (CC-BY 4.0)."
    },
    "WGC_GOLDHUB": {
        "portal_url": "https://www.gold.org/goldhub/data/gold-prices",
        "description": "World Gold Council historical gold price averages",
        "unit": "Multiple currencies (USD, INR, EUR)",
        "frequency": "Daily / Monthly / Annual",
        "provider": "World Gold Council / ICE Benchmark Administration",
        "license_notes": "Requires authenticated account login; direct programmatic bulk access protected by Cloudflare/WAF."
    },
    "LBMA_DIRECT": {
        "description": "London Bullion Market Association (LBMA) Gold Fixings (AM & PM)",
        "unit": "USD per troy ounce",
        "provider": "ICE Benchmark Administration (IBA)",
        "license_notes": "Direct bulk automated distribution requires commercial license or Nasdaq Data Link subscription key."
    }
}

# Market Regimes Definition
MARKET_REGIMES = [
    {
        "name": "Pre-GFC Stability",
        "start_date": "2000-01-01",
        "end_date": "2007-11-30",
        "description": "Low inflation baseline and early commodity super-cycle."
    },
    {
        "name": "2008 Global Financial Crisis (GFC)",
        "start_date": "2007-12-01",
        "end_date": "2009-06-30",
        "description": "US subprime collapse, Lehman Brothers liquidation, liquidity freeze, and flight to safety."
    },
    {
        "name": "Post-GFC Quantitative Easing & European Sovereign Debt",
        "start_date": "2009-07-01",
        "end_date": "2012-12-31",
        "description": "Unprecedented global central bank QE and European sovereign debt crisis, driving gold to then-record highs ($1,920/oz in 2011)."
    },
    {
        "name": "Fed Taper & Commodity Consolidation",
        "start_date": "2013-01-01",
        "end_date": "2018-12-31",
        "description": "Fed taper tantrum, strong US dollar, and cyclical multi-year gold consolidation."
    },
    {
        "name": "Pre-Pandemic Policy Pivot",
        "start_date": "2019-01-01",
        "end_date": "2019-12-31",
        "description": "US-China trade war and Federal Reserve rate cuts restarting gold momentum."
    },
    {
        "name": "2020 COVID-19 Pandemic Shock",
        "start_date": "2020-01-01",
        "end_date": "2021-12-31",
        "description": "Worldwide pandemic lockdowns, global monetary expansion, negative real yields, gold breaches $2,000/oz for the first time."
    },
    {
        "name": "Global Monetary Tightening Transition",
        "start_date": "2022-01-01",
        "end_date": "2023-12-31",
        "description": "Aggressive central bank rate hikes battling inflation, offset by geopolitical conflict (Ukraine, Middle East)."
    },
    {
        "name": "2024-2026 Structural Gold Bull Regime & Record Highs",
        "start_date": "2024-01-01",
        "end_date": "2026-12-31",
        "description": "Massive central bank reserve accumulation, de-dollarization pressures, geopolitical realignment, gold continuously breaches all-time highs above $2,700-$3,500/oz."
    }
]

# Logging Setup Function
def setup_logging(log_level: str = None) -> logging.Logger:
    """Configures and returns a standardized logger for the pipeline."""
    level = log_level or os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger("gold_pipeline")
