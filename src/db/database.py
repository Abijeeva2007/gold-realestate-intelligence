"""
Database Integration Module using SQLAlchemy.
Defines schemas for historical gold prices, foreign exchange, and domestic benchmarks,
ensuring seamless compatibility with SQLite (local development) and PostgreSQL (production).
"""

from pathlib import Path
from typing import Optional
import pandas as pd
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    Boolean,
    Date,
    Index
)
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import DATABASE_URL, setup_logging

logger = setup_logging()
Base = declarative_base()

class GoldDailyPrice(Base):
    """Daily Global Gold Prices and Domestic Indian Parity Table."""
    __tablename__ = "gold_daily_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), nullable=False, unique=True, index=True)
    close_usd_per_troy_oz = Column(Float, nullable=True)
    open_usd_per_troy_oz = Column(Float, nullable=True)
    high_usd_per_troy_oz = Column(Float, nullable=True)
    low_usd_per_troy_oz = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    fx_usdinr = Column(Float, nullable=True)
    gold_parity_inr_per_10g = Column(Float, nullable=True)
    regime_name = Column(String(100), nullable=True)
    is_crisis_regime = Column(Boolean, default=False)
    source = Column(String(100), default="COMEX_Gold_Futures")
    is_interpolated = Column(Boolean, default=False)


class RbiAnnualGold(Base):
    """RBI Official Annual Benchmark Gold Prices Table."""
    __tablename__ = "rbi_annual_gold_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    financial_year = Column(String(20), nullable=False, unique=True, index=True)
    fy_start_year = Column(Integer, nullable=True)
    gold_mumbai_inr_per_10g = Column(Float, nullable=False)
    gold_london_usd_per_troy_oz = Column(Float, nullable=False)
    spread_inr_per_10g = Column(Float, nullable=True)
    source = Column(String(100), default="RBI_Table_35_Handbook")
    is_interpolated = Column(Boolean, default=False)


class RbiMonthlyGold(Base):
    """RBI Official Monthly Benchmark Gold Prices Table."""
    __tablename__ = "rbi_monthly_gold_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year_month = Column(String(7), nullable=False, unique=True, index=True)
    financial_year = Column(String(20), nullable=False)
    month = Column(String(10), nullable=False)
    gold_mumbai_inr_per_10g = Column(Float, nullable=False)
    gold_london_usd_per_troy_oz = Column(Float, nullable=False)
    spread_inr_per_10g = Column(Float, nullable=True)
    source = Column(String(100), default="RBI_Table_164_Handbook")
    is_interpolated = Column(Boolean, default=False)


def get_engine(url: Optional[str] = None):
    """Returns SQLAlchemy engine for given or configured URL."""
    db_url = url or DATABASE_URL
    return create_engine(db_url, echo=False)


def init_db(engine=None):
    """Initializes tables in database."""
    eng = engine or get_engine()
    Base.metadata.create_all(eng)
    logger.info(f"Database schema initialized successfully on {eng.url}")
    return eng


def load_dataframe_to_db(df: pd.DataFrame, table_name: str, engine=None, if_exists: str = "replace"):
    """Loads a pandas dataframe into database using SQLAlchemy."""
    eng = engine or get_engine()
    df.to_sql(table_name, eng, if_exists=if_exists, index=False)
    logger.info(f"Loaded {len(df)} records into table '{table_name}'.")
