"""
Unit conversion engine for Tamil Nadu Real Estate Intelligence.
Supports standard Imperial (sq ft), Metric (sq m), and indigenous South Indian / Tamil units:
- Ground (2,400 sq ft)
- Cent (435.6 sq ft)
- Kuzhi (144 sq ft)
- Acre (43,560 sq ft / 100 cents / 18.15 grounds)
- Hectare (107,639.104 sq ft / 10,000 sq m)
"""

from typing import Dict, Any, Tuple
from src.real_estate.config import (
    SQFT_PER_SQM, SQFT_PER_CENT, SQFT_PER_GROUND,
    SQFT_PER_ACRE, SQFT_PER_HECTARE, SQFT_PER_KUZHI
)


class RealEstateUnitConverter:
    """Mathematical conversions for Tamil Nadu land and built property units."""

    AREA_TO_SQFT_FACTORS = {
        "SQFT": 1.0,
        "SQ_FT": 1.0,
        "SFT": 1.0,
        "SQM": SQFT_PER_SQM,
        "SQ_M": SQFT_PER_SQM,
        "SQ_METRE": SQFT_PER_SQM,
        "CENT": SQFT_PER_CENT,
        "CENTS": SQFT_PER_CENT,
        "GROUND": SQFT_PER_GROUND,
        "GROUNDS": SQFT_PER_GROUND,
        "ACRE": SQFT_PER_ACRE,
        "ACRES": SQFT_PER_ACRE,
        "HECTARE": SQFT_PER_HECTARE,
        "HECTARES": SQFT_PER_HECTARE,
        "KUZHI": SQFT_PER_KUZHI,
        "MAA": SQFT_PER_KUZHI * 100.0  # 1 Maa = 100 Kuzhi = 14,400 sq ft (~0.33 acre)
    }

    @classmethod
    def to_sqft(cls, area: float, unit: str) -> float:
        """Convert any area unit to square feet."""
        clean_unit = unit.strip().upper()
        if clean_unit not in cls.AREA_TO_SQFT_FACTORS:
            raise ValueError(f"Unsupported land unit '{unit}'. Supported: {list(cls.AREA_TO_SQFT_FACTORS.keys())}")
        return round(float(area) * cls.AREA_TO_SQFT_FACTORS[clean_unit], 4)

    @classmethod
    def to_sqm(cls, area: float, unit: str) -> float:
        """Convert any area unit to square metres."""
        sqft = cls.to_sqft(area, unit)
        return round(sqft / SQFT_PER_SQM, 4)

    @classmethod
    def to_cents(cls, area: float, unit: str) -> float:
        """Convert any area unit to cents."""
        sqft = cls.to_sqft(area, unit)
        return round(sqft / SQFT_PER_CENT, 4)

    @classmethod
    def to_grounds(cls, area: float, unit: str) -> float:
        """Convert any area unit to grounds."""
        sqft = cls.to_sqft(area, unit)
        return round(sqft / SQFT_PER_GROUND, 4)

    @classmethod
    def to_acres(cls, area: float, unit: str) -> float:
        """Convert any area unit to acres."""
        sqft = cls.to_sqft(area, unit)
        return round(sqft / SQFT_PER_ACRE, 4)

    @classmethod
    def normalize_price(
        cls,
        total_amount_inr: float,
        area_value: float,
        area_unit: str
    ) -> Tuple[float, float, Dict[str, float]]:
        """
        Calculates normalized metrics:
        - Price per sq ft (INR)
        - Price per sq m (INR)
        - Auxiliary regional breakdown (per ground, per cent, per acre)
        """
        if total_amount_inr <= 0:
            raise ValueError(f"Total amount must be positive, got {total_amount_inr}")
        if area_value <= 0:
            raise ValueError(f"Area must be positive, got {area_value}")

        total_sqft = cls.to_sqft(area_value, area_unit)
        price_per_sqft = round(total_amount_inr / total_sqft, 2)
        price_per_sqm = round(price_per_sqft * SQFT_PER_SQM, 2)

        auxiliary = {
            "price_per_cent_inr": round(price_per_sqft * SQFT_PER_CENT, 2),
            "price_per_ground_inr": round(price_per_sqft * SQFT_PER_GROUND, 2),
            "price_per_acre_inr": round(price_per_sqft * SQFT_PER_ACRE, 2),
            "total_sqft": total_sqft,
            "total_sqm": round(total_sqft / SQFT_PER_SQM, 2),
            "total_cents": round(total_sqft / SQFT_PER_CENT, 3),
            "total_grounds": round(total_sqft / SQFT_PER_GROUND, 3),
            "total_acres": round(total_sqft / SQFT_PER_ACRE, 4)
        }

        return price_per_sqft, price_per_sqm, auxiliary
