"""
Configuration for Tamil Nadu Real Estate Intelligence & Prediction Engine.
Isolates database paths, unit constants, source metadata, and regional bounds.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Independent real estate data paths
REAL_ESTATE_DATA_DIR = BASE_DIR / "data"
REAL_ESTATE_RAW_DIR = BASE_DIR / "data/raw/real_estate"
REAL_ESTATE_PROCESSED_DIR = BASE_DIR / "data/processed/real_estate"
REAL_ESTATE_MODELS_DIR = BASE_DIR / "models/real_estate"

for p in [REAL_ESTATE_RAW_DIR, REAL_ESTATE_PROCESSED_DIR, REAL_ESTATE_MODELS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Dedicated SQLite database URL
REAL_ESTATE_DB_PATH = REAL_ESTATE_DATA_DIR / "real_estate.db"
REAL_ESTATE_DATABASE_URL = os.getenv("REAL_ESTATE_DATABASE_URL", f"sqlite:///{REAL_ESTATE_DB_PATH}")

# Tamil Nadu Land Measurement Conversion Constants
SQFT_PER_SQM = 10.7639104
SQFT_PER_CENT = 435.6
SQFT_PER_GROUND = 2400.0
SQFT_PER_ACRE = 43560.0
SQFT_PER_HECTARE = 107639.104
SQFT_PER_KUZHI = 144.0  # Traditional Tamil agricultural measure (100 Kuzhi = 1 Maa = 0.33 acre)

CENTS_PER_GROUND = SQFT_PER_GROUND / SQFT_PER_CENT  # 5.5096418
GROUNDS_PER_ACRE = SQFT_PER_ACRE / SQFT_PER_GROUND  # 18.15
CENTS_PER_ACRE = 100.0

# Supported Price Types
PRICE_TYPES = [
    "TRANSACTION",      # Registered actual sale price
    "GUIDELINE",        # TNREGINET statutory stamp duty base rate
    "ASKING",           # Current builder / portal listing price
    "RENTAL",           # Monthly lease value
    "BANK_ASSESSMENT",  # Formal mortgage valuation report
    "MODEL_ESTIMATE"    # Algorithmic fair market valuation
]

# Supported Property Categories & Types
PROPERTY_CATEGORIES = {
    "RESIDENTIAL_APARTMENT": {"name": "Residential Apartment", "category": "RESIDENTIAL", "unit": "SQFT"},
    "INDEPENDENT_HOUSE": {"name": "Independent House / Villa", "category": "RESIDENTIAL", "unit": "SQFT"},
    "VILLA": {"name": "Gated Community Villa", "category": "RESIDENTIAL", "unit": "SQFT"},
    "RESIDENTIAL_PLOT": {"name": "Residential Layout Plot", "category": "LAND", "unit": "SQFT"},
    "AGRICULTURAL_LAND": {"name": "Agricultural Land", "category": "AGRICULTURAL", "unit": "ACRE"},
    "COMMERCIAL_PROPERTY": {"name": "Commercial Office / Retail Space", "category": "COMMERCIAL", "unit": "SQFT"}
}

# Data Sources Metadata & Provenance
REAL_ESTATE_SOURCES = {
    "TNREGINET": {
        "name": "Tamil Nadu Registration Department (TNREGINET)",
        "provider": "Inspector General of Registration, Government of Tamil Nadu",
        "url": "https://tnreginet.gov.in",
        "access_method": "Official Public Portal / Offline Guideline Value Register Extracts",
        "authentication_required": False,
        "update_frequency": "Periodic statutory notifications",
        "description": "Statutory minimum guideline values for streets and survey numbers across all 38 districts of Tamil Nadu. Used exclusively for stamp duty and registration tax assessment.",
        "license_notes": "Official public administrative records published by the Government of Tamil Nadu."
    },
    "NHB_RESIDEX": {
        "name": "National Housing Bank RESIDEX Housing Price Index",
        "provider": "National Housing Bank (NHB), Wholly Owned by Reserve Bank of India",
        "url": "https://residex.nhb.org.in",
        "access_method": "Official Quarterly Statistical Releases & Portal Data",
        "authentication_required": False,
        "update_frequency": "Quarterly",
        "description": "Official housing price indices for major Indian metropolitan areas including Chennai and Coimbatore, tracking both registered property prices and valuation indices.",
        "license_notes": "Public statistical research data published by the National Housing Bank."
    },
    "RBI_DBIE": {
        "name": "RBI Database on Indian Economy (DBIE)",
        "provider": "Reserve Bank of India (RBI)",
        "url": "https://dbie.rbi.org.in",
        "access_method": "Official Statistical Data Releases",
        "authentication_required": False,
        "update_frequency": "Monthly / Bi-monthly",
        "description": "Macroeconomic benchmarks: Policy Repo Rate, Weighted Average Lending Rate (WALR), Bank Credit to Housing, and Consumer Price Index (CPI).",
        "license_notes": "Official public statistical publications of the central bank."
    },
    "BIS_REALESTATE": {
        "name": "Bank for International Settlements Residential Property Price Statistics",
        "provider": "Bank for International Settlements (BIS)",
        "url": "https://www.bis.org/statistics/pp.htm",
        "access_method": "Official Public Data API / CSV Portal",
        "authentication_required": False,
        "update_frequency": "Quarterly",
        "description": "Long-term real and nominal residential property price series for India and global cross-market comparisons.",
        "license_notes": "Open statistical data provided by the Bank for International Settlements."
    },
    "TNRERA": {
        "name": "Tamil Nadu Real Estate Regulatory Authority (TNRERA)",
        "provider": "Government of Tamil Nadu",
        "url": "https://www.rera.tn.gov.in",
        "access_method": "Public Regulatory Register Portal Extracts",
        "authentication_required": False,
        "update_frequency": "Continuous / Monthly",
        "description": "Statutory registry of approved real estate residential projects, layout approvals, and registered promoters across Tamil Nadu.",
        "license_notes": "Public regulatory registry mandated under the Real Estate (Regulation and Development) Act, 2016."
    }
}
