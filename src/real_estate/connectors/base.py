"""
Base class for Tamil Nadu Real Estate Data Source Connectors.
Provides standardized provenance tracking, validation, deduplication, and ingestion logging.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from src.real_estate.db.schema import DataSource, IngestionLog
from src.real_estate.validators.data_validator import RealEstateDataValidator


class BaseRealEstateConnector(ABC):
    """Abstract connector establishing provenance, extraction, validation, and audit trail."""

    def __init__(self, source_code: str):
        self.source_code = source_code

    def get_source_record(self, db: Session) -> DataSource:
        """Fetch the registered DataSource record."""
        source = db.query(DataSource).filter(DataSource.code == self.source_code).first()
        if not source:
            raise ValueError(f"DataSource '{self.source_code}' not found in registry. Ensure database is seeded.")
        return source

    @abstractmethod
    def fetch_raw_data(self) -> List[Dict[str, Any]]:
        """Extract raw records from official source extracts or APIs."""
        pass

    @abstractmethod
    def transform_records(self, raw_records: List[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
        """Normalize units, resolve foreign keys, and compute standard metrics."""
        pass

    def ingest(self, db: Session) -> Dict[str, Any]:
        """
        Orchestrates full ETL lifecycle:
        1. Fetch raw records.
        2. Transform and normalize.
        3. Validate against boundary checks and duplicates.
        4. Load into database.
        5. Record audit trail in ingestion_logs.
        """
        source = self.get_source_record(db)
        log = IngestionLog(
            source_id=source.id,
            run_timestamp=datetime.utcnow(),
            records_extracted=0,
            records_inserted=0,
            records_rejected=0,
            status="RUNNING"
        )
        db.add(log)
        db.commit()

        try:
            raw_records = self.fetch_raw_data()
            log.records_extracted = len(raw_records)

            transformed = self.transform_records(raw_records, db)
            
            inserted_count = 0
            rejected_count = 0
            error_details = []

            for record in transformed:
                # Validate record
                val_res = RealEstateDataValidator.validate_price_observation(
                    db=db,
                    locality_id=record["locality_id"],
                    property_type_id=record["property_type_id"],
                    source_id=source.id,
                    price_type=record["price_type"],
                    amount=record["amount"],
                    area_value=record["area_value"],
                    price_per_sqft_inr=record["price_per_sqft_inr"],
                    observation_date=record["observation_date"],
                    reject_duplicates=True
                )

                if val_res["is_valid"]:
                    db.add(record["model_instance"])
                    inserted_count += 1
                else:
                    rejected_count += 1
                    error_details.append(f"Record {record.get('id_desc')}: {', '.join(val_res['errors'])}")

            db.commit()

            log.records_inserted = inserted_count
            log.records_rejected = rejected_count
            log.status = "SUCCESS" if rejected_count == 0 else "PARTIAL"
            log.error_details = "\n".join(error_details[:20]) if error_details else None
            db.commit()

            return {
                "source": self.source_code,
                "status": log.status,
                "extracted": log.records_extracted,
                "inserted": log.records_inserted,
                "rejected": log.records_rejected,
                "log_id": log.id
            }

        except Exception as e:
            db.rollback()
            log.status = "FAILED"
            log.error_details = str(e)
            db.commit()
            raise e
