"""
Data Collectors Package.
Provides modules to collect gold prices, Indian spot bullion, and USD/INR exchange rates.
"""

from src.collectors.base_collector import BaseCollector
from src.collectors.comex_gold_collector import ComexGoldCollector
from src.collectors.fx_collector import FXCollector
from src.collectors.rbi_gold_collector import RbiGoldCollector
from src.collectors.world_bank_collector import WorldBankCollector

__all__ = [
    "BaseCollector",
    "ComexGoldCollector",
    "FXCollector",
    "RbiGoldCollector",
    "WorldBankCollector",
]
