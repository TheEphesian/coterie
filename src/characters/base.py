"""Base character class with common functionality."""

from abc import ABC, abstractmethod
from typing import Any


class RaceCharacter(ABC):
    """Abstract base for all race-specific character types."""
    
    race_type: str = ""
    
    def __init__(self, character_data: dict[str, Any]):
        self.data = character_data
    
    @abstractmethod
    def get_trait_categories(self) -> list[str]:
        """Return list of trait categories for this race."""
        pass
    
    @abstractmethod
    def get_temper_fields(self) -> list[str]:
        """Return list of temper fields (willpower, blood, etc.)."""
        pass
    
    @abstractmethod
    def validate(self) -> list[str]:
        """Validate character data, return list of errors."""
        pass
