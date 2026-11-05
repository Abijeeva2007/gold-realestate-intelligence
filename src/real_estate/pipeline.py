"""
Master Ingestion Pipeline for Tamil Nadu Real Estate Intelligence Engine.
Executes ETL workflows across all 5 connectors with complete audit logging.
"""

from typing import Dict, Any, List
from src.real_estate.db.database import SessionLocal
from src.real_estate.connectors.tnreginet import TNREGINETConnector
from src.real_estate.connectors.nhb_residex import NHBResidexConnector
from src.real_estate.connectors.rbi_dbie import RBIDBIEConnector
from src.real_estate.connectors.bis import BISRealEstateConnector
from src.real_estate.connectors.tnrera import TNRERAConnector


def run_real_estate_ingestion_pipeline() -> List[Dict[str, Any]]:
    """Runs all 5 connectors and outputs a comprehensive execution report."""
    db = SessionLocal()
    results = []

    connectors = [
        TNREGINETConnector(),
        NHBResidexConnector(),
        RBIDBIEConnector(),
        BISRealEstateConnector(),
        TNRERAConnector()
    ]

    try:
        print("=== COMMENCING REAL ESTATE ETL INGESTION PIPELINE ===")
        for conn in connectors:
            print(f"Running connector: {conn.source_code}...")
            res = conn.ingest(db)
            results.append(res)
            print(f"  [{res['source']}] Extracted: {res['extracted']}, Inserted: {res['inserted']}, Rejected: {res['rejected']} -> Status: {res['status']}")

        print("=== REAL ESTATE ETL INGESTION COMPLETED ===")
        return results

    finally:
        db.close()


if __name__ == "__main__":
    run_real_estate_ingestion_pipeline()
