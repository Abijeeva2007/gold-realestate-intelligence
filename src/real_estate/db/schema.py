"""
SQLAlchemy ORM models defining the 13 normalized tables for the
Tamil Nadu Real Estate Intelligence & Prediction Engine.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime,
    ForeignKey, Text, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from src.real_estate.db.database import Base


class District(Base):
    """Tamil Nadu Administrative District (38 districts)."""
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(32), unique=True, nullable=False, index=True)  # e.g., "CHN", "CBE", "MDU"
    name = Column(String(128), unique=True, nullable=False, index=True) # e.g., "Chennai", "Coimbatore"
    headquarters = Column(String(128), nullable=False)
    region = Column(String(64), nullable=False)                         # Northern, Western, Southern, Central, Delta
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    area_sqkm = Column(Float, nullable=True)
    population_census = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    taluks = relationship("Taluk", back_populates="district", cascade="all, delete-orphan")
    localities = relationship("Locality", back_populates="district")
    indices = relationship("MarketIndex", back_populates="district")
    infrastructure = relationship("InfrastructureProject", back_populates="district")


class Taluk(Base):
    """Sub-district revenue division (Taluk)."""
    __tablename__ = "taluks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, ForeignKey("districts.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False, index=True)              # e.g., "Mylapore", "Tambaram", "Coimbatore North"
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("district_id", "name", name="uq_district_taluk"),
    )

    # Relationships
    district = relationship("District", back_populates="taluks")
    localities = relationship("Locality", back_populates="taluk", cascade="all, delete-orphan")


class Locality(Base):
    """City neighbourhood, village, or specific urban node."""
    __tablename__ = "localities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    taluk_id = Column(Integer, ForeignKey("taluks.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(128), nullable=False, index=True)              # e.g., "Anna Nagar", "Adyar", "Saravanampatti"
    postal_code = Column(String(16), nullable=True, index=True)
    tier = Column(String(32), default="TIER_1")                         # TIER_1 (Chennai core), TIER_2 (Coimbatore/Madurai), TIER_3 (Emerging/Rural)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("district_id", "name", name="uq_district_locality"),
    )

    # Relationships
    district = relationship("District", back_populates="localities")
    taluk = relationship("Taluk", back_populates="localities")
    properties = relationship("Property", back_populates="locality")
    price_observations = relationship("PriceObservation", back_populates="locality")
    indices = relationship("MarketIndex", back_populates="locality")
    predictions = relationship("Prediction", back_populates="locality")
    infrastructure = relationship("InfrastructureProject", back_populates="locality")


class PropertyType(Base):
    """Categorization of asset classes (Apartment, Land, Commercial)."""
    __tablename__ = "property_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False, index=True)  # RESIDENTIAL_APARTMENT, RESIDENTIAL_PLOT, etc.
    category = Column(String(64), nullable=False)                       # RESIDENTIAL, COMMERCIAL, LAND, AGRICULTURAL
    name = Column(String(128), nullable=False)
    unit_default = Column(String(32), default="SQFT")                   # SQFT, ACRE, GROUND, CENT
    description = Column(Text, nullable=True)

    # Relationships
    properties = relationship("Property", back_populates="property_type")
    price_observations = relationship("PriceObservation", back_populates="property_type")
    indices = relationship("MarketIndex", back_populates="property_type")
    predictions = relationship("Prediction", back_populates="property_type")


class Property(Base):
    """Individual real estate asset, development, or survey tract."""
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    locality_id = Column(Integer, ForeignKey("localities.id"), nullable=False, index=True)
    property_type_id = Column(Integer, ForeignKey("property_types.id"), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    address = Column(Text, nullable=True)
    rera_reg_number = Column(String(128), nullable=True, index=True)
    survey_number = Column(String(128), nullable=True)                  # Revenue survey number for TNREGINET alignment
    super_built_up_area = Column(Float, nullable=True)
    carpet_area = Column(Float, nullable=True)
    plot_area = Column(Float, nullable=True)
    area_unit = Column(String(32), default="SQFT")
    bedrooms = Column(Integer, nullable=True)
    floor_number = Column(Integer, nullable=True)
    total_floors = Column(Integer, nullable=True)
    age_years = Column(Float, nullable=True)
    furnishing_status = Column(String(64), nullable=True)               # UNFURNISHED, SEMI_FURNISHED, FULLY_FURNISHED
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    locality = relationship("Locality", back_populates="properties")
    property_type = relationship("PropertyType", back_populates="properties")
    price_observations = relationship("PriceObservation", back_populates="property")


class DataSource(Base):
    """Provenanced registry of data originators."""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False, index=True)  # TNREGINET, NHB_RESIDEX, RBI_DBIE, BIS, TNRERA
    name = Column(String(256), nullable=False)
    provider = Column(String(256), nullable=False)
    access_method = Column(String(256), nullable=False)
    url = Column(String(512), nullable=False)
    authentication_required = Column(Boolean, default=False)
    update_frequency = Column(String(64), default="Monthly")
    status = Column(String(32), default="ACTIVE")                       # ACTIVE, PAUSED, DEPRECATED
    license_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    price_observations = relationship("PriceObservation", back_populates="source")
    indices = relationship("MarketIndex", back_populates="source")
    ingestion_logs = relationship("IngestionLog", back_populates="source")


class PriceObservation(Base):
    """
    Core granular pricing evidence ledger.
    Strictly separates TRANSACTION, GUIDELINE, ASKING, RENTAL, BANK_ASSESSMENT, and MODEL_ESTIMATE.
    """
    __tablename__ = "price_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="SET NULL"), nullable=True, index=True)
    locality_id = Column(Integer, ForeignKey("localities.id"), nullable=False, index=True)
    property_type_id = Column(Integer, ForeignKey("property_types.id"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False, index=True)
    
    price_type = Column(String(32), nullable=False, index=True)         # TRANSACTION, GUIDELINE, ASKING, RENTAL, BANK_ASSESSMENT, MODEL_ESTIMATE
    amount = Column(Float, nullable=False)                              # Total aggregate transaction/guideline/asking value
    original_currency = Column(String(8), default="INR")
    
    area_value = Column(Float, nullable=False)                          # Area in original unit
    original_unit = Column(String(32), nullable=False)                  # SQFT, SQM, GROUND, CENT, ACRE
    
    price_per_sqft_inr = Column(Float, nullable=False, index=True)      # Primary normalized benchmark (INR / sq ft)
    price_per_sqm_inr = Column(Float, nullable=False)                   # Normalized metric benchmark (INR / sq m)
    
    observation_date = Column(Date, nullable=False, index=True)         # Date when transaction or guideline became effective
    publication_date = Column(Date, nullable=True)                      # Gazette or portal publication date
    verified = Column(Boolean, default=False)
    verification_status = Column(String(32), default="VERIFIED", index=True) # VERIFIED, UNVERIFIED, DERIVED, REJECTED
    data_quality_flags = Column(String(256), nullable=True)             # e.g., "OK", "OUTLIER_HIGH", "SUSPECT_UNIT"
    source_reference = Column(String(256), nullable=True)               # e.g. Gazette SRO Notification, RERA Doc #
    retrieval_date = Column(Date, nullable=True)                        # Date of ingestion / retrieval
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_price_loc_type_date", "locality_id", "price_type", "observation_date"),
    )

    # Relationships
    property = relationship("Property", back_populates="price_observations")
    locality = relationship("Locality", back_populates="price_observations")
    property_type = relationship("PropertyType", back_populates="price_observations")
    source = relationship("DataSource", back_populates="price_observations")


class MarketIndex(Base):
    """Aggregated longitudinal indices (NHB RESIDEX, City Hedonic HPI)."""
    __tablename__ = "market_indices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True, index=True)
    locality_id = Column(Integer, ForeignKey("localities.id"), nullable=True, index=True)
    property_type_id = Column(Integer, ForeignKey("property_types.id"), nullable=True)
    
    index_name = Column(String(128), nullable=False, index=True)        # e.g., "NHB_RESIDEX_CHENNAI", "COIMBATORE_COMPOSITE_HPI"
    base_period = Column(String(32), default="2017-18=100")
    period_date = Column(Date, nullable=False, index=True)              # Quarter or month ending
    index_value = Column(Float, nullable=False)
    yoy_growth_pct = Column(Float, nullable=True)
    qoq_growth_pct = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("index_name", "period_date", name="uq_index_period"),
    )

    # Relationships
    source = relationship("DataSource", back_populates="indices")
    district = relationship("District", back_populates="indices")
    locality = relationship("Locality", back_populates="indices")
    property_type = relationship("PropertyType", back_populates="indices")


class MacroIndicator(Base):
    """Indian and global economic and monetary factors influencing housing."""
    __tablename__ = "macro_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_code = Column(String(64), nullable=False, index=True)     # e.g., "RBI_REPO_RATE", "HOME_LOAN_WALR", "HOUSING_CREDIT_OUTSTANDING", "CPI_HOUSING"
    indicator_name = Column(String(256), nullable=False)
    provider = Column(String(128), nullable=False)                      # RBI, MoSPI, BIS
    frequency = Column(String(32), default="Monthly")                   # Daily, Monthly, Quarterly, Annual
    period_date = Column(Date, nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=False)                           # PERCENT, INR_CRORE, INDEX_POINTS
    publication_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("indicator_code", "period_date", name="uq_macro_indicator_period"),
    )


class InfrastructureProject(Base):
    """Highways, metro corridors, airports, and industrial zones driving land valuation."""
    __tablename__ = "infrastructure_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    locality_id = Column(Integer, ForeignKey("localities.id"), nullable=True, index=True)
    project_name = Column(String(256), nullable=False)                  # e.g., "Chennai Metro Phase 2 - Line 3/4/5", "Parandur Greenfield Airport"
    project_type = Column(String(64), nullable=False)                   # METRO, HIGHWAY, AIRPORT, IT_PARK, INDUSTRIAL_CORRIDOR
    status = Column(String(64), nullable=False)                         # ANNOUNCED, UNDER_CONSTRUCTION, OPERATIONAL
    expected_completion_year = Column(Integer, nullable=True)
    investment_inr_crores = Column(Float, nullable=True)
    impact_radius_km = Column(Float, default=5.0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    district = relationship("District", back_populates="infrastructure")
    locality = relationship("Locality", back_populates="infrastructure")


class Model(Base):
    """Machine learning forecasting model registration metadata."""
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_code = Column(String(64), unique=True, nullable=False, index=True)
    model_name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    target_variable = Column(String(64), default="price_per_sqft_inr")
    algorithm = Column(String(64), nullable=False)                      # e.g., "HEDONIC_REGRESSION", "SPATIAL_XGBOOST", "ARIMA_PANEL"
    hyperparams_json = Column(Text, nullable=True)
    training_start_date = Column(Date, nullable=True)
    training_end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    predictions = relationship("Prediction", back_populates="model")


class Prediction(Base):
    """Forward-looking real estate price projections by horizon."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, index=True)
    locality_id = Column(Integer, ForeignKey("localities.id"), nullable=False, index=True)
    property_type_id = Column(Integer, ForeignKey("property_types.id"), nullable=False, index=True)
    
    forecast_origin = Column(Date, nullable=False, index=True)
    horizon_months = Column(Integer, nullable=False)                    # 3, 6, 12, 24 months
    target_date = Column(Date, nullable=False, index=True)
    
    predicted_price_per_sqft = Column(Float, nullable=False)
    lower_bound_95 = Column(Float, nullable=False)
    upper_bound_95 = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    model = relationship("Model", back_populates="predictions")
    locality = relationship("Locality", back_populates="predictions")
    property_type = relationship("PropertyType", back_populates="predictions")


class IngestionLog(Base):
    """Audit log for automated and manual source ingestion runs."""
    __tablename__ = "ingestion_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    run_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    records_extracted = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    status = Column(String(32), default="SUCCESS")                       # SUCCESS, PARTIAL, FAILED
    error_details = Column(Text, nullable=True)

    # Relationships
    source = relationship("DataSource", back_populates="ingestion_logs")
