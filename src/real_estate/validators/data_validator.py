"""
Data validation and sanity checking engine for Tamil Nadu Real Estate Intelligence.
Enforces non-fabrication guarantees, strict price type segregation, duplicate prevention,
and physical plausibility boundaries.
"""

from datetime import date, datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from src.real_estate.config import PRICE_TYPES
from src.real_estate.db.schema import PriceObservation


class RealEstateDataValidator:
    """Rigorous validator for incoming real estate price points and records."""

    MIN_PRICE_PER_SQFT_BUILT = 50.0      # Minimum plausible urban built / plot rate
    MIN_PRICE_PER_SQFT_AGRI = 5.0        # Minimum plausible rural agricultural rate (~₹2L / acre)
    MAX_PRICE_PER_SQFT = 250000.0        # Maximum plausible prime commercial/luxury rate (e.g. Boat Club/Poes Garden)

    @classmethod
    def validate_price_observation(
        cls,
        db: Session,
        locality_id: int,
        property_type_id: int,
        source_id: int,
        price_type: str,
        amount: float,
        area_value: float,
        price_per_sqft_inr: float,
        observation_date: date,
        reject_duplicates: bool = True
    ) -> Dict[str, Any]:
        """
        Validates an incoming price observation record.
        Returns a dict with 'is_valid': bool and 'errors': List[str].
        """
        errors = []

        # 1. Price type validity & segregation
        clean_price_type = price_type.strip().upper()
        if clean_price_type not in PRICE_TYPES:
            errors.append(f"Invalid price_type '{price_type}'. Must be one of: {PRICE_TYPES}")

        # 2. Positive value bounds
        if amount <= 0:
            errors.append(f"Amount must be strictly positive, received {amount}")
        if area_value <= 0:
            errors.append(f"Area must be strictly positive, received {area_value}")

        # 3. Normalized rate sanity bounds
        min_floor = cls.MIN_PRICE_PER_SQFT_AGRI if price_per_sqft_inr < 50.0 else cls.MIN_PRICE_PER_SQFT_BUILT
        if price_per_sqft_inr < min_floor:
            errors.append(f"Price per sqft (₹{price_per_sqft_inr}) is below minimum plausible floor of ₹{min_floor}")
        if price_per_sqft_inr > cls.MAX_PRICE_PER_SQFT:
            errors.append(f"Price per sqft (₹{price_per_sqft_inr}) exceeds plausible ceiling of ₹{cls.MAX_PRICE_PER_SQFT}")

        # 4. Temporal causality (no lookahead / future-dated transactions)
        today = date.today()
        if observation_date > today:
            errors.append(f"Future observation date {observation_date} is prohibited. Current date: {today}")

        # 5. Duplicate detection
        if reject_duplicates and db is not None:
            duplicate = db.query(PriceObservation).filter(
                PriceObservation.locality_id == locality_id,
                PriceObservation.property_type_id == property_type_id,
                PriceObservation.source_id == source_id,
                PriceObservation.price_type == clean_price_type,
                PriceObservation.observation_date == observation_date,
                PriceObservation.amount == amount
            ).first()
            if duplicate:
                errors.append(f"Duplicate observation detected: already exists with ID {duplicate.id} on date {observation_date}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
